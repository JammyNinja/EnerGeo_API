import uuid
from pathlib import Path

import requests
from decouple import config
from langchain.tools import tool
from openai import OpenAI
from pydantic import BaseModel, Field

IMAGE_DIRECTORY = Path(__file__).parent.parent / "images"
CLIENT = OpenAI(api_key=str(config("OPENAI_API_KEY")))

def image_downloader(image_url: str | None) -> str:
    if image_url is None:
        return "No image URL returned from API."
    response = requests.get(image_url)
    if response.status_code != 200:
        return "Could not download image from URL."
    unique_id: uuid.UUID = uuid.uuid4()
    image_path = IMAGE_DIRECTORY / f"{unique_id}.png"
    print("image generator path", image_path)
    with open(image_path, "wb") as file:
        file.write(response.content)
    return str(image_path)

class GenerateImageInput(BaseModel):
    image_description: str = Field(
        description="A detailed description of the desired image." #An image of the weather conditions in the desired location.
    )


#original
# @tool("generate_image", args_schema=GenerateImageInput)
# def generate_image(image_description: str) -> str:
#     """Generate an image based on a detailed description."""
#     response = CLIENT.images.generate(
#         model="dall-e-3",
#         prompt=image_description,
#         size="1024x1024",
#         quality="standard",  # standard or hd
#         n=1,
#     )
#     image_url = response.data[0].url
#     print(image_url)
#     # return image_downloader(image_url)
#     return image_url

#trying to return image path and url
@tool("generate_image", args_schema=GenerateImageInput)
def generate_image(image_description: str) -> str:
    """Generate a dictionary that contains both the url and the path of a
        generated image based on a detailed description.
    """
    response = CLIENT.images.generate(
        model="dall-e-3",
        prompt=image_description,
        size="1024x1024",
        quality="standard",  # standard or hd
        n=1,
    )
    image_url = response.data[0].url

    print(image_url)
    image_path = image_downloader(image_url)
    print(image_path)

    return {
        "image_url" : image_url,
        "image_path": image_path
    }



#tool attempt
# @tool("get_image_url", args_schema=GenerateImageInput)
# def get_image_url(image_description: str) -> str:
#     """ Get the url of a generated image """
#     response = CLIENT.images.generate(
#         model="dall-e-3",
#         prompt=image_description,
#         size="1024x1024",
#         quality="standard",  # standard or hd
#         n=1,
#     )
#     image_url = response.data[0].url
#     return image_url


if __name__ == "__main__":
    print(generate_image.run("A picture of sharks eating pizza in space."))
