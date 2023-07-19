# Code for 2020 China Hualu Cup Data Lake Algorithm Competition (Lane Detection Track)

## Introduction
Lane-Detection-with-ERFNet based paddlepaddle_v2.5

## Contents
1. [Installation](#installation)
2. [Datasets](#datasets)
3. [Training](#training)
4. [Evaluation](#evaluation)

## Installation
- [Anaconda3]
- [PaddlePaddle 2.5.0]
- OpenCV 4.8.0.74
- CUDA 11.2.2
- cuDNN 8.2.1.32
- TensorBoard (optional)
- pycocotools (optional)

Notes: 

- It may also run well on other versions but with no guarantee.

- TensorBoard is optional, just for recording training process. If not installed, feel free to comment relevant lines
of code.

- pycocotools is only required for visualization in `utils/visualization.py`.

For your convenience, we wrap up the installation process with the following commands.

```Shell
conda create -n paddle python=3.7 -y && conda activate paddle
pip install opencv-python==xxxx
python -m pip install paddlepaddle-gpu==xxx
pip install pycocotools
```

## Datasets
TRoM

We assume the directory layout for the competition dataset `PreliminaryData` as below.

    Project_ROOT
    └── datasets
        ├── __init__.py
        ├── lane_det.py
        └── PreliminaryData
            ├── train_pic            # contains training images
            │   ├── 10008283.jpg
            │   ├── ...
            │   └── 10024760.jpg
            ├── train_label          # contains correponding grayscale labels
            │   ├── 10008283.png
            │   ├── ...
            │   └── 10024760.png
            └── testB                # contains test images
                ├── 10014001.jpg
                ├── ...
                └── 10016129.jpg

Note: Due to copyright issues, we do not release the dataset used for the competition, feel free to adopt our method on
your own dataset.

## Training
To train the model, run the following command.
```Shell
python train_erfnet_paddle.py --epochs 150 -b 8 --lr 0.01
```
By default, we train our model with batch size 8 for 150 epochs on one RTX 2080ti GPU, which takes up approximately 
7,000 MB GPU memory and 24hrs to finish. Our model starts with the pretrained weights
`pretrained/ERFNet_pretrained.pdparams`, which is converted from the released torch version pretrained
[weights](https://github.com/cardwing/Codes-for-Lane-Detection/blob/master/ERFNet-CULane-PyTorch/pretrained/ERFNet_pretrained.tar)
on Cityscape dataset.

Notes:
- If you wish to reproduce our results, please do not modify the batch
size as it might impose uncertainty influence on the optimization steps.

- It will save the outputs (models and other records) to `trained/` by default. Feel free to change it to your 
expected directory by specifying `--save-dir path/to/output`.

## Evaluation
To reproduce our final results, just run this command:
```Shell
python test_erfnet_paddle.py
```
By default, it will test on our released model `trained/ERFNet_trained.pdparams`, which exactly obtains the final results
we submitted to the evaluation server.

To evaluate the models trained by yourself, simply add the `--resume` augment as:
```Shell
python test_erfnet_paddle.py --resume trained/erfnet_epxxx
```
Replace `xxx` with the epoch point you want to test. Note that we recommend you to test the model with the highest mIoU
on the training set, which is indicated by the file `trained/best_model`.

The testing results (prediction maps of lane markings) will be saved in `results/result` by default.



## License
This repo is released under the Apache 2.0 License (refer to the LICENSE file for details).

## Acknowledgement
This repo is mainly based on 
[Codes-for-Lane-Detection](https://github.com/cardwing/Codes-for-Lane-Detection/tree/master/ERFNet-CULane-PyTorch), many
thanks to them.

Should you have any questions regarding this repo, feel free to email me at ze001@e.ntu.edu.sg.
