#!/bin/bash
conda update -n base -c defaults conda -y
conda create --name="aws" python==3.9 -y
source ~/nvme/miniconda3/bin/activate aws
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y
conda install lightning -c conda-forge -y
conda install anaconda::pandas -y
conda install anaconda::absl-py -y
conda install conda-forge::sarpy -y
conda install conda-forge::deprecated -y
touch ~/conda_done