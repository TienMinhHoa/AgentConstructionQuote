from langchain.tools import tool
import base64
import httpx
import fitz
from PIL import Image
import io
from typing import Annotated


async def encode_pdf_from_url(pdf_url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(pdf_url)
            response.raise_for_status()
            pdf_data = response.content
            pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
            page = pdf_document.load_page(0)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            buffer = io.BytesIO()
            img.save(buffer, format="PNG")

        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        print(f"Error loading image: {e}\n")
        return None


async def encode_image_from_url(url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            image_data = response.content
            return base64.b64encode(image_data).decode("utf-8")
    except Exception as e:
        print(f"Error loading image: {e}\n")
        return None


@tool
async def handdle_links(
    url: Annotated[str, "The url links to the resource that \
                            Agent need to handdle"]
):
    """
    This tool is designed for agent to download resource from internet.
    """

    if ".jpg" in url:
        base64_image = await encode_image_from_url(url)
    elif "pdf" in url:
        base64_image = await encode_pdf_from_url(url)

    return base64_image
