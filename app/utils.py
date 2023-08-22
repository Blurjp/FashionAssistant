import uuid
from botocore.exceptions import ClientError
from app import s3, profileImageS3Bucket
import requests, json

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