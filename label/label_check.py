# -*-coding:utf-8 -*-
# Date: 2022/8/2
# Time: 15:21
"""
1、根据图片名称寻找标签文件，找不到则新建空的同名txt文件。
2、遍历标签文件，对于超出边界的标签进行修正。
3、标签保留6位有效数字
"""
import os
import re
import shutil
from tqdm import tqdm
from utils.common import CText, walk_file, get_img_label_paths


class LabelCorrect(object):
    def __init__(self, data_dir, is_result=False):
        self.data_dir = data_dir
        self.img_paths, self.label_paths = get_img_label_paths(data_dir)

    def del_blank_line(self):
        for label_path in self.label_paths:
            new_line = []
            try:
                label = CText(label_path).read_lines()
            except:
                print(label_path)
                continue
            for line in label:
                if len(line.strip()):
                    new_line.append(line)
            CText(label_path, is_clear=True).append(("\n".join(new_line) + "\n") if len(new_line) else "")
        pass

    def out_correct(self):
        """
        1.标签出界修正。
        2.空白标签填充。
        """
        out_correct_bar = tqdm(self.label_paths)
        for label_path in out_correct_bar:
            out_correct_bar.set_description("标签出界修正")
            # 检查标签是否出界
            is_out = False
            new_label = []
            label = CText(label_path).read_lines(is_split=True, sep=" ")
            for i, rect in enumerate(label):
                # np.clip(ret[1:5], 0, 1)
                for j in range(1, 5):
                    try:
                        if eval(rect[j]) < 0:
                            rect[j] = str(0)
                            is_out = True
                            print("标签文件：{}中第{}行第{}列数据超出边界".format(label_path, i+1, j+1))
                        if eval(rect[j]) > 1:
                            rect[j] = str(1)
                            is_out = True
                            print("标签文件：{}中第{}行第{}列数据超出边界".format(label_path, i+1, j+1))
                    except:
                        print("2", label_path)
                new_label.append(" ".join(rect))
            # 如果存在标签出界，对标签文件重新写
            if is_out:
                CText(label_path, is_clear=True).append("\n".join(new_label))

    def remove_lonely_labels(self):
        label_paths = []
        for dir_path, _, _ in os.walk(self.data_dir):
            if re.search("Result", dir_path):
                label_paths += walk_file(dir_path, suffixs=".txt$")

        remove_lonely_labels_bar = tqdm(label_paths)
        for label_path in remove_lonely_labels_bar:
            remove_lonely_labels_bar.set_description("删除多余标签")
            if label_path not in self.label_paths:
                os.unlink(label_path)

    def remove_config(self):
        for dir_path, dir_names, _ in os.walk(self.data_dir):
            if re.search("Config", dir_path):
                print(dir_path)
                shutil.rmtree(dir_path)

    def copy_labels_to_imgdir(self):
        copy_labels_bar = tqdm(self.label_paths)
        for label_path in copy_labels_bar:
            copy_labels_bar.set_description("复制标签文件")
            img_dir = os.path.dirname(os.path.dirname(label_path))
            label_name = os.path.basename(label_path)
            shutil.copyfile(label_path, os.path.join(img_dir, label_name))


if __name__ == "__main__":
    for i in range(1):
        lc = LabelCorrect(data_dir=r"C:\Users\i\Desktop\WeiQiao\hongwai_1", is_result=True)
        lc.del_blank_line()
        lc.out_correct()
        lc.remove_lonely_labels()
        lc.remove_config()
