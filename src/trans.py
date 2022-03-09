from paddleocr import PaddleOCR
import uuid
import os
from PIL import Image

def process(path,dict):
    ocr = PaddleOCR(det_model_dir = './model/det/', # 检测模型所在文件夹
                rec_model_dir = './model/rec/', # 识别模型所在文件夹。
                cls_model_dir = './model/cls/',
                use_angle_cls=True, lang="ch")
    result = ocr.ocr(path, cls=True)
    temp = ''
    res = []
    tempStack = []
    im = Image.open(path)

    for line in result:
        content = line[1][0]
        if content[0:2] != "等级":
            temp+=content
            tempStack.append([(line[0][0][0], line[0][0][1], line[0][1][0], line[0][2][1]),content])
        else:
            if temp not in dict:
                for item in tempStack:
                    region = im.crop(item[0])
                    id = str(uuid.uuid4())
                    region.save('./data/' + id + '.jpg')
                    with open('train.txt', 'a') as out:
                        out.write("'" + id + '.jpg' + "'" + ', ' + item[1] + '\n')
            else:
                res.append([temp,content[2:4]])
            tempStack.clear()
            temp = ''
    im.close()
    os.remove(path)
    return res



