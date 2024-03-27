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
from model import CommonNet
import numpy as np

class FileTransferService(my_pb2_grpc.FileTransferServiceServicer):

    def __init__(self):
        self.image_name1 = None
        self.image_name2 = None
        self.merged_image_name = None


    def work_with_img(self, request, context, case_nom):
        device = torch.device('cpu')
        width_1 = 512
        height_1 = 256
        model = CommonNet()
        model.to(device)
        model.load_state_dict(torch.load(r'/Users/aroslavsapoval/myProjects/Practic3/GRPC_practic_neural/ves.pth'))
        image1 = Image.open(BytesIO(request.image_1))
        image2 = Image.open(BytesIO(request.image_2))
        left_test = np.array(image1.convert('RGB').resize((width_1, height_1), Image.BICUBIC))
        right_test = np.array(image2.convert('RGB').resize((width_1, height_1), Image.BICUBIC))
        model.eval()
        with torch.no_grad():
            left_test = left_test.transpose(2, 0, 1).astype('float32') / 255.0
            right_test = right_test.transpose(2, 0, 1).astype('float32') / 255.0
            left_test = torch.from_numpy(left_test).unsqueeze(0).to(device)
            right_test = torch.from_numpy(right_test).unsqueeze(0).to(device)
            pred = model(left_test, right_test).squeeze(0)
            pred = pred.squeeze(0)
            pred = pred[..., 100:, :].detach().cpu().numpy()

        pred_img = Image.fromarray(255 * pred.astype(np.uint8))
        self.image_name1 = request.filename1
        self.image_name2 = request.filename2
        self.merged_image_name = self.image_name1 + "_" + self.image_name2
        output_folder = f"merged_image_case_{case_nom}"
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, self.merged_image_name)
        pred_img.save(output_path, format="PNG")


    def Case1(self, request, context):
        self.work_with_img(request, context, case_nom=1)
        response = my_pb2.FileResponse(message="Images were successfully transferred to the server using 1 method")
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
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         options=[('grpc.max_receive_message_length', 2000 * 1024 * 1024)])
    my_pb2_grpc.add_FileTransferServiceServicer_to_server(FileTransferService(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print("Сервер запущен на порту 50052...")
    server.wait_for_termination()


if __name__ == '__main__':
    run_server()
