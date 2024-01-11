# -*-coding:utf-8 -*-
# Author: Zenghui Tang
# Date: 2024/1/11
# Time: 9:25
import os
import re
IMG_FORMATS = [".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG", ".bmp", ".BMP"]


def walk_file(root_dir: str, sub_dir: str = "", suffixs="$|".join(IMG_FORMATS)+"$"):
    file_paths = []
    for dir_path, dir_names, file_names in os.walk(root_dir):
        if sub_dir and not re.search(sub_dir, dir_path):
            continue
        for file_name in file_names:
            if suffixs and not re.search(suffixs, file_name):
                continue
            file_paths.append(os.path.join(dir_path, file_name))
    return sorted(file_paths)


class CText(object):
    def __init__(self, path: str, is_clear: bool = False) -> None:
        self.path = path
        fp = open(path, 'a', encoding='utf-8')
        fp.close()
        if is_clear:
            self.clear()

    def clear(self) -> None:
        fp = open(self.path, 'r+', encoding='utf-8')
        fp.truncate()
        fp.close()

    def append(self, text: str) -> None:
        fp = open(self.path, 'a', encoding='utf-8')
        fp.write(text)
        fp.close()

    def read_lines(self, is_split: bool = False, sep: str = None):
        lines = []
        fp = open(self.path, encoding='utf-8')
        for item in fp.readlines():
            if is_split:
                lines.append(item.strip().split(sep))
            else:
                lines.append(item.strip())
        fp.close()
        return lines


def get_img_label_paths(root_dir):
    img_paths = walk_file(root_dir)
    label_paths = []
    for img_path in img_paths:
        img_dir, img_name = os.path.split(img_path)
        label_name = os.path.splitext(img_name)[0] + ".txt"
        label_path = os.path.join(img_dir, "Result", label_name)
        label_paths.append(label_path)
    return img_paths, label_paths


def paths2names(paths):
    names = [os.path.basename(path) for path in paths]
    return names


def rects2str(rects):
    content = ""
    for rect in rects:
        content += " ".join([str(v) for v in rect]) + '\n'
    return content


def get_save_path(img_path, suffix="ret"):
    img_dir, img_name = os.path.split(img_path)
    img_save_dir = img_dir + "_" + suffix
    label_save_dir = os.path.join(img_save_dir, "Result")
    os.makedirs(img_save_dir, exist_ok=True)
    os.makedirs(label_save_dir, exist_ok=True)
    img_save_path = os.path.join(img_save_dir, img_name)
    label_save_path = os.path.join(label_save_dir, os.path.splitext(img_name)[0] + ".txt")
    return img_save_path, label_save_path


def xywh2xyxy(rects, img_shape):
    rects_xyxy = []
    img_h, img_w = img_shape[:2]
    for rect in rects:
        cls, cx, cy, bw, bh = [float(v) for v in rect[:5]]
        x1 = max(0, int((cx - bw / 2.) * img_w))
        x2 = min(int((cx + bw / 2.) * img_w), img_w - 1)
        y1 = max(0, int((cy - bh / 2.) * img_h))
        y2 = min(int((cy + bh / 2.) * img_h), img_h - 1)
        rects_xyxy.append([int(cls), int(x1), int(y1), int(x2), int(y2)])
    return rects_xyxy


def xyxy2xywh(rects, img_shape):
    rects_xywh = []
    img_h, img_w = img_shape[:2]
    for rect in rects:
        cls, x1, y1, x2, y2 = [float(v) for v in rect[:5]]
        cx = (x2 + x1) / 2. / img_w  # 小数点很重要，去掉出错。
        cy = (y2 + y1) / 2. / img_h
        bw = (x2 - x1) / img_w
        bh = (y2 - y1) / img_h
        rects_xywh.append([int(cls), round(cx, 7), round(cy, 7), round(bw, 7), round(bh, 7)])
    return rects_xywh


def parsing_block_name(block_path):
    block_name = os.path.basename(block_path)
    block_key, suffix = os.path.splitext(block_name)
    img_key, cls, cx, cy, bw, bh = block_key.rsplit("_", 5)
    img_name = img_key + suffix
    return img_name, cls, cx, cy, bw, bh


if __name__ == "__main__":
    pass
