import os
import time
import json

import torch
import torchvision
from PIL import Image
import matplotlib.pyplot as plt

from torchvision import transforms
from network_files.faster_rcnn_framework import FasterRCNN, FastRCNNPredictor
from backbone.resnet50_fpn_model import resnet50_fpn_backbone
from network_files.rpn_function import AnchorsGenerator
from backbone.mobilenetv2_model import MobileNetV2
from draw_box_utils import draw_box


# print("hello")
def create_model(num_classes):
    # mobileNetv2+faster_RCNN
    # backbone = MobileNetV2().features
    # backbone.out_channels = 1280
    #
    # anchor_generator = AnchorsGenerator(sizes=((32, 64, 128, 256, 512),),
    #                                     aspect_ratios=((0.5, 1.0, 2.0),))
    #
    # roi_pooler = torchvision.ops.MultiScaleRoIAlign(featmap_names=['0'],
    #                                                 output_size=[7, 7],
    #                                                 sampling_ratio=2)
    #
    # model = FasterRCNN(backbone=backbone,
    #                    num_classes=num_classes,
    #                    rpn_anchor_generator=anchor_generator,
    #                    box_roi_pool=roi_pooler)

    # resNet50+fpn+faster_RCNN
    backbone = resnet50_fpn_backbone()
    model = FasterRCNN(backbone=backbone, num_classes=num_classes)

    return model


def main():
    # get devices
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("using {} device.".format(device))

    # create model
    model = create_model(num_classes=2)

    # load train weights
    train_weights = "./save_weights/resNetFpn-model-5.pth"
    assert os.path.exists(train_weights), "{} file dose not exist.".format(train_weights)
    model.load_state_dict(torch.load(train_weights, map_location=device)["model"])
    model.to(device)

    # read class_indict
    label_json_path = './pascal_voc_classes.json'
    assert os.path.exists(label_json_path), "json file {} dose not exist.".format(label_json_path)
    json_file = open(label_json_path, 'r')
    class_dict = json.load(json_file)
    category_index = {v: k for k, v in class_dict.items()}

    # load image
    original_img = Image.open("./tree3.jpg")

    # from pil image to tensor, do not normalize image
    data_transform = transforms.Compose([transforms.ToTensor()])
    img = data_transform(original_img)
    # expand batch dimension
    img = torch.unsqueeze(img, dim=0)

    model.eval()  # 进入验证模式
    with torch.no_grad():
        # init
        img_height, img_width = img.shape[-2:]
        init_img = torch.zeros((1, 3, img_height, img_width), device=device)
        model(init_img)

        t_start = time.time()
        predictions = model(img.to(device))[0]
        print("inference+NMS time: {}".format(time.time() - t_start))

        predict_boxes = predictions["boxes"].to("cpu").numpy()
        predict_classes = predictions["labels"].to("cpu").numpy()
        predict_scores = predictions["scores"].to("cpu").numpy()

        print("如果提示目标大小合适，目标左右位置合适，目标上下位置合适，则可以拍照")

        ws, hs = predict_boxes[:, 2] - predict_boxes[:, 0], predict_boxes[:, 3] - predict_boxes[:, 1]
        if (hs / img_height > 0.6) | (ws / img_width > 0.6):
            print("目标物过大，请将摄像头向远处移动")
        elif (hs / img_height < 0.2) | (ws / img_width < 0.2):
            print("目标物过小，请将摄像头向近处移动")
        else:
            print("目标大小合适")

        if (predict_boxes[:, 2] > 0.5*img_width) & (predict_boxes[:, 0] > 0.5*img_width):
            print("目标物过右，请将摄像头向右侧移动，使物体出现在中央")
        elif (predict_boxes[:, 2] < 0.5*img_width) & (predict_boxes[:, 0] < 0.5*img_width):
            print("目标物过左，请将摄像头向左侧移动，使物体出现在中央")
        else:
            print("目标左右位置合适")

        if (predict_boxes[:, 3] < 0.5*img_height) & (predict_boxes[:, 1] < 0.5*img_height):
            print("目标物过上，请将摄像头向上移动，使物体出现在中央")
        elif (predict_boxes[:, 3] > 0.5*img_height) & (predict_boxes[:, 1] > 0.5*img_height):
            print("目标物过下，请将摄像头向下移动，使物体出现在中央")
        else:
            print("目标上下位置合适")

        if len(predict_boxes) == 0:
            print("没有检测到任何目标!")

        draw_box(original_img,
                 predict_boxes,
                 predict_classes,
                 predict_scores,
                 category_index,
                 thresh=0.5,
                 line_thickness=3)
        plt.imshow(original_img)
        plt.show()
        # 保存预测的图片结果
        original_img.save("test_result-tree2.jpg")


if __name__ == '__main__':
    main()
