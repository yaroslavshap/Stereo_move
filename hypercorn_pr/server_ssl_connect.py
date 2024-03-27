from hypercorn.config import Config
from hypercorn.asyncio import serve
import asyncio
import ssl
import os
from PIL import Image
from typing import Union
from fastapi import FastAPI, UploadFile, File, Form

app = FastAPI()

@app.post("/receive_images/")
async def receive_images(file1: UploadFile = File(...), file2: UploadFile = File(...), image_name: str = Form(...), image_name_2: str = Form(...)):
    try:
        # Сохраняем полученные изображения на диск
        image1 = Image.open(file1.file)
        image2 = Image.open(file2.file)

        merged_image = Image.new("RGB", (image1.width + image2.width, max(image1.height, image2.height)))
        merged_image.paste(image1, (0, 0))
        merged_image.paste(image2, (image1.width, 0))
        merged_image_name = image_name + "_" + image_name_2

        output_folder = "merged_images"
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, merged_image_name)
        merged_image.save(output_path, format="PNG")

        return {"message": f"Изображения {image_name} и {image_name_2} успешно приняты и сохранены."}
    except Exception as e:
        return {"message": f"Error receiving and processing images: {str(e)}"}

ssl_connect = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)  # создает новый контекст SSL с настройками по умолчанию.
ssl_connect.load_cert_chain(certfile="cert2.pem", keyfile="key2.pem") # загружает сертификат и приватный ключ из файлов localhost.crt и localhost.key соответственно
# ssl_connect.load_cert_chain(certfile="localhost.crt", keyfile="localhost.key")
# ssl_connect = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# ssl_connect.load_cert_chain(certfile="cert.pem",
#                             keyfile="key.pem",
#                             password='qwerty')
ssl_connect.minimum_version=ssl.TLSVersion.TLSv1_2 # устанавливает минимальную поддерживаемую версию протокола SSL/TLS.

config = Config() # объект конфигурации
config.bind = ["myprogdom.ru:443"] # адрес привязки
config.ssl = ssl_connect # устанавливаете контекст

# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     task = loop.create_task(serve(app, config))
#
#     try:
#         loop.run_until_complete(task)
#     except KeyboardInterrupt:
#         print("Shutting down...")
#     finally:
#         task.cancel()
#         loop.run_until_complete(task)

if __name__ == "__main__":
    asyncio.run(serve(app, config))