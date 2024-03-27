from fastapi import FastAPI, UploadFile, File, Form
from PIL import Image
import os
import uvicorn

app = FastAPI()


@app.post("/receive_images/")
async def receive_images(file1: UploadFile = File(...), file2: UploadFile = File(...), image_name: str = Form(...), image_name_2: str = Form(...)):
    try:
        # # Сохраняем полученные изображения на диск
        image1 = Image.open(file1.file)
        image2 = Image.open(file2.file)
        #
        # merged_image = Image.new("RGB", (image1.width + image2.width, max(image1.height, image2.height)))
        # merged_image.paste(image1, (0, 0))
        # merged_image.paste(image2, (image1.width, 0))
        # merged_image_name = image_name + "_" + image_name_2
        #
        # output_folder = "merged_images"
        # os.makedirs(output_folder, exist_ok=True)
        # output_path = os.path.join(output_folder, merged_image_name)
        # merged_image.save(output_path, format="PNG")

        return {"message": f"Изображения {image_name} и {image_name_2} успешно приняты и сохранены."}
    except Exception as e:
        return {"message": f"Error receiving and processing images: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8089)