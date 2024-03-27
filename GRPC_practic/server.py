import time

import cv2
import grpc
from concurrent import futures
from PIL import Image
from io import BytesIO
import my_pb2
import my_pb2_grpc
import os
import torch
import numpy as np

class FileTransferService(my_pb2_grpc.FileTransferServiceServicer):

    def __init__(self):
        self.image_name1 = None
        self.image_name2 = None
        self.merged_image_name = None


    def work_with_img(self, request, context, case_nom):

        image1_bytes = request.image_1
        self.image_name1 = request.filename1
        output_folder = f"images_left"
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, self.image_name1)
        with open(output_path, "wb") as file:
            file.write(image1_bytes)

        image2_bytes = request.image_2
        self.image_name2 = request.filename2
        output_folder = f"images_right"
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, self.image_name2)
        with open(output_path, "wb") as file:
            file.write(image2_bytes)

    def Case1(self, request, context):
        print(request.filename1)
        self.work_with_img(request, context, case_nom=1)
        response = my_pb2.FileResponse(message=f"Images {request.filename1} and {request.filename2}")
        return response

    def Case2(self, request_iterator, context):
        all_img = []
        for request in request_iterator:
            # all_img.append(request.filename1)
            self.work_with_img(request, context, case_nom=2)
            all_img.append(self.merged_image_name)

        response = my_pb2.FileResponse(message=f"Images were successfully transferred to the server using 2 method. You have sent {len(all_img)}")
        return response

    def Case3(self, request, context):
        self.work_with_img(request, context, case_nom=3)
        for i in range(3):
            response = my_pb2.FileResponse(message=f"Images were successfully transferred to the server using 3 method {i + 1}")
            yield response

    def Case4(self, request_iterator, context):
        for request in request_iterator:
            self.work_with_img(request, context, case_nom=4)
            response = my_pb2.FileResponse(
                message=f"Images {self.image_name1} and {self.image_name2} were successfully transferred to the server using 4 method.")
            yield response


def run_server():
    host = '127.0.0.1'
    port = '8099'

    # # Загрузите сертификаты
    # with open('/Users/aroslavsapoval/myProjects/Practic3/GRPC_practic/cert.pem', 'rb') as f:
    #     server_certificate = f.read()
    # with open('/Users/aroslavsapoval/myProjects/Practic3/GRPC_practic/key.pem', 'rb') as f:
    #     server_key = f.read()
    #
    # # Создайте учетные данные сервера
    # server_credentials = grpc.ssl_server_credentials(((server_key, server_certificate),))

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         options=[('grpc.max_receive_message_length', 2000 * 1024 * 1024)])
    my_pb2_grpc.add_FileTransferServiceServicer_to_server(FileTransferService(), server)

    server.add_insecure_port(f'{host}:{port}')    # , server_credentials
    server.start()
    print(f"Сервер запущен на {host}:{port}") # http://{host}:{port}
    server.wait_for_termination()


if __name__ == '__main__':
    run_server()
