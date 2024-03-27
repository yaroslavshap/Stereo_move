# Сервер с использованием Quart
import io

from server_quart import Quart, request
from PIL import Image

app = Quart(__name__)

@app.route("/receive_images/", methods=["POST"])
async def receive_images():
    try:
        file = (await request.files)["file"]  # Прочитать содержимое файла
        image = Image.open(io.BytesIO(file))  # Открыть изображение из байтового потока

        return {"message": f"Изображение {request.files['file'].name} успешно принято."}
    except Exception as e:
        return {"message": f"Error receiving and processing images: {str(e)}"}

# if __name__ == "__main__":
#
#     app.run(host="127.0.0.1", port=8000)

