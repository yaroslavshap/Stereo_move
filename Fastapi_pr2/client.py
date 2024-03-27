import time
from fastapi import FastAPI
import os
import httpx
import asyncio
import uvicorn

app = FastAPI()

# URL адрес второго сервера
second_server_url = "http://localhost:8021/receive_images/"

# Путь к папкам с изображениями на сервере отправителя
folder1 = "/Users/aroslavsapoval/myProjects/data/images_grpc_1980/left"
folder2 = "/Users/aroslavsapoval/myProjects/data/images_grpc_1980/right"
results = []


@app.post("/send-images/")
async def send_images():
    try:
        # Получение списка файлов из папок
        files1 = sorted(os.listdir(folder1))
        files2 = sorted(os.listdir(folder2))

        # Проверка, что количество файлов в папках совпадает
        if len(files1) != len(files2):
            return {"message": "Несоответствие количества файлов в папках."}

        total_time = 0

        async with httpx.AsyncClient() as client:
            # Организация цикла для отправки каждой пары изображений
            for i in range(len(files1)):
                file1_path = os.path.join(folder1, files1[i])
                file2_path = os.path.join(folder2, files2[i])

                # Отправляем пару изображений на второй сервер
                with open(file1_path, "rb") as file1, open(file2_path, "rb") as file2:
                    file1_bytes = file1.read()  # Прочитать содержимое файла 1 в виде байтов
                    file2_bytes = file2.read()
                    data = {"image_name": files1[i], "image_name_2": files2[i]}  # Используем имя первого изображения для уникальности

                    start_time = time.time()  # Засекаем время передачи
                    response = await client.post(second_server_url, files={"file1": file1_bytes, "file2": file2_bytes}, data=data)
                    end_time = time.time()  # Засекаем время завершения передачи
                    transfer_time = end_time - start_time
                    total_time += transfer_time

                    response_data = response.json()

                    if response.status_code == 200:
                        print(f"время передачи этой пары изображений: {transfer_time} секунд.")
                        print("Ответ сервера:", response.text)
                    else:
                        print(f"Error sending images {files1[i]} and {files2[i]}: {response_data['message']}")
            print(f"Общее время передачи изображений: {total_time} секунд.")
            # results.append(total_time)
            print(f"Среднее время передачи изображения - {total_time/len(files1)} секунд.")
        return {"message": "Images sent successfully.", "total_time": total_time}
    except Exception as e:
        return {"message": f"Error sending images: {str(e)}"}


# событие, которое асинхронно запускается при старте сервера
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_images())


if __name__ == "__main__":
    uvicorn.run("client:app", host="localhost", port=8022, reload=True)