#!/usr/bin/env python
# coding: utf-8
"""
v1.1 修正了v1.0无法处理 - 副本 的问题。
"""
import copy
import os
import re
import cv2
import time
import shutil
import argparse
import numpy as np

classes = {0: "人员", 1: "自行车/摩托车", 2: "三轮车", 3: "小汽车", 4: "小卡车", 5: "大卡车",
           6: "施工机械", 7: "罐车", 8: "客车", 9: "农用车", 10: "挖掘机", 11: "推土机",
           12: "装载机", 13: "桩机", 14: "压路机", 15: "渣土车", 16: "皮卡车"}


def walk_file(dir: str, sub_dir: str = "", _filter: str = ""):
    file_paths = []
    for dirpath, dirnames, filenames in os.walk(dir):
        if sub_dir and not re.search(sub_dir, dirpath):
            continue
        for filename in filenames:
            if _filter and not re.search(_filter, filename):
                continue
            file_paths.append(os.path.join(dirpath, filename))
    return file_paths


class CText(object):
    def __init__(self, path: str, is_clear: bool = False) -> None:
        self.path = path
        fp = open(path, 'a')  # 无则创建，有则打开
        fp.close()
        if is_clear:
            self.clear()

    def clear(self) -> None:
        fp = open(self.path, 'r+')
        fp.truncate()
        fp.close()

    def append(self, text: str) -> None:
        fp = open(self.path, 'a')
        fp.write(text)
        fp.close()

    def read_lines(self, is_split: bool = False, sep: str = None):
        lines = []
        fp = open(self.path)
        for item in fp.readlines():
            if is_split:
                lines.append(item.strip().split(sep))
            else:
                lines.append(item.strip())
        fp.close()
        return lines


def xywh2xyxy(rect, img_shape):
    img_h, img_w, _ = img_shape

    [cls, cx, cy, bw, bh] = rect
    cx = int(float(cx) * img_w)
    bw = int(float(bw) * img_w)
    cy = int(float(cy) * img_h)
    bh = int(float(bh) * img_h)

    x1 = max(int(cx - bw / 2), 0)
    x2 = min(int(cx + bw / 2), img_w)
    y1 = max(int(cy - bh / 2), 0)
    y2 = min(int(cy + bh / 2), img_h)
    return [cls, x1, y1, x2, y2]


def draw_rect(img, rects):
    for rgn in rects:
        if len(rgn) == 0:
            continue
        cls, x1, y1, x2, y2 = xywh2xyxy(rgn, img.shape)
        img = cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), thickness=1)
    return img


def remove_abnormal(rects):
    for rect in reversed(rects):
        if "副本" in rect[-1]:
            rects.remove(rect)
    return rects


def img_read(file_path, flags=cv2.IMREAD_UNCHANGED):
    """
    flags: cv2.IMREAD_COLOR（flags=1);
           cv2.IMREAD_GRAYSCALE(flags=0)
           cv2.IMREAD_UNCHANGED(flags=-1)
    """
    if not os.path.exists(file_path):
        return None
    try:
        img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), flags=flags)
    # except Exception as err:
    except:
        img = None
        print("img_read error:")
    return img


def gen_block():
    """
    依据标签生成对应类别文件夹，图像block保存至对应目录.
    """
    if os.path.exists(ret_dir):
        backup = input("is need backup the previous cls images? yes/no\n")
        while True:
            if backup in ["yes", "y", "no", "n"]:
                break
            else:
                backup = input("input yes or no.\n")

        if backup in ["yes", "y"]:
            for i in range(100):
                back_dir = os.path.join(ret_dir + ("_%03d" % (i + 1)))
                if not os.path.exists(back_dir):
                    print("start backup images...")
                    print("back_dir dir is:", back_dir)
                    shutil.copytree(ret_dir, back_dir)
                    print("end backup.")
                    break

        shutil.rmtree(ret_dir, ignore_errors=True)

    for key in classes.keys():
        os.makedirs(os.path.join(ret_dir, str(key)), exist_ok=True)

    file_paths = walk_file(data_dir)
    for idx, file_path in enumerate(file_paths):
        print(idx, file_path)
        key = os.path.splitext(os.path.basename(file_path))[0]
        text_path = os.path.join(data_dir, "Result", key + ".txt")
        if not os.path.exists(text_path):
            continue
        rgns = CText(text_path).read_lines(is_split=True)
        rgns = remove_abnormal(rgns)
        img = img_read(file_path)
        if img is None:
            continue
        img = draw_rect(img, rgns)
        for i, rgn in enumerate(rgns):
            if len(rgn) == 0:
                continue
            cls, x1, y1, x2, y2 = xywh2xyxy(rgn, img.shape)
            bw, bh = x2 - x1, y2 - y1
            tx1 = max(int(x1 - max(40., bw * 0.3)), 0)
            tx2 = min(int(x2 + max(40., bw * 0.3)), img.shape[1])
            ty1 = max(int(y1 - max(40., bh * 0.3)), 0)
            ty2 = min(int(y2 + max(40., bh * 0.3)), img.shape[0])
            cls_dir = os.path.join(ret_dir, cls)
            os.makedirs(cls_dir, exist_ok=True)

            block = copy.deepcopy(img[ty1:ty2, tx1:tx2, :])
            org_x1, org_y1 = int(x1 - tx1), int(y1 - ty1)
            block = cv2.rectangle(block, (org_x1, org_y1), (org_x1+bw, org_y1+bh), (0, 0, 255), thickness=2)

            # 添加图片名称
            [cls, x0, y0, w0, h0] = rgn
            block_name = os.path.join(cls_dir, "%s_%s_%s_%s_%s_%s.jpg" % (key, cls, x0, y0, w0, h0))
            try:
                h1, w1, _ = block.shape
                block = cv2.resize(block, (w1 * 2, h1 * 2))
                cv2.imencode('.jpg', block, params=[cv2.IMWRITE_JPEG_QUALITY, 90])[1].tofile(block_name)
            except Exception as err:
                print("err:", err)


def update_cls():
    """
    依据图像块目录，保存更新类别.
    """

    file_paths = walk_file(ret_dir)
    print("total block nums:", len(file_paths))
    if len(file_paths) == 0:
        return

    block_dict = {}
    for idx, file_path in enumerate(file_paths):
        key_name = os.path.splitext(os.path.basename(file_path))[0]
        block_dict[key_name] = os.path.basename(os.path.dirname(file_path))  # key_name: cls

    label_dir = os.path.join(data_dir, "Result")
    if not os.path.exists(label_dir):
        print("label result dir 'Result' not exists.")
        exit(0)

    # backup = input("is need backup the previous Result file? yes/no\n")
    backup = "n"
    while True:
        if backup in ["yes", "y", "no", "n"]:
            break
        else:
            backup = input("input yes or no.\n")
    if backup in ["yes", "y"]:
        for i in range(100):
            back_dir = os.path.join(label_dir + ("_back_%03d" % (i + 1)))
            if not os.path.exists(back_dir):
                print("start backup images...")
                print("back_dir dir is:", back_dir)
                shutil.copytree(label_dir, back_dir)
                print("end backup.")
                if i > 0:
                    shutil.rmtree(label_dir, ignore_errors=True)  # 第二次备份删除空文件标记。
                break

    os.makedirs(label_dir, exist_ok=True)
    file_paths = walk_file(data_dir)
    for idx, file_path in enumerate(file_paths):
        print(idx, file_path)
        key = os.path.splitext(os.path.basename(file_path))[0]
        text_path = os.path.join(label_dir, key + ".txt")

        rgns = []
        for k in block_dict.keys():
            if not k.startswith(key + "_"):
                continue
            [_, x0, y0, w0, h0] = k.split("_")[-5:]
            cls = block_dict[k]
            rgns.append([cls, x0, y0, w0, h0])

        if len(rgns) == 0:
            continue
        rgns = remove_abnormal(rgns)
        cfile = CText(text_path, is_clear=True)
        for rgn in rgns:
            if len(rgn) == 0:
                continue
            [cls, x0, y0, w0, h0] = rgn
            cfile.append("%s %s %s %s %s\n" % (cls, x0, y0, w0, h0))


def argv_parse():
    parser = argparse.ArgumentParser(usage="it is use for start semantic segmentation sever.",
                                     description="change detect demo.")
    parser.add_argument("--data_dir", default=r"C:\Users\i\Desktop\fsdownload\langfang_error_03", type=str, help="label img dir name.")
    return parser.parse_args()


def main():
    while True:
        print("Enter the index to select command:")
        print("1.gen_block();\n"
              "2.update_cls();\n"
              "3.exit().")
        select = input()
        while select not in ["1", "2", "3"]:
            print("please input index in '1,2,3'")
        if int(select) == 1:
            print("run gen_block().")
            gen_block()
        elif int(select) == 2:
            print("run update_cls().")
            update_cls()
        else:
            break


if __name__ == '__main__':
    start = time.time()
    # try:
    arg = argv_parse()
    print("\narg:\n", arg)

    data_dir = arg.data_dir
    ret_dir = data_dir + "_cls"
    main()
    pass
    # except Exception as err:
    #     print("err:", err)

    end = time.time()
    print("total time is %.3fs." % float(end - start))
    pass
