# ELEKTRONN3 - Neural Network Toolkit
#
# Copyright (c) 2019 - now
# Max Planck Institute of Neurobiology, Munich, Germany
# Authors: Jonathan Klimesch

import os
import torch
import argparse
# Don't move this stuff, it needs to be run this early to work
import elektronn3
elektronn3.select_mpl_backend('Agg')
import morphx.processing.clouds as clouds
from torch import nn
from morphx.data.torchset import TorchSet
from elektronn3.models.convpoint import SegSmall, SegBig
from elektronn3.training.trainer3d import Trainer3d, Backup


# PARSE PARAMETERS #

parser = argparse.ArgumentParser(description='Train a network.')
parser.add_argument('--na', type=str, default="pointcloud_TEST", help='Experiment name')
parser.add_argument('--tp', type=str, default="/wholebrain/scratch/yliu/merger_gt_semseg_pointcloud/gt_results/", help='Train path')
parser.add_argument('--sr', type=str, default="/wholebrain/scratch/yliu/pointcloud_train_result/", help='Save root')
parser.add_argument('--bs', type=int, default=16, help='Batch size')
parser.add_argument('--sp', type=int, default=1000, help='Number of sample points')
parser.add_argument('--ra', type=int, default=10000, help='Radius')
parser.add_argument('--cl', type=int, default=2, help='Number of classes')
parser.add_argument('--co', action='store_true', help='Disable CUDA')
parser.add_argument('--big', action='store_true', help='Use big SegBig Convpoint network')

args = parser.parse_args()


# SET UP ENVIRONMENT #

use_cuda = not args.co

# define parameters
name = args.na
batch_size = args.bs
npoints = args.sp
radius = args.ra
num_classes = args.cl
milestones = [60, 120]
lr = 1e-3
lr_stepsize = 1000
lr_dec = 0.995
max_steps = 500000

if use_cuda:
    device = torch.device('cuda')
else:
    device = torch.device('cpu')

print(f'Running on device: {device}')

# set paths
save_root = os.path.expanduser(args.sr)
train_path = os.path.expanduser(args.tp)


# CREATE NETWORK AND PREPARE DATA SET#

input_channels = 1
if args.big:
    model = SegBig(input_channels, num_classes)
else:
    model = SegSmall(input_channels, num_classes)

if use_cuda:
    if torch.cuda.device_count() > 1:
        print("Let's use", torch.cuda.device_count(), "GPUs!")
        batch_size = batch_size * torch.cuda.device_count()
        model = nn.DataParallel(model)
    model.to(device)

# Transformations to be applied to samples before feeding them to the network
train_transform = clouds.Compose([clouds.RandomRotate(), clouds.Center()])

train_ds = TorchSet(train_path, radius, npoints, train_transform, class_num=num_classes)
import pdb
pdb.set_trace()

# PREPARE AND START TRAINING #

# set up optimization
optimizer = torch.optim.Adam(model.parameters(), lr=lr)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, lr_stepsize, lr_dec)

criterion = torch.nn.CrossEntropyLoss()
if use_cuda:
    criterion.cuda()

# Create trainer
trainer = Trainer3d(
    model=model,
    criterion=criterion,
    optimizer=optimizer,
    device=device,
    train_dataset=train_ds,
    batchsize=batch_size,
    num_workers=0,
    save_root=save_root,
    exp_name=name,
    schedulers={"lr": scheduler},
)

# Archiving training script, src folder, env info
bk = Backup(script_path=__file__,
            save_path=trainer.save_path).archive_backup()

# Start training
trainer.run(max_steps)