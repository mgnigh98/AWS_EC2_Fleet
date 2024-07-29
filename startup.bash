#!/bin/bash
tmux_send(){
    tmux send-keys -t aws "$1" C-m
}

@echo off
# creates a tmux session with the name 'aws'
tmux new -d -s aws

# mounts the ephemeral drive
sudo mkfs -t xfs /dev/nvme1n1
sudo mkdir "$HOME/nvme"
sudo mount /dev/nvme1n1 "$HOME/nvme"
sudo chmod 777 $HOME/nvme
sudo apt install unzip
sudo apt-get install libgl1 -y

# downloads and installs aws cli
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "nvme/awscliv2.zip"
unzip ~/nvme/awscliv2.zip -d ~/nvme
rm ~/nvme/awscliv2.zip
sudo ./nvme/aws/install

# # downloads and installs miniconda
# sudo apt update
mkdir -p ~/nvme/miniconda3
mkdir -p ~/nvme/python/files
mkdir -p ~/nvme/python/epochs/model_weights/
touch ~/nvme/python/epochs/model_weights/stop.txt
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/nvme/miniconda3/miniconda.sh
bash ~/nvme/miniconda3/miniconda.sh -b -u -p ~/nvme/miniconda3
rm -rf ~/nvme/miniconda3/miniconda.sh

tmux_send "echo PATH='/home/ubuntu/nvme/miniconda3/bin:$PATH' >> ~/.bashrc"
tmux_send 'source ~/.bashrc'

tmux_send 'bash conda.bash'







