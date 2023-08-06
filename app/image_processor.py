from model.clipseg import CLIPDensePredT
import torch
from torchvision import transforms
from PIL import Image
import requests
from io import BytesIO
import matplotlib.pyplot as plt

def download_image(img_url):
    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content))
    return img

device = "cuda" if torch.cuda.is_available() else "cpu"
# Add your image URL here
img_url = "https://assets.burberry.com/is/image/Burberryltd/6716B279-A570-49E4-9E46-0EA71607239F?$BBY_V2_ML_1x1$&wid=3000&hei=3000"

# The original image
image = download_image(img_url).resize((768, 768))

# Load CLIP model. Available models = ['RN50', 'RN101', 'RN50x4',
# 'RN50x16', 'RN50x64', 'ViT-B/32', 'ViT-B/16', 'ViT-L/14', 'ViT-L/14@336px']
model = CLIPDensePredT(version='ViT-B/16', reduce_dim=64)
model.eval()

# non-strict, because we only stored decoder weights (not CLIP weights)
model.load_state_dict(torch.load('weights/rd64-uni.pth', map_location=torch.device(device)), strict=False)


# Image normalization and resizing
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    transforms.Resize((768, 768)),
])
img = transform(image).unsqueeze(0)

# Text prompt
prompt = 'Get the suit only.'

# predict
mask_image_filename = 'the_mask_image.png'
with torch.no_grad():
    preds = model(img.repeat(4,1,1,1), prompt)[0]

# save the mask image after computing the area under the standard
#   Gaussian probability density function and calculates the cumulative
#   distribution function of the normal distribution with ndtr.
plt.imsave(mask_image_filename,torch.special.ndtr(preds[0][0]))