#!/bin/bash
FILE_DIR="nvme/python/NAFNet/datasets"
if [ ! -d "${FILE_DIR}/sicd" ]; then
#copy zip file from s3 bucket, unzip it and remove the original zip file
    sudo mkfs -t xfs /dev/nvme2n1
    sudo mount /dev/nvme2n1 "$FILE_DIR"
    sudo chmod 777 $FILE_DIR
    s3_DIR="data200k"
    ulimit -n 4096
    aws s3 cp --recursive "s3://synthetic-sicd-pairs/${s3_DIR}/" "${FILE_DIR}/sicd/" --quiet
    # tar -xf "${FILE_DIR}/sicd/val.tar" -d "${FILE_DIR}"
    # unzip -q "${FILE_DIR}/sicd.zip" -d "${FILE_DIR}"
    # rm "${FILE_DIR}/sicd/val.tar"
fi
source ~/nvme/miniconda3/bin/activate aws
pip install -e ~/nvme/python/tim_utils
pip install -e ~/nvme/python/complextorch

cd nvme/python/NAFNet
pip install -r requirements.txt
python setup.py develop --no_cuda_ext
bash start.sh
# python3 ~/nvme/python/CV_SR_lightning.py 100 5 False
sleep 5m
sudo shutdown
