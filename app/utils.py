import uuid
from botocore.exceptions import ClientError
from app import s3, profileImageS3Bucket
import requests, json, os
from rembg import remove
from PIL import Image
import io

UPLOAD_FOLDER = 'temp_uploads'  # Temporary folder to store uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image formats

# Ensure the temporary upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
def remove_background_from_cv2_image(cv2_image):
    # Convert OpenCV image (numpy array) to PIL Image
    pil_image = Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

    # Remove background using rembg
    output_image = remove(pil_image)

    # Convert the PIL image back to OpenCV format (numpy array)
    output_image = Image.open(io.BytesIO(output_image))
    output_cv2_image = cv2.cvtColor(np.array(output_image), cv2.COLOR_RGB2BGR)

    return output_cv2_image
    
def remove_background_from_image(image_file):
    try:
        # open the image file
        input_image = Image.open(image_file)

        # remove the background
        output_image = remove(input_image)

        # save the output image to a bytesio object to avoid saving it to disk
        output_io = io.BytesIO()
        output_image.save(output_io, format='PNG')
        output_io.seek(0)
        return output_io

    except Exception as e:
        print(f"error while removing background: {e}")
        raise

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_temp_image(image, filename):
    """
    Save image to a temporary location and return its path.
    """
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    image.save(filepath)
    return filepath

def upload_profile_image_bytes(file_bytes, filename):
    """
    Uploads a profile image to an S3 bucket using an in-memory bytes object.
    
    Parameters:
    - file_bytes: A BytesIO object containing the file's data.
    - filename: The name to assign to the file in the S3 bucket.
    
    Returns:
    - s3_url: The URL of the uploaded file in the S3 bucket.
    """
    try:
        # Check if file_bytes is a BytesIO object
        if not isinstance(file_bytes, io.BytesIO):
            raise ValueError("Input must be a BytesIO object")

        # Seek to the beginning of the BytesIO stream
        file_bytes.seek(0)

        # Upload the file to S3 using boto3
        s3_url = upload_to_s3(file_bytes, filename, profileImageS3Bucket)
        return s3_url
    except Exception as e:
        raise e

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

def send_images_to_process(user_id, cloth_id, image_process_url, profile_image_url, cloth_image_url):
    data = {
        'user_id': user_id,
        'cloth_id': cloth_id,
        'profile_image_url': profile_image_url,
        'cloth_image_url': cloth_image_url,
        'image_id': str(uuid.uuid4())
    }
    headers = {'Content-Type': 'application/json'}

    response = requests.post(image_process_url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        print("Images sent successfully.")
        return response.json()["final_image_s3_presigned_url"]
    else:
        print(f"Failed to process the images. Status code: {response.status_code}")
        return None