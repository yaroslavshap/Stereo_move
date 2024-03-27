from fastapi import FastAPI, UploadFile, File, Form
from PIL import Image
import os
import shutil

app = FastAPI()

@app.post("/receive_images/")
async def receive_images(
    file1: bytes = File(...),
    file2: bytes = File(...),
    image_name: str = Form(...),
    image_name_2: str = Form(...),
):
    try:
        # Создаем временную директорию для сохранения изображений
        temp_dir = "temp_images"
        os.makedirs(temp_dir, exist_ok=True)

        # Сохраняем полученные изображения во временную директорию
        with open(os.path.join(temp_dir, image_name), "wb") as f1, open(os.path.join(temp_dir, image_name_2), "wb") as f2:
            f1.write(file1)
            f2.write(file2)

        # Загружаем изображения и выполняем операции
        image1 = Image.open(os.path.join(temp_dir, image_name))
        image2 = Image.open(os.path.join(temp_dir, image_name_2))

        merged_image = Image.new("RGB", (image1.width + image2.width, max(image1.height, image2.height)))
        merged_image.paste(image1, (0, 0))
        merged_image.paste(image2, (image1.width, 0))

        # Сохраняем объединенное изображение
        output_folder = "merged_images"
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, f"{image_name}_{image_name_2}.png")
        merged_image.save(output_path, format="PNG")

        # Удаляем временную директорию
        shutil.rmtree(temp_dir, ignore_errors=True)

        return {"message": f"Изображения {image_name} и {image_name_2} успешно приняты и сохранены."}
    except Exception as e:
        return {"message": f"Ошибка при приеме и обработке изображений: {str(e)}"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="localhost", port=8021, reload=True)
