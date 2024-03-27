import httpx
import time
import asyncio

async def send_file_to_server():
    try:
        url = "https://127.0.0.1:8003/receive_images/"
        file_path = "/hypercorn_pr/large_file.bin"

        async with httpx.AsyncClient(http2=True, verify=False) as client:
            with open(file_path, "rb") as file:
                start_time = time.time()  # Засекаем время передачи
                response = await client.post(url, files={"file": file})
                end_time = time.time()  # Засекаем время завершения передачи
                transfer_time = end_time - start_time
                print(f"{transfer_time} секунд")
                print(response.http_version)
            if response.status_code == 200:
                print("File uploaded successfully.")
                print("Server response:", response.text)
            else:
                print("Error:", response.text)
    except Exception as e:
        print(f"Error sending file: {e}")


# # Запуск функции отправки файла
# await send_file_to_server()
if __name__ == "__main__":
    asyncio.run(send_file_to_server())
