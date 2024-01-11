# -*-coding:utf-8 -*-
# Author: ZengHui Tang
# Date: 2022/12/7
# Time: 10:09
import os
import cv2
import copy
import numpy as np
import matplotlib.pyplot as plt


def draw_detect_boxes(img, labels, cmaps=None, label_names=None,
                      fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL,
                      fontScale=1.2, thickness=2, is_cut=False):
    """ yolo boxes
        img = cv2.imread("dog.jpg")
        ret = draw_detect_boxes(img, np.array([[0, 100, 100, 400, 400]]), [[0, 255, 255]], ["cat asda"])
        cv2.imwrite("dog111.jpg", ret)
    """

    image = copy.deepcopy(img)
    img_h, img_w = image.shape[:2]
    for idx, label in enumerate(labels):
        # print(label)
        [cls, x1, y1, x2, y2] = label[:5]
        cls_color = cmaps[int(cls)]
        print(x1, y1, x2, y2)
        image = cv2.rectangle(image, (x1, y1), (x2, y2), cls_color, thickness=thickness)

        try:
            obj_name = label_names[cls]
        except:
            obj_name = "%d" % cls

        # print("obj_name:", obj_name)
        # cv2.getTextSize(obj_name, cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.2, 2)
        (tw, th), _ = cv2.getTextSize(obj_name, fontFace, fontScale, thickness)

        if is_cut:
            is_cut = False
            while tw > x2 - x1:
                obj_name = obj_name[:int(len(obj_name) * 0.9)]
                (tw, th), _ = cv2.getTextSize(obj_name, fontFace, fontScale, thickness)
                is_cut = True
        is_cut = False
        if is_cut:
            obj_name += "..."
            (tw, th), _ = cv2.getTextSize(obj_name, fontFace, fontScale, thickness)

        th += 4
        image = cv2.rectangle(image, (max(x1 - thickness // 2, 0), max(y1 - th, 0)),
                              (min(img_w, x2 + thickness // 2), y1),
                              cls_color, thickness=cv2.FILLED)
        # 将中文标注框高度固定，长度与检测框宽度一致，中文字体大小固定
        image = cv2.rectangle(image, (x1, y1-20), (x2, y1), cls_color, thickness=cv2.FILLED)
        # obj_name = "工程机械_挖掘机"
        image = put_text_ex(image, obj_name, (x1, max(y1 - 20, 0)), color=(255, 255, 255))
        # image = cv2.putText(image, obj_name, (x1, max(y1 - 2, 0)), cv2.FONT_HERSHEY_COMPLEX_SMALL,
        #                     color=(0, 0, 0), fontScale=fontScale * 1.0, thickness=thickness)
    return image


def put_text_ex(img, txt, loc, fount=20, color=(255, 0, 0)):
    """
    写中文
    NotoSansCJK.ttc下载地址：
    链接：https://pan.baidu.com/s/1cDM45oycD_ciCCd23HAqBA
    提取码：xudy
    """
    from PIL import Image, ImageDraw, ImageFont
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    font = ImageFont.truetype(os.path.join(r"C:\Windows\Fonts", "simhei.ttf"), fount)
    if isinstance(txt, str):
        txt.encode('gb2312')
    draw = ImageDraw.Draw(pil)
    draw.text(loc, txt, font=font, fill=color)

    # plt.imshow(cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR))
    # plt.show()

    return cv2.cvtColor(np.asarray(pil), cv2.COLOR_RGB2BGR)


if __name__ == "__main__":

    data = []
    # test2_2.txt中的位置信息只保留了整数位，小数位在从txt写入list后测试报错
    with open(r'C:\Users\i\Desktop\a\Result\16899347018444.txt') as f:
        for line in f.readlines():
            temp = line.split()
            temp1 = []
            for num in temp:
                temp1.append(int(num))  # ValueError: invalid literal for int() with base 10: '979.7073170731707'
            print(temp1)
            data.append(temp1)

    img = cv2.imread(r'C:\Users\i\Desktop\a\16899347018444.png')
    # ret = draw_detect_boxes(img, [loc], cmaps=[[0,0,255]], label_names=[ "人", "货车", '小汽车','三轮车'])
    ret = draw_detect_boxes(img, data, cmaps=[[0, 0, 255],[0, 255, 0],[255, 0, 0],[40, 35, 25]], label_names=["人", "货车", '小汽车', '三轮车'])

    plt.imshow(ret)
    plt.show()
