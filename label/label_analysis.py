# -*-coding:utf-8 -*-
# Author: ZengHui Tang
# Date: 2022/12/6
# Time: 20:05
import os
import collections
from tqdm import tqdm
from tqdm.contrib import tzip
from utils.read_write import walk_file, CText, img_read
classes = ["人员", "摩托车", "三轮车", "小汽车", "小卡车", "大卡车", "施工机械", "罐车", "大客车", "农用车",
           "挖掘机", "推土机", "装载机", "桩机", "压路机", "渣土车", "皮卡车", "摩托车", "三轮车", "小汽车", "小卡车", "大卡车", "施工机械", "罐车", "大客车", "农用车",
           "挖掘机", "推土机", "装载机", "桩机", "压路机", "渣土车", "皮卡车"]


class DatasetAnalysis(object):
    def __init__(self, data_path, write_bg=False):
        self.data_path = data_path
        self.write_bg = write_bg
        self.img_paths, self.label_paths = self.get_img_label_paths()
        self.record()

    def get_img_label_paths(self):
        """
        data: dir or txt(img_path)
        """
        # get img_paths
        if os.path.isdir(self.data_path):  # dir
            img_paths = walk_file(self.data_path)
        elif os.path.isfile(self.data_path):  # .txt
            img_paths = CText(self.data_path).read_lines()
        else:
            raise FileNotFoundError(f'{self.data_path} does not exist')

        # get label_paths
        label_paths = []
        for img_path in img_paths:
            img_dir, img_name = os.path.split(img_path)
            label_paths.append(os.path.join(img_dir, "result", img_name.rsplit(".", 1)[0] + ".txt"))
        return img_paths, label_paths

    @property
    def get_save_path_head(self):
        save_path_head = self.data_path if os.path.isdir(self.data_path) else self.data_path.rsplit(".", 1)[0]
        return save_path_head

    def object_class_analysis(self):
        bg_paths = []
        per_cls_num = [0 for v in classes]
        per_cls_img_num = [0 for v in classes]
        for img_path, label_path in tzip(self.img_paths, self.label_paths):
            try:
                rects = CText(label_path).read_lines(is_split=True, sep=" ")
            except FileNotFoundError:  #
                bg_paths.append(img_path)
                continue
            except:
                continue
            if len(rects) < 1:
                bg_paths.append(img_path)
            occ_cls = [int(rect[0]) for rect in rects if rect[0] not in ["", " "]]
            # 按类别统计

            for cls in occ_cls:
                # if cls > 4:
                #     continue
                per_cls_num[cls] += 1
            # 按图像统计
            for s_cls in set(occ_cls):
                # if s_cls > 4:
                #     continue
                per_cls_img_num[s_cls] += 1
        return per_cls_num, per_cls_img_num, bg_paths

    def rect_size_analysis(self):
        """
        归一化后的宽高
        """
        pass

    def rect_local_analysis(self):
        """
        根据中心点统计
        """
        for label_path in tqdm(self.label_paths):
            pass

    def imgsz_analysis(self):
        shape = []
        for img_path in tqdm(self.img_paths):
            img = img_read(img_path)
            shape.append(img.shape[:2])
        return collections.Counter(shape)

    def record(self):
        f = CText(self.get_save_path_head + "_analysis_result.txt", is_clear=True)
        per_cls_num, per_cls_img_num, bg_paths = self.object_class_analysis()

        if self.write_bg:
            f.append("\n".join(bg_paths) + "\n")

        img_num = len(self.img_paths)
        bg_num = len(bg_paths)
        f.append(f"共有 {img_num} 张图像，其中背景图像{bg_num},背景占比{round(bg_num/img_num * 100, 2)}%\n\n\n")

        f.append("按类别统计结果(某类别有多少个)：" + "\n")
        for i, cls in enumerate(classes):
            f.append(str(i) + "\t\t" + cls + "\t\t" + str(per_cls_num[i]) + "\n")
        f.append("\n\n\n")

        f.append("按图像统计结果(某类别在多少张图像中出现)：" + "\n")
        for i, cls in enumerate(classes):
            f.append(str(i) + "\t\t" + cls + "\t\t" + str(per_cls_img_num[i]) + "\n")
        f.append("\n\n\n")

        # f.append("图像尺寸统计结果：" + "\n")
        # for sz, num in self.imgsz_analysis().items():
        #     f.append(str(sz) + "\t\t" + str(num) + "\n")


if __name__ == "__main__":
    da = DatasetAnalysis(r"F:\014_YouQiHongWai_engcar\raw_engcar_rotate_copy_bg_engcar_rotate_copy", write_bg=False)

