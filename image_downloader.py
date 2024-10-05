import pandas as pd
import requests
import os
import hashlib
import chardet  # Import chardet to detect file encoding

def download_image(url, folder, file_name):
    """Download an image from a URL using requests and save it to a specified folder with a specific filename."""
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    # User agent string to mimic a real web browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
    }

    # Make the GET request with custom headers
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        file_path = os.path.join(folder, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Image downloaded and saved in {file_path}")
    else:
        print(f"Failed to download the image from {url} - HTTP Status: {response.status_code}")

def generate_filename(description):
    """Generate a unique filename using a hash of the description."""
    hash_object = hashlib.sha256(description.encode())
    return hash_object.hexdigest() + '.jpg'  # append .jpg to make the filename clear

def detect_encoding(file_path):
    """Detect the encoding of a file using chardet."""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        print(f"Detected encoding: {result['encoding']}")  # Print detected encoding
    return result['encoding']

def process_csv(file_path):
    """Process a CSV file to download images based on their URLs in specified fields."""
    encoding = detect_encoding(file_path)  # Determine the encoding of the file
    try:
        # Read CSV with the detected encoding
        data = pd.read_csv(file_path, encoding=encoding)
        #data = pd.read_csv(file_path, delimiter='\t', encoding=encoding, on_bad_lines='skip')
        data.columns = ['ProductName', 'Brand', 'Price', 'Sizes', 'Images', 'Description']
        for _, row in data.iterrows():
            print(row)
            urls = str(row['Images']).split(',')
            description = str(row['Description'])
            if len(urls) >= 2:
                file_name = generate_filename(description)
                download_image(urls[0], 'cloth', file_name)  # File extension is already added in generate_filename
                download_image(urls[1], 'image', file_name)
    except pd.errors.ParserError as e:
        print(f"Error reading CSV: {e}")

def find_description_from_hash(target_hash, possible_descriptions):
    """Find the original description by comparing the hash to possible descriptions."""
    for description in possible_descriptions:
        if hashlib.sha256(description.encode()).hexdigest() == target_hash:
            return description
    return None  # If no match is found

if __name__ == "__main__":
    csv_file_path = 'net-a-porter.csv'  # Ensure the correct path to your CSV file

    process_csv(csv_file_path)
