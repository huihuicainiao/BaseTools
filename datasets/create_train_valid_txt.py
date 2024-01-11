# -*-coding:utf-8 -*-
# Date: 2022/8/3
# Time: 9:17
import os
import re
import random
IMG_FORMAT = [".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG", ".bmp", ".BMP"]


def walk_file(root_dir: str, sub_dir: str = "", suffixs="$|".join(IMG_FORMAT)+"$"):
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


def split_trainval(data_list, ratio=0.2, is_split=False):
    for data_path in data_list:
        print(data_path)
        lines = walk_file(data_path)
        #lines = CText(data_path).read_lines()
        if is_split:
            random.shuffle(lines)
            train = lines[int(ratio * len(lines)):]
            valid = lines[:int(ratio * len(lines))]
            CText("./pvp_v4_tiny_train.txt").append("\n".join(train) + "\n")
            CText("./pvp_v4_tiny_valid.txt").append("\n".join(valid) + "\n")
        else:
            CText("./train.txt").append("\n".join(lines) + "\n")


if __name__ == "__main__":
    data_list = [
    "/mnt/data/datasets/hongwai_0705"
    ]
    split_trainval(data_list, ratio=0.1, is_split=True)
