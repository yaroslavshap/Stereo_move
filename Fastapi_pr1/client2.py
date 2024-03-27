import os
import time
import httpx
from fastapi import FastAPI
import uvicorn
import asyncio

app = FastAPI()

# URL адрес первого микросервиса (отправителя)
sender_url = "http://localhost:8011/receive_images/"

# Путь к папкам с изображениями на сервере отправителя
folder1 = "/Users/aroslavsapoval/myProjects/data/images_grpc_1980/left"

@app.post("/send-images/")
async def send_images():
    try:
        # Получение списка файлов из папок
        files1 = os.listdir(folder1)

        total_time = 0

        async with httpx.AsyncClient() as client:
            # Организация цикла для отправки каждой пары изображений
            for filename1 in files1:
                file1_path = os.path.join(folder1, filename1)

                # Отправляем пару изображений на второй сервер
                with open(file1_path, "rb") as file1:

                    start_time = time.time()  # Засекаем время передачи
                    response = await client.post(sender_url, files={"file1": file1})
                    end_time = time.time()  # Засекаем время завершения передачи
                    transfer_time = end_time - start_time
                    total_time += transfer_time

                    response_data = response.json()

                    if response.status_code == 200:
                        print(f"Images {filename1} sent successfully.")
                        print(f"время передачи {transfer_time} секунд.")
                        print("Ответ сервера:", response.text)  # Вывод ответа от сервера
                    else:
                        print(f"Error sending image {filename1}: {response.text}")

            print(f"Общее время передачи изображений: {total_time} секунд.")
    except Exception as e:
        print(f"Error sending images: {str(e)}")


# событие, которое асинхронно запускается при старте сервера
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_images())


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8012)

# if __name__ == "__main__":
#     asyncio.run(send_images())
