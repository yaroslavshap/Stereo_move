import time
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import cv2
import torch.utils.data as data
from torch.nn.parallel import DistributedDataParallel
from torch.utils.data import BatchSampler, RandomSampler, DistributedSampler
from tqdm import tqdm
import sys
import torch.distributed as dist
import torch.multiprocessing as mp
from model import CommonNet
from dataloader import StereoDataset2


# считаю количество параметров в нейронной сети
def count_param(model_):
    return sum(p.numel() for p in model_.parameters() if p.requires_grad)


def otrisovka_pred(output, outputs_val):
    output = output[-1].detach().numpy()
    output = output.transpose(1, 2, 0)
    fig, ax = plt.subplots(1, 2, figsize=(20, 8))
    ax[0].matshow(output, label='Предсказано обучение')
    ax[0].set_xlabel('ширина')
    ax[0].set_ylabel('высота')
    ax[0].set_title("")
    ax[0].legend()

    outputs_val = outputs_val[-1].detach().numpy()
    outputs_val = outputs_val.transpose(1, 2, 0)
    ax[1].matshow(outputs_val, label='Предсказано валидация')
    ax[1].set_xlabel('ширина')
    ax[1].set_ylabel('высота')
    ax[1].set_title("")
    ax[1].legend()

    plt.show()


def otrisovka_graf(train_losses, val_losses, scheduller_values):
    fig, ax = plt.subplots(1, 3, figsize=(20, 8))
    ax[0].plot(train_losses, label='Train loss')
    ax[0].set_xlbel('Epoch')
    ax[0].set_ylabel('Train loss')
    ax[0].set_title("Train loss vs epoch")
    ax[0].legend()

    ax[1].plot(val_losses, label='Val loss')
    ax[1].set_xlbel('Epoch')
    ax[1].set_ylabel('Val loss')
    ax[1].set_title("Val loss vs epoch")
    ax[1].legend()

    ax[2].plot(scheduller_values, label='Learning rate')
    ax[2].set_xlabel('Epoch')
    ax[2].set_ylabel('Learning rate')
    ax[2].set_title("Learning rate vs epoch")
    ax[2].legend()

    plt.show()


def average_gradients(model):
    size = float(dist.get_world_size())
    for param in model.parameters():
        dist.all_reduce(param.grad.data, op=dist.ReduceOp.SUM)
        param.grad.data /= size


def iteration(trainloader, device, optimizer, model, running_loss, total, criterion, keff):
    for sample in trainloader:
        left = sample['image_l'].float().to(device)
        right = sample['image_r'].float().to(device)
        label = sample['image_lazer'].float().to(device)

        optimizer.zero_grad()
        outputs = model(left, right)
        loss = criterion(outputs[..., 120:, :], label[..., 120:, :])
        loss.backward()
        torch.nn.utils.clip_grad_norm(model.parameters(), 0.1)
        # усреднение градиентов
        average_gradients(model)
        # Синхронизация между узлами после каждой эпохи
        dist.barrier()
        optimizer.step()
        running_loss += loss.item()
        total += label.size(0)
        if keff == 0:
            trainloader.set_postfix_str(f'Rank {dist.get_rank()}, Loss:{running_loss / total:.6f}')

    return outputs, running_loss, total


def train_on_device(rank, world_size):
    # Инициализация процесса для каждого устройства
    dist.init_process_group(backend='nccl', world_size=world_size, rank=rank)
    # устройство, на котором будет выполняться обучение
    device = torch.device(f'cuda:{rank}' if torch.cuda.is_available() else 'cpu')
    # инициализирую
    model = CommonNet().to(device)

    # автоматическое управление распределенным обучением
    # model = DistributedDataParallel(model, device_ids=[rank], output_device=rank)

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # добавляю learning rate schedules
    scheduler = optim.lr_scheduler.MultiStepLR(optimizer, milestones=[60, 120, 160], gamma=0.1)
    print("Количество параметров в нейронной сети", count_param(model))
    num_epochs = 2

    data_folder_train = '/Users/aroslavsapoval/Desktop/data/Kitti_dataset/train'
    dataset = StereoDataset2(data_folder_train)
    trainloader = data.DataLoader(dataset, sampler=DistributedSampler(dataset, world_size, rank), batch_size=5)

    data_folder_validation = '/Users/aroslavsapoval/Desktop/data/Kitti_dataset/validation'
    dataset_val = StereoDataset2(data_folder_validation)
    trainloader_val = data.DataLoader(dataset_val, sampler=DistributedSampler(dataset_val, world_size, rank), batch_size=5)

    start_time = time.time()

    # обучаю модель
    model.train()
    train_losses = []
    val_losses = []
    scheduler_values = []
    for epoch in range(num_epochs):
        running_loss = 0.0
        correct, total = 0, 0
        trainloader = tqdm(trainloader, total=len(trainloader))
        # цикл по даталоадеру обучающему
        outputs, running_loss, total = iteration(trainloader, device, optimizer, model, running_loss, total, criterion,
                                                 keff=0)
        # цикл по даталоадеру валидационному
        outputs_val, running_loss_val, total_val = iteration(trainloader_val, device, optimizer, model, running_loss,
                                                             total, criterion, keff=1)

        # scheduler.step()
        # scheduler_values.append(scheduler.get_last_lr()[0])
        train_losses.append(running_loss / total)
        val_losses.append(running_loss_val / total_val)

        # Print epoch results
        print(f'[Epoch {epoch}] Train loss: {running_loss / total:.6f} Val loss: {running_loss_val / total_val}')

        if epoch % 10 == 0 and rank == 0:
            # save the trained weights
            weights_file = f'siam_prob_2_epoch-{epoch}.pth'
            torch.save(model.module.state_dict(), weights_file)

    end_time = time.time()
    print(f"Total time taken for training: {end_time - start_time:.3f} seconds.")

    if rank == 0:
        # отрисовываю картинки обучения и валидации
        otrisovka_pred(outputs, outputs_val)
        # отрисовываю графики ошибки обуения / ошибки валидации
        otrisovka_graf(train_losses, val_losses, scheduler_values)


if __name__ == "__main__":
    world_size = dist.get_world_size()  # Количество устройств для параллельного обучения
    mp.spawn(train_on_device, args=(world_size,), nprocs=world_size, join=True)
    # mp.spawn - для запуска каждого процесса в отдельном исполняемом контексте (поэтому dist.barrier() тут можно не использовать)
    # join=True - программа будет ждать завершения всех процессов, прежде чем завершить свою работу
    # nprocs=world_size - сколько процессов (устройств) будет создано для выполнения функции train_on_device
