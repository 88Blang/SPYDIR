from PIL import Image as PILImage
import requests
from io import BytesIO
from urllib.request import urlopen
import io
from colorthief import ColorThief


def get_img(image_path):
    """
    Given path (url or local file), returns img buffer
    """

    if image_path.startswith("http://") or image_path.startswith("https://"):
        response = requests.get(image_path)
        response.raise_for_status()
        img = PILImage.open(BytesIO(response.content))
    else:
        img = PILImage.open(image_path)
    return img


def rgb_to_hex(rgb: tuple) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def get_img_color(image_path: str) -> str:
    """Gets brand color

    Args:
        image_path (str): URL for image
    Returns:
        str: Hex color of image
    """
    fd = urlopen(image_path)
    f = io.BytesIO(fd.read())
    color_thief = ColorThief(f)
    color = color_thief.get_color(quality=1)
    return rgb_to_hex(color)
