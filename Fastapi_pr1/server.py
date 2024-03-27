from io import BytesIO

from fastapi import FastAPI, UploadFile, File, Form
from PIL import Image
import os

app = FastAPI()

async def work_with_img(file1, file2, image_name, image_name_2):
    # Сохраняем полученные изображения на диск
    image1_bytes = await file1.read()
    output_folder = "images_left"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, image_name)
    with open(output_path, "wb") as file:
        file.write(image1_bytes)
    # Сохраняем полученные изображения на диск
    image2_bytes = await file2.read()
    output_folder = "images_right"
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, image_name_2)
    with open(output_path, "wb") as file:
        file.write(image2_bytes)

@app.post("/receive_images/")
async def receive_images(file1: UploadFile = File(...), file2: UploadFile = File(...), image_name: str = Form(...), image_name_2: str = Form(...)):
    try:
        await work_with_img(file1, file2, image_name, image_name_2)
        #print(f"{image_name} and {image_name_2}")
        return f"{image_name} и {image_name_2} приняты "
    except Exception as e:
        return {"message": f"Error receiving and processing images: {str(e)}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="localhost", port=8011, reload=True)
