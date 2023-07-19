import paddle
from paddle.vision.transforms import Compose, Resize, Transpose, Normalize
import cv2
from PIL import Image
import models


def transform_image(img_path):
    transforms = Compose([
        Resize((224, 224)),
        Transpose(),
        Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], data_format='HWC')
    ])

    img = Image.open(img_path)
    img = transforms(img)
    img = paddle.to_tensor(img)
    img = img.unsqueeze(0)  # 添加batch维度
    return img

your_model = models.ERFNet(20, [576, 1024])
model = paddle.Model(your_model)  # 用你的模型替换your_model
model.load("trained/ERFNet_trained.pdparams")

img_path = 'test.jpg'  # 测试图像的路径
img = transform_image(img_path)

model.eval()
output = model(img)  # output应该是检测到的车道线的坐标


original_img = cv2.imread(img_path)
for line in output:
    cv2.line(original_img, tuple(line[0]), tuple(line[1]), (0, 255, 0), 2)  # 假设每条线由两个点定义，用绿色画线

cv2.imwrite('output.jpg', original_img)  # 保存图像

