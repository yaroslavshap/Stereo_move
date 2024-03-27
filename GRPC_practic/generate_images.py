from PIL import Image
import numpy as np
import os

path = "/Users/aroslavsapoval/myProjects/images_grpc_512/left"
path2 = "/Users/aroslavsapoval/myProjects/images_grpc_512/right"

# Создайте папку для сохранения изображений, если она не существует
if not os.path.exists(path):
    os.makedirs(path)

# Создайте папку для сохранения изображений, если она не существует
if not os.path.exists(path2):
    os.makedirs(path2)

# Размер изображений
width = 512
height = 256

# Количество изображений, которые нужно создать
num_images = 200

for i in range(num_images):
    # Создаем случайное изображение с использованием NumPy
    image_data = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    image = Image.fromarray(image_data)
    # Создаем случайное изображение с использованием NumPy
    image_data_2 = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    image_2 = Image.fromarray(image_data_2)

    # Сохраняем изображение в формате PNG
    image.save(os.path.join(path, f"image_{i + 1}_l.png"))
    image_2.save(os.path.join(path2, f"image_{i + 1}_r.png"))

print(f"Создано {num_images} изображений и сохранено по пути: {path}.")
print(f"Создано {num_images} изображений и сохранено по пути: {path2}.")
