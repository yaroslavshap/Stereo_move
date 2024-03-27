import math
from functools import reduce
import grpc
from my_pb2 import FileRequest, BatchRequest
from my_pb2_grpc import FileTransferServiceStub
from dataloader import Dataloader
from os.path import join
import time
import threading
import copy

# Создаем массив для хранения изображений он сразу идет объектом сообщения из файла proto
batch_request = BatchRequest()
# Создаем блокировку для безопасного доступа к массиву изображений
image_lock = threading.Lock()




mass_all = []
image_lock2 = threading.Lock()



# Функция для считывания изображений и добавления их в массив с задержкой
def read_images(images, path_l, path_r):
    global batch_request  # Объявляем, что мы используем глобальную переменную
    while True:
        for i in range(len(images.filenames1)):
            print("Изображение добавленное в массив - ", images.filenames1[i])
            request = zapros(images, path_l, path_r, i)

            with image_lock:  # Блокируем доступ к массиву
                batch_request.images.extend([request])  # Добавляем изображение к batch_request

            print("количество изображений в массиве скопилось - ", len(batch_request.images))
            time.sleep(1)  # Задержка в 1 секунду


# функция по которой открываю нужные изображения и создаю запрос
def zapros(images, path_l, path_r, i):
    with open(join(path_l, images.filenames1[i]), 'rb') as f1, open(join(path_r, images.filenames2[i]), 'rb') as f2:
        image1_bytes = f1.read()
        image2_bytes = f2.read()

    request = FileRequest(
        image_1=image1_bytes,
        image_2=image2_bytes,
        filename1=str(images.filenames1[i]),
        filename2=str(images.filenames1[i]))

    return request


# унарная передача
def run_client_case5(stub, all_time):
    while True:
        time.sleep(0.7)
        print("tut")
        global batch_request
        if batch_request.images:
            data_to_send = copy.copy(batch_request)
            print(len(data_to_send.images))
            # новый пустой объект BatchRequest, который заменит глобальный объект
            batch_request = BatchRequest()
            result = stub.Case5(data_to_send)
            print("Результат - ", result)






def read_images_2(images, path_l, path_r):
    global mass_all
    while True:
        time.sleep(10)
        for i in range(len(images.filenames1)):
            print("Изображение добавленное в массив - ", images.filenames1[i])
            request = zapros(images, path_l, path_r, i)
            with image_lock2:
                mass_all.append(request)
            print("количество изображений в массиве скопилось - ", len(mass_all))



# функция для передачи потока от клиента
def get_client_stream_requests(images, path_l, path_r, stub):
    global mass_all
    while True:
        for i in mass_all:
            yield i
        break



# двунаправленный поток
def run_client_case_2(images, path_l, path_r, stub):

    response_stream = stub.Case4(get_client_stream_requests(images, path_l, path_r, stub))
    for response in response_stream:
        print("response - ", response)




def run():
    channel = grpc.insecure_channel('localhost:50053')

    # Устанавливаем максимальный размер сообщения на клиенте в 10 МБ
    max_message_length = 100 * 1024 * 1024  # 10 МБ в байтах
    channel = grpc.insecure_channel('localhost:50053', options=(('grpc.max_send_message_length', max_message_length),))

    stub = FileTransferServiceStub(channel)
    path_l = "/Users/aroslavsapoval/Desktop/data_grpc/left"
    path_r = "/Users/aroslavsapoval/Desktop/data_grpc/right"
    images = Dataloader(path_l, path_r)
    while True:
        all_time = []
        print("\n\n\n\n\n")
        print("2. Выход")
        print("3. Поток запросов от клиента, поток ответов от сервера")
        print("4 - унарная передача массива")
        otvet = input("Выберете от 2 до 4:")

        if otvet == "2":
            break
        elif otvet == "3":
            read_thread = threading.Thread(target=read_images_2, args=(images, path_l, path_r))
            sent_thread = threading.Thread(target=run_client_case_2, args=(images, path_l, path_r, stub))
            read_thread.start()
            sent_thread.start()
            # Ожидаем завершения потоков
            read_thread.join()
            sent_thread.join()
        elif otvet == "4":
            read_thread = threading.Thread(target=read_images, args=(images, path_l, path_r))
            sent_thread = threading.Thread(target=run_client_case5, args=(stub,  all_time))
            read_thread.start()
            sent_thread.start()
            # Ожидаем завершения потоков
            read_thread.join()
            sent_thread.join()


if __name__ == '__main__':
    run()
