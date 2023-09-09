import uuid
from botocore.exceptions import ClientError
from app import s3, profileImageS3Bucket
import requests, json, os

UPLOAD_FOLDER = 'temp_uploads'  # Temporary folder to store uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image formats

# Ensure the temporary upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_temp_image(image, filename):
    """
    Save image to a temporary location and return its path.
    """
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image.save(filepath)
    return filepath


def upload_profile_image(file, filename):
    try:
        s3_url = upload_to_s3(file, filename, profileImageS3Bucket)
        return s3_url
    except Exception as e:
        raise e

def upload_to_s3(file, filename, bucket_name):

    try:
        s3.upload_fileobj(file, bucket_name, filename)
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"
        return s3_url
    except ClientError as e:
        raise Exception("Failed to upload image to S3: " + str(e))

def download_profile_image(profile_image_key, bucket_name=profileImageS3Bucket):
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=profile_image_key)
        image_content = obj['Body'].read()
        return image_content
    except Exception as e:
        raise e

def download_from_s3(file_key, bucket_name):
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        file_content = obj['Body'].read()
        return file_content
    except Exception as e:
        raise e

def generate_presigned_url(file_key, bucket_name=profileImageS3Bucket, expiration=3600):
    """
    Generate a presigned URL to share an S3 object.

    :param file_key: The key of the file (i.e., filename) in the S3 bucket.
    :param bucket_name: Name of the S3 bucket.
    :param expiration: Time in seconds for which the URL is valid.
    :return: Presigned URL as a string.
    """

    try:
        response = s3.generate_presigned_url('get_object',
                                             Params={'Bucket': bucket_name, 'Key': file_key},
                                             ExpiresIn=expiration)
        return response
    except ClientError as e:
        raise Exception("Failed to generate presigned URL: " + str(e))

# Other functions remain the same

def send_images_to_process(user_id, image_process_url, profile_image_url, cloth_image_url):
    url = image_process_url  # replace with your actual Flask server URL
    data = {
        'user_id': user_id,
        'profile_image_url': profile_image_url,
        'cloth_image_url': cloth_image_url,
        'image_id': uuid.uuid4()
    }
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        print("Images sent successfully.")
        return response.json()["final_image_s3_url"]
    else:
        print(f"Failed to process the images. Status code: {response.status_code}")
        return None