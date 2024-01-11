# -*-coding:utf-8 -*-
# Author: Zenghui Tang
# Date: 2024/1/10
# Time: 18:51
import os
import json
import numpy as np
from tqdm import tqdm
from tqdm.contrib import tzip
from utils.common import walk_file, get_img_label_paths
from utils.read_write import label_write


def print_classes(json_dir):
    json_paths = walk_file(json_dir, suffixs=".json")

    classes = set()
    for json_path in tqdm(json_paths):
        with open(json_path, "r") as json_object:
            json_label = json.load(json_object)
            for json_rect in json_label["shapes"]:
                classes.add(json_rect["label"])
    print(classes)
    return None


def json2txt(json_dir):
    img_paths, label_paths = get_img_label_paths(json_dir)
    for img_path, label_path in tzip(img_paths, label_paths):
        json_path = os.path.splitext(img_path)[0] + ".json"
        if not os.path.exists(json_path):
            label_write(label_path, "\n")
        else:
            with open(json_path, "r") as json_object:
                json_label = json.load(json_object)
                img_w = int(json_label["imageWidth"])
                img_h = int(json_label["imageHeight"])

                xyxy = []
                for json_rect in json_label["shapes"]:
                    cls = CLASSES.index(str(json_rect["label"]))  # 获取类别索引
                    x1, y1, x2, y2 = np.ravel(json_rect["points"])
                    xyxy.append([cls, x1, y1, x2, y2])
                label_write(label_path, xyxy, [img_h, img_w])


if __name__ == "__main__":
    # 类和索引
    CLASSES = ["spot", "frag"]

    json_dir = r"C:\Users\i\Desktop\WeiQiao"
    # print_classes(json_dir)
    json2txt(json_dir)



