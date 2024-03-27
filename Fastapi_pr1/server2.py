from fastapi import FastAPI, UploadFile, File, Form
from PIL import Image
import os
import uvicorn

app = FastAPI()


@app.post("/receive_images/")
async def receive_images(file1: UploadFile = File(...)):
    try:
        image1 = Image.open(file1.file)
        output_folder = "merged_images"
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, file1.filename)
        image1.save(output_path, format="PNG")

        return {"message": f"Изображение {file1.filename} успешно."}
    except Exception as e:
        return {"message": f"Error receiving and processing images: {str(e)}"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8011)
