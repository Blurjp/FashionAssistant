from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Cloth
from app import db, google, s3, image_processing_service_url, profileImageS3Bucket, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from uuid import uuid4
from .utils import upload_profile_image, send_images_to_process, generate_presigned_url, allowed_file, remove_background_from_image, upload_profile_image_bytes
import traceback
import os, requests, uuid

routes = Blueprint('routes', __name__)

@routes.route('/get-google-client-id', methods=['GET'])
def get_google_client_id():
    """
    Flask route to return the Google Client ID from the server configuration.
    """
    google_client_id = current_app.config['GOOGLE_CLIENT_ID']
    return jsonify({"google_client_id": google_client_id})

@routes.route('/verify-token', methods=['POST'])
def verify_google_token():
    try:
        print('verify_google_token')
        # Get the token from the frontend
        token = request.json.get('token')

        # Verify the token with Google's OAuth2 API
        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        response = requests.get(url)

        if response.status_code != 200:
            return jsonify({"success": False, "message": "Failed to verify token"}), 400

        # Parse the response from Google
        profile = response.json()

        # Get email from the profile
        email = profile['email']
        name = profile.get('name', '')

        # Check if the user exists in the database
        user = User.query.filter_by(email=email).first()

        if not user:
            # Create a new user if they don't exist
            user_id = str(uuid4())  # Generate unique UUID
            user = User(id=user_id, name=name, email=email, password=None)  # No password for Google OAuth users
            db.session.add(user)
            db.session.commit()

        # Log in the user
        login_user(user)

        # Send a success response with the redirect URL
        return jsonify({"success": True, "message": "Logged in successfully", "redirect_url": url_for('routes.show_clothes')})

    except Exception as e:
        print(f"Error verifying Google token: {e}")
        return jsonify({"success": False, "message": "Error verifying token"}), 500


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get JSON data
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({'message': 'The email you entered does not exist in our system.', 'success': False})

        if not user.check_password(password):
            return jsonify({'message': 'Invalid password', 'success': False}), 401

        # Create a unique session ID using UUID4
        session_id = str(uuid4())
        session['user_id'] = session_id
        user.session_id = session_id
        db.session.commit()

        # Log in the user
        login_user(user)

        return jsonify({'message': 'Logged in successfully', 'success': True, 'redirect_url': url_for('routes.show_clothes')})

    return render_template('login.html')

@routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get JSON data
        data = request.get_json()
        name = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'An account with that email already exists.', 'success': False}), 400

        # Create new user
        user_id = str(uuid4())  # Generate unique user ID
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(id=user_id, name=name, email=email, password=hashed_password)

        # Add user to the database
        db.session.add(new_user)
        db.session.commit()

        # Log in the user
        login_user(new_user)

        return jsonify({'message': 'Account created successfully', 'success': True})

    return render_template('signup.html')

@routes.route('/process_images', methods=['POST'])
@login_required
def process_images():
    data = request.json
    user_id = current_user.id
    profile_image_url = generate_presigned_url(current_user.profile_picture)
    cloth_image_link = data['cloth_image_link']
    cloth_id = data['cloth_id']

    final_image_url = send_images_to_process(user_id, cloth_id, image_processing_service_url, profile_image_url, cloth_image_link)

    if final_image_url:
        return jsonify({"status": "success", "final_image_url": final_image_url}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to process the images."}), 500

@routes.route('/google_login')
def google_login():
    print('in google login')
    redirect_uri = url_for('routes.google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@routes.route('/google_authorize')
def google_authorize():
    # Exchange the authorization code for a token
    token = google.authorize_access_token()
    
    # Fetch user information from Google's userinfo endpoint
    resp = google.get('https://www.googleapis.com/oauth2/v3/userinfo')  # Use full URL
    
    # Parse the response
    user_info = resp.json()

    # Handle the user info and log in the user
    email = user_info['email']
    name = user_info.get('name', '')

    # Check if user exists in the database
    user = User.query.filter_by(email=email).first()

    if not user:
        # Create a new user if they don't exist
        user_id = str(uuid4())  # Generate unique UUID
        user = User(id=user_id, name=name, email=email, password=None)  # No password for OAuth users
        db.session.add(user)
        db.session.commit()

    # Log the user in
    login_user(user)

    return redirect(url_for('routes.show_clothes'))



@routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

@routes.route('/')
def index():
    hasUploadedProfileImage = None
    if current_user.is_authenticated:
        hasUploadedProfileImage = current_user.profile_picture

    return render_template('index2.html', is_authenticated=current_user.is_authenticated, user=current_user, hasUploadedProfileImage=hasUploadedProfileImage)

@routes.route('/upload_portrait', methods=['POST'])
@login_required
def upload_portrait():
    try:
        portrait_file = request.files.get('profile-image')
        if not portrait_file or not allowed_file(portrait_file.filename):
            return jsonify({"error": "Invalid or no file selected"}), 400

        output_io = remove_background_from_image(portrait_file)

        # Secure and make filename unique
        filename = secure_filename(f"{current_user.id}_{uuid.uuid4().hex}_{portrait_file.filename}")

        # Upload the portrait file to S3
        #upload_profile_image(portrait_file, filename)
        upload_profile_image_bytes(output_io, filename)

        # Store the file key in the database
        current_user.profile_picture = filename
        db.session.commit()

        # Generate a pre-signed URL for the uploaded image
        presigned_url = generate_presigned_url(filename)

        return jsonify({"message": "Profile image uploaded successfully", "image_url": presigned_url}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@routes.route('/get-presigned-url', methods=['GET'])
@login_required
def get_profile_image_presigned_url():
    try:
        s3_key = current_user.profile_picture
        if not s3_key:
            return jsonify({"error": "No profile picture uploaded"}), 400

        presigned_url = generate_presigned_url(s3_key)
        if presigned_url:
            return jsonify(success=True, presigned_url=presigned_url)
        else:
            return jsonify(success=False, message="Failed to generate pre-signed URL"), 500

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500

@routes.route('/clothes')
def show_clothes():
    # Query the Cloth table to retrieve all clothes
    clothes = Cloth.query.all()

    # Prepare the data to be passed to the template
    clothes_data = []
    for cloth in clothes:
        images = cloth.Images.split(',')
        try_on_link = images[0] if images else None  # Use the first image as the TryOnLink

        clothes_data.append({
            'ClothesID': cloth.id,
            'ProductName': cloth.ProductName,
            'Brand': cloth.Brand,
            'Price': cloth.Price,
            'Images': cloth.Images.split(','),
            'Sizes': cloth.Sizes,
            'Description': cloth.Description,
            'TryOnLink': try_on_link
        })

    return render_template('index2.html', clothes=clothes_data)
