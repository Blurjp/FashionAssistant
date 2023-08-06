from transformers import AutoModelForSequenceClassification, AutoTokenizer
from PIL import Image
from io import BytesIO
import torch
import base64
import matplotlib.pyplot as plt
from diffusers import StableDiffusionInpaintPipeline

# Download the model and tokenizer
model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
device = "cuda" if torch.cuda.is_available() else "cpu"



# display PIL images as grid
def display_images(images=None, columns=3, width=100, height=100):
    plt.figure(figsize=(width, height))
    for i, image in enumerate(images):
        plt.subplot(int(len(images) / columns + 1), columns, i + 1)
        plt.axis('off')
        plt.imshow(image)

# Display images in a row/col grid
def image_grid(imgs, rows, cols):
    assert len(imgs) == rows*cols
    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols*w, rows*h))
    grid_w, grid_h = grid.size

    for i, img in enumerate(imgs):
        grid.paste(img, box=(i%cols*w, i//cols*h))
    return grid

# Encoder to convert an image to json string
def encode_base64(input_image_filename):
    image = Image.open(input_image_filename).convert("RGB")
    #with open(file_name, "rb") as image:
    image_string = base64.b64encode(bytearray(image.read())).decode()
    return image_string

# Decode to to convert a json str to an image
def decode_base64_image(base64_string):
    decoded_string = BytesIO(base64.b64decode(base64_string))
    img = Image.open(decoded_string)
    return img


pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-inpainting",
    #torch_dtype=torch.float16,
)
pipe.to(device)
#pipe.enable_xformers_memory_efficient_attention()

num_images_per_prompt = 3
#prompt = "A female super-model poses in a casual long vacation skirt, with full body length, bright colors, photorealistic, high quality, highly detailed, elegant, sharp focus"
prompt = "A male model poses in a casual long vacation skirt, dark colors, photorealistic, high quality, highly detailed, elegant, sharp focus"

# Convert image to string
input_image_filename = "skirt-model-2.jpg"
mask_image_filename = "the_mask_image.png"
#encoded_input_image = encode_base64(input_image_filename)
#encoded_mask_image = encode_base64("the_mask_image.jpg")


# Set in-painting parameters
guidance_scale = 6.7
num_inference_steps = 45

input_image = Image.open(input_image_filename)
mask_image = Image.open(mask_image_filename)

image = pipe(prompt=prompt, image=input_image, mask_image=mask_image).images[0]
image.save("./yellow_cat_on_park_bench.png")

# for index, image in enumerate(pipe(prompt=prompt, image=input_image, mask_image=mask_image).images):
#     image.save("./yellow_cat_on_park_bench" + str(index) + ".png")

# run prediction
# response = predictor.predict(data={
#     "inputs": prompt,
#     "input_img": encoded_input_image,
#     "mask_img": encoded_mask_image,
#     "num_images_per_prompt" : num_images_per_prompt,
#     "image_length": 768
# }
# )
#
# # decode images
# decoded_images = [decode_base64_image(image) for image in response["generated_images"]]
#
# # visualize generation
# display_images(decoded_images, columns=num_images_per_prompt, width=100, height=100)
#
# # insert initial image in the list so we can compare side by side
# decoded_images.insert(0, image)
#
# # Display inpainting images in grid
# image_grid(decoded_images, 1, num_images_per_prompt + 1)
