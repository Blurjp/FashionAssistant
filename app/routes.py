from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app.chat import send_message_to_chatgpt, extract_items_from_response, perform_google_search
from authlib.integrations.flask_client import OAuth
from app.models import User
from app import login_manager, db, s3, profileImageS3Bucket
from werkzeug.security import check_password_hash, generate_password_hash
from uuid import uuid4
from botocore.exceptions import ClientError
import requests
import json


IMAGE_PROCESSING_SERVICE_URL = "http://your-image-processing-service/api/process_image"

routes = Blueprint('routes', __name__)
oauth = OAuth()
google = None
microsoft = None


def init_app(app):
    global google, microsoft
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'
    oauth.init_app(app)

    google = oauth.register(
        name='google',
        # Add your Google client ID and secret here
    )

    # microsoft = oauth.register(
    #     name='microsoft',
    #     # Add your Microsoft client ID and secret here
    # )

#extra_ask = "And please give me back a list of recommended items in python list based on your response content."

@routes.route("/process_chat", methods=["POST"])
def process_chat():
    message = request.json.get("message", "")
    chatgpt_response = send_message_to_chatgpt(message)

    # Extract keywords from ChatGPT response
    items = extract_items_from_response(chatgpt_response)
    #keywords = extract_keywords_from_response(chatgpt_response)
    search_results = []  # Define the variable with a default value
    try:
        # Perform a Google search using extracted keywords (You can replace this with your search logic)
        search_results = perform_google_search(items)
    except Exception as e:
        print(f"Error performing Google search: {str(e)}")

    return jsonify({
        "chatgpt_response": chatgpt_response,
        "search_results": search_results
    })

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get JSON data
        data = request.get_json()
        # Get form data
        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'The email you entered does not exist in our system.', 'success': False})
        if not user.check_password(password):
            # return a JSON response with a message and success status
            print("Invalid password")
            return jsonify({'message': 'Invalid password', 'success': False}), 401
        # create a unique session ID using UUID4
        session_id = str(uuid4())
        # store the session ID in the session cookie
        session['user_id'] = session_id
        # add the session ID to the user's record in the database
        user.session_id = session_id
        db.session.commit()

        # Log in user
        login_user(user)

        # return a JSON response with a success status
        return jsonify({'message': 'Logged in successfully', 'success': True})
    return render_template('login.html')

@routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get JSON data
        data = request.get_json()
        # Get form data
        name = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Generate unique id
        user_id = str(uuid4())

        # Create hashed password
        hashed_password = generate_password_hash(password, method='sha256')

        # print("my password_hash", hashed_password)
        # print("my login pass", password)
        # if check_password_hash(hashed_password, password):
        #     print("check_password_hash true")
        # else:
        #     print("check_password_hash false")

        print("Check if email already exists")
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print("email already exists")
            # Return a JSON response with a message and success status
            return jsonify({'message': 'An account with that email already exists.', 'success': False}), 400

        print("Create new user")
        # Create new user
        new_user = User(id=user_id, name=name, email=email, password=hashed_password)

        # Add new user to database
        db.session.add(new_user)
        db.session.commit()
        print("add user to db successfully")

        # Log in user
        login_user(new_user)

        # Return a JSON response with a success status
        return jsonify({'message': 'Account created successfully', 'success': True})

    return render_template('signup.html')


@routes.route('/login/google')
def login_google():
    # Add the Google login logic here
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

# @app.route('/login/microsoft')
# def login_microsoft():
# Add the Microsoft login logic here

@routes.route('/authorize/google')
def authorize_google():
    token = google.authorize_access_token()
    resp = google.get('https://www.googleapis.com/oauth2/v2/userinfo')
    profile = resp.json()

    # Check if the user exists in the database
    user = User.query.filter_by(email=profile['email']).first()

    # Create the user if they don't exist
    if user is None:
        user = User()
        user.email = profile['email']
        user.name = profile['name']
        db.session.add(user)
        db.session.commit()

    # Log in the user
    login_user(user)

    return redirect(url_for('routes.index'))

# @app.route('/authorize/microsoft')
# def authorize_microsoft():
# Add the Microsoft authorization logic here

@routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.index'))


@routes.route('/')
def index():
    return render_template('index2.html', is_authenticated=current_user.is_authenticated)

@routes.route('/login', methods=['GET'])
def login_modal():
    print("try to render_template login")
    return render_template('login.html')


@routes.route('/signup', methods=['GET'])
def signup_modal():
    print("try to render_template signup")
    return render_template('signup.html')

@routes.route('/upload_portrait', methods=['POST'])
def upload_portrait():

    if not current_user.is_authenticated:
        return jsonify({"error": "User not authenticated"}), 401

    if 'portrait' not in request.files:
        return jsonify({"error": "No file selected"}), 400

    portrait_file = request.files['portrait']

    if portrait_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Generate a unique filename for the uploaded image
    filename = f"{current_user.id}_{portrait_file.filename}"
    print('inside upload:', profileImageS3Bucket)

    cloth_image_url = 'https://www.net-a-porter.com/variants/images/1647597286238983/in/w1365_q80.jpg'

    try:
        # Upload the portrait file to S3
        s3.upload_fileobj(portrait_file, profileImageS3Bucket, filename)

        # Get the URL of the uploaded image
        s3_url = f"https://{profileImageS3Bucket}.s3.amazonaws.com/{filename}"

        # Store the profile image URL in the database
        current_user.profile_picture = s3_url
        db.session.commit()

        send_images_to_process(current_user.id, s3_url, cloth_image_url)

        return jsonify({"message": "Profile image uploaded successfully", "image_url": s3_url}), 200

    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("User already exists")
        else:
            print("Unexpected error: %s" % e)
        return jsonify({"error": "Failed to upload image to S3"}), 500

def send_images_to_process(user_id, profile_image_url, cloth_image_url):
    url = "http://localhost:5000/acceptImages"  # replace with your actual Flask server URL
    data = {
        'user_id': user_id,
        'profile_image_url': profile_image_url,
        'cloth_image_url': cloth_image_url
    }
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        print("Images sent successfully.")
        return response.json()["final_image_s3_url"]
    else:
        print(f"Failed to send images. Status code: {response.status_code}")
        return None

