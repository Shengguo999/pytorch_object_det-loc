# pytorch_object_det-loc
object detection and localization by pytorch
训练权重模型已经加载好，理论上安装完各种包就可以开始识别了。

数据集也可以用自己的，但这里不包括训练模块，只有直接用已经训练好的权重文件识别的模块。

可以识别如下物体
    "aeroplane": 1,
    "bicycle": 2,
    "bird": 3,
    "boat": 4,
    "bottle": 5,
    "bus": 6,
    "car": 7,
    "cat": 8,
    "chair": 9,
    "cow": 10,
    "dining-table": 11,
    "dog": 12,
    "horse": 13,
    "motorbike": 14,
    "person": 15,
    "potted-plant": 16,
    "sheep": 17,
    "sofa": 18,
    "train": 19,
    "tv-monitor": 20
好像不支持中文显示

需要安装的包如下：
lxml==4.6.2
matplotlib==3.2.1
numpy==1.17.0
tqdm==4.42.1
torch==1.6.0
torchvision==0.7.0
pycocotools==2.0.0
Pillow==8.0.1
