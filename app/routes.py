from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app.chat import send_message_to_chatgpt, extract_items_from_response, perform_google_search
from authlib.integrations.flask_client import OAuth
from app.models import User
from app import login_manager, db, image_processing_service_url
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from uuid import uuid4
from .utils import upload_profile_image, send_images_to_process, download_profile_image, download_from_s3, save_temp_image, allowed_file, generate_presigned_url
import base64
import traceback
import os, uuid

routes = Blueprint('routes', __name__)
oauth = OAuth()
google = None
microsoft = None
presigned_url = None

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
    #return render_template('login.html')

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
    hasUploadedProfileImage = None
    if current_user and current_user.is_authenticated:
        hasUploadedProfileImage = current_user.profile_picture
    #presigned_url = generate_presigned_url(current_user.profile_picture)
    #return render_template('index2.html', is_authenticated=current_user.is_authenticated, user=current_user, profile_image_url=presigned_url)
    return render_template('index2.html', is_authenticated=current_user.is_authenticated, user=current_user, profile_image_url= presigned_url, hasUploadedProfileImage=hasUploadedProfileImage)

# @routes.route('/profile', methods=['GET', 'POST'])
# @login_required
# def profile():
#     if current_user.profile_picture:
#         profile_image_key = current_user.profile_picture.split("/")[-1]
#     if profile_image_key:
#         profile_image_content = download_profile_image(profile_image_key)
#         profile_image_url = f"data:image/jpeg;base64,{base64.b64encode(profile_image_content).decode('utf-8')}"
#     else:
#         profile_image_url = None
#
#     return render_template('index2.html', is_authenticated=True, profile_image_url=profile_image_url)


# @routes.route('/login', methods=['GET'])
# def login_modal():
#     print("try to render_template login")
#     return render_template('login.html')
#
#
# @routes.route('/signup', methods=['GET'])
# def signup_modal():
#     print("try to render_template signup")
#     return render_template('signup.html')

# @routes.route('/profile')
# @login_required
# def profile():
#     return render_template('profile.html', user=current_user)

@routes.route('/upload_portrait', methods=['POST'])
def upload_portrait():
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "User not authenticated"}), 401

        portrait_file = request.files.get('profile-image')

        if not portrait_file or portrait_file.filename == '' or not allowed_file(portrait_file.filename):
            return jsonify({"error": "Invalid or no file selected"}), 400

        # Secure and make filename unique
        filename = secure_filename(f"{current_user.id}_{uuid.uuid4().hex}_{portrait_file.filename}")

        # Upload the portrait file to S3 directly
        upload_profile_image(portrait_file, filename)  # make sure your upload_profile_image function can handle file objects

        # Store the file key (filename) in the database instead of the full S3 URL
        current_user.profile_picture = filename
        db.session.commit()

        # Generate a pre-signed URL for the uploaded image
        presigned_url = generate_presigned_url(filename)

        return jsonify({
            "message": "Profile image uploaded successfully",
            "image_url": presigned_url
        }), 200

    except Exception as e:
        print('error uploading profile')
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@routes.route('/get-presigned-url', methods=['GET'])
def get_profile_image_presigned_url():
    try:
        if not current_user.is_authenticated:
            return jsonify({"error": "User not authenticated"}), 401

        # Get the S3 key from the database
        s3_key = current_user.profile_picture

        if not s3_key:
            return jsonify({"error": "No profile picture uploaded"}), 400

        # You can store the key in the user's session, database, etc.
        # For now, I'm assuming you know the key (filename) of the user's profile image
        presigned_url = generate_presigned_url(current_user.profile_picture)
        print(presigned_url);
        if presigned_url:
            return jsonify(success=True, presigned_url=presigned_url)
        else:
            return jsonify(success=False, message="Failed to generate pre-signed URL"), 500

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500





