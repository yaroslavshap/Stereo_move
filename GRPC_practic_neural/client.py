import math
from functools import reduce
import grpc
from my_pb2 import FileRequest
from my_pb2_grpc import FileTransferServiceStub
from dataloader import Dataloader2
from os.path import join
import statistics
import time


# функция для передачи потока от клиента
def get_client_stream_requests(images, path_l, path_r, stub, all_time):
    while True:
        for i in range(len(images.filenames1)):
            request = zapros(images, path_l, path_r, i)
            yield request
            # print("Отправлено")
        break


# функция по которой открываю нужные изображения и создаю запрос
def zapros(images, path_l, path_r, i):
    with open(join(path_l, images.filenames1[i]), 'rb') as f1, open(join(path_r, images.filenames2[i]), 'rb') as f2:
        image1_bytes = f1.read()
        image2_bytes = f2.read()

    request = FileRequest(
        image_1=image1_bytes,
        image_2=image2_bytes,
        filename1=str(images.filenames1[i]),
        filename2=str(images.filenames2[i]))
    return request


# унарная передача
def run_client_case1(images, path_l, path_r, stub, all_time):
    for i in range(len(images.filenames1)):
        request = zapros(images, path_l, path_r, i)
        start_time = time.time()  # Засекаем начальное время перед отправкой
        result = stub.Case1(request)
        # print(f"Способ 1: {result.message}")
        end_time = time.time()  # Засекаем время после получения ответа
        res_time = end_time - start_time
        all_time.append(res_time)
    return all_time


# поток от клиента
def run_client_case2(images, path_l, path_r, stub, all_time):
    start_time = time.time()
    result = stub.Case2(get_client_stream_requests(images, path_l, path_r, stub, all_time))
    end_time = time.time()
    res_time = end_time - start_time
    all_time.append(res_time)
    # print(f"Способ 2: {result.message}")
    return all_time


# поток от сервера
def run_client_case3(images, path_l, path_r, stub, all_time):
    for i in range(len(images.filenames1)):
        request = zapros(images, path_l, path_r, i)
        start_time = time.time()
        response_stream = stub.Case3(request)
        for hello_reply in response_stream:
            pass
            # print(hello_reply)
        end_time = time.time()
        res_time = end_time - start_time
        all_time.append(res_time)
    return all_time


# двунаправленный поток
def run_client_case4(images, path_l, path_r, stub, all_time):
    start_time = time.time()  # Засекаем начальное время перед отправкой
    response_stream = stub.Case4(get_client_stream_requests(images, path_l, path_r, stub, all_time))
    for response in response_stream:
        pass
        # print(response)
    end_time = time.time()  # Засекаем время после получения ответа
    res_time = end_time - start_time
    all_time.append(res_time)
    return all_time


def pechat(all_time, sred_time):
    # print("Массив, где хранится время передачи каждого изображения - ", all_time)
    print("Количество элементов в all_time - ", len(all_time))
    print("Сумма времени в all_time - ", math.fsum(all_time))
    print(f"Среднее время передачи для изображения - {sred_time}")


def run():
    # Устанавливаем максимальный размер сообщения на клиенте в 10 МБ
    max_message_length = 2000 * 1024 * 1024  # 10 МБ в байтах
    channel = grpc.insecure_channel('localhost:50052', options=(('grpc.max_send_message_length', max_message_length),))
    stub = FileTransferServiceStub(channel)
    path_l = "/Users/aroslavsapoval/myProjects/data/images_grpc_512/left"
    path_r = "/Users/aroslavsapoval/myProjects/data/images_grpc_512/right"
    images = Dataloader2(path_l, path_r)
    transfer_methods = {}
    popit = 0
    n = 0
    while True:
        all_time = []
        print("\n\n")
        print("1. Унарный - один запрос, один ответ")
        print("2. Поток от клиента, один ответ от сервера")
        print("3. Запрос от клиента, поток от сервера")
        print("4. Поток запросов от клиента, поток ответов от сервера")
        print("5. Все способы")
        print("6. Вывод таблицы значений (отсортировано по возрастанию среднего времени)")
        print("7. Выход")
        otvet = int(input("Выберете от 1 до 6:"))
        sred_time = None
        if otvet == 1:
            popit += 1
            all_time = run_client_case1(images, path_l, path_r, stub, all_time)
            sred_time = math.fsum(all_time) / len(all_time)
            pechat(all_time, sred_time)
            method = f"метод {otvet}"
            transfer_methods[popit] = {"method": method, "total_time": math.fsum(all_time), "average_time": sred_time}
        elif otvet == 2:
            popit += 1
            all_time = run_client_case2(images, path_l, path_r, stub, all_time)
            sred_time = math.fsum(all_time) / len(images.filenames1)
            pechat(all_time, sred_time)
            method = f"метод {otvet}"
            transfer_methods[popit] = {"method": method, "total_time": math.fsum(all_time), "average_time": sred_time}
        elif otvet == 3:
            popit += 1
            all_time = run_client_case3(images, path_l, path_r, stub, all_time)
            sred_time = math.fsum(all_time) / len(all_time)
            pechat(all_time, sred_time)
            method = f"метод {otvet}"
            transfer_methods[popit] = {"method": method, "total_time": math.fsum(all_time), "average_time": sred_time}
        elif otvet == 4:
            popit += 1
            all_time = run_client_case4(images, path_l, path_r, stub, all_time)
            sred_time = math.fsum(all_time) / len(images.filenames1)
            pechat(all_time, sred_time)
            method = f"метод {otvet}"
            transfer_methods[popit] = {"method": method, "total_time": math.fsum(all_time), "average_time": sred_time}
        elif otvet == 5:
            while n < 10:
                for i in range(1, 5):
                    popit += 1
                    all_time = []
                    sred_time = None
                    func_name = f"run_client_case{i}"
                    print(func_name)
                    func = globals()[func_name]
                    all_time = func(images, path_l, path_r, stub, all_time)
                    sred_time = math.fsum(all_time) / len(images.filenames1)
                    print(f"Способ - {i}")
                    pechat(all_time, sred_time)
                    method = f"метод {i}"
                    transfer_methods[popit] = {"method": method, "total_time": math.fsum(all_time),
                                               "average_time": sred_time}
                n += 1
        elif otvet == 6:
            sorted_methods = sorted(transfer_methods.items(), key=lambda x: x[1]["average_time"])
            for i in sorted_methods:
                print(i)
        elif otvet == 7:
            break


if __name__ == '__main__':
    run()
