# -*-coding:utf-8 -*-
# Date: 2023/1/5
# Time: 11:16
import os
import cv2
import numpy as np
from utils.common import xywh2xyxy, xyxy2xywh, rects2str
from utils.common import CText


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


def img_write(img_path, img, ratio=None, is_mkdir=True):
    """
        .png为无损压缩，.jpg为有损压缩，添加中文支持
    """
    if is_mkdir and not os.path.exists(os.path.dirname(img_path)):
        try:
            os.makedirs(os.path.dirname(img_path), exist_ok=True)
        except Exception as err:
            print("error:", img_path, err)

    suffix = os.path.splitext(img_path)[1]
    if suffix in [".png", ".PNG"]:
        ratio = ratio if ratio is not None else 0
        # 取值范围：0~9，数值越小，压缩比越低，图片质量越高
        assert 0 <= ratio <= 9, "ratio should in 0~9"
        params = [cv2.IMWRITE_PNG_COMPRESSION, ratio]  # ratio: 0~9
    elif suffix in [".jpg", ".JPG"]:
        ratio = ratio if ratio is not None else 100
        # 取值范围：0~100，数值越小，压缩比越高，图片质量损失越严重
        assert 0 <= ratio <= 100, "ratio should in 0~100"
        params = [cv2.IMWRITE_JPEG_QUALITY, ratio]  # ratio:0~100
    else:
        raise ValueError(f"{suffix} not support compress.")

    # cv2.imwrite(img_path, img, params)
    try:
        cv2.imencode(suffix, img, params)[1].tofile(img_path)
    except Exception as err:
        print("error:", img_path, err)


def label_read(file_path, img_shape=None):
    if not os.path.exists(file_path):
        return []

    rects = CText(file_path).read_lines(is_split=True, sep=" ")
    if img_shape is None:
        rects_xywh = []
        for rect in rects:
            rects_xywh.append([float(v) if i > 0 else int(v) for i, v in enumerate(rect[:7])])
        return rects_xywh
    else:
        rects_xyxy = xywh2xyxy(rects, img_shape=img_shape)
        return rects_xyxy


def label_write(file_path, rects, img_shape=None, is_mkdir=True):
    if is_mkdir and not os.path.exists(os.path.dirname(file_path)):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        except Exception as err:
            print("error:", file_path, err)
    if img_shape is not None:
        rects = xyxy2xywh(rects, img_shape)
    content = rects2str(rects)
    CText(file_path, is_clear=True).append(content)


