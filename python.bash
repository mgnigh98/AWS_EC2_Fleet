#!/bin/bash
FILE_DIR="nvme/python/NAFNet/datasets"
if [ ! -d "${FILE_DIR}/sicd" ]; then
#copy zip file from s3 bucket, unzip it and remove the original zip file
    s3_FILE="sicd_focused"
    ulimit -n 4096
    aws s3 cp "s3://synthetic-sicd-pairs/${s3_FILE}.zip" "${FILE_DIR}/sicd.zip"
    unzip -q "${FILE_DIR}/sicd.zip" -d "${FILE_DIR}"
    rm "${FILE_DIR}/sicd.zip"
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