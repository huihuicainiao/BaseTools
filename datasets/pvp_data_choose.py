# -*-coding:utf-8 -*-
# Author: Zenghui Tang
# Date: 2023/4/23
# Time: 17:27
"""
1、编号：n[01, 02, 03]
2、场景：平地光伏（G: ground）；水面光伏（W: water）；屋顶光伏(R: roof)；山地光伏(M: mountain)；
3、样式：[S, D, Q, M, O]分别代表【单排（S：single），双排（D: double），四排（Q: quadruple），多排（M：multi row）; 其他（O: other）
4、间隙：紧凑（T: tight）；松散(L: loose)
5、说明：正常（N: norm）;背景（G：background）; 接线盒（J: Junction box）;亮（B：bright）;暗（D: dark）;模糊（F: fuzzy）；阴影（S: shadow） 飞行高度过高（H: height）组件中间有黑色线条（L：line）可组合，其他异常（A: abnormal）。
例：
n01_G_S_T_J 具有接线盒的单排紧凑型平地光伏。
n01_0_0_0_G  因为背景不存在样式，因此用0补位。
"""
import os
import re
import shutil
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


def get_img_label_paths(root_dir):
    img_paths = walk_file(root_dir)
    label_paths = []
    for img_path in img_paths:
        img_dir, img_name = os.path.split(img_path)
        label_name = os.path.splitext(img_name)[0] + ".txt"
        label_path = os.path.join(img_dir, "Result", label_name)
        label_paths.append(label_path)
    return img_paths, label_paths


class PVPDataChoose(object):
    def __init__(self, datasets_path):
        self.img_paths, self.label_paths = get_img_label_paths(datasets_path)

    @staticmethod
    def path_parse(img_path):
        dir_name = os.path.basename(os.path.dirname(img_path))
        _, scene, style, distance, explanation = dir_name.split("_")
        return scene, style, distance, explanation

    def copy_label(self):
        for old_label_path in self.label_paths:
            if not os.path.exists(old_label_path):
                CText(old_label_path)
            old_label_dir, old_label_name = os.path.split(old_label_path)
            new_label_path = os.path.join(os.path.dirname(old_label_dir), old_label_name)
            shutil.copyfile(old_label_path, new_label_path)

    def choose(self, txt_path=r"./pvp_datasets.txt"):
        ret_paths = []
        for img_path in self.img_paths:
            if os.path.basename(os.path.dirname(img_path)).count("_") != 4:
                continue
            is_choose = False
            scene, style, distance, explanation = self.path_parse(img_path)
            # G: 平地光伏, W: 水面光伏, R: 屋顶光伏, M: 山地光伏
            # S：单排, D: 双排, Q: 四排, M：多排, O: 其他
            # T: 紧密, L: 疏松
            # N: 正常, G：背景, J: 接线盒, B：亮, D: 暗, F: 模糊, S: 阴影, H: 太高, L：线条, A: 其他异常
            if (scene in ["G", "R"]) and (style in ["D", "Q", "M"]) and (distance in ["T"]):
                for c in explanation:
                    if (c in ["N"]) and (c not in ["J", "F", "S", "H", "L", "A"]):
                        is_choose = True
            if is_choose:
                ret_paths.append(img_path)
        if len(ret_paths):
            CText(txt_path).append("\n".join(ret_paths) + "\n")


if __name__ == "__main__":
    pvp = PVPDataChoose(r"/mnt/data/datasets/002_PVPDatasets")
    # pvp.copy_label()
    pvp.choose()
