import cv2
import os
import glob

# 文件夹路径，你需要根据实际情况修改这些路径
original_images_dir = "/home/jiaqi/workspace/prj/Lane-Detection-with-ERFNet/datasets/PreliminaryData/testB"
binary_images_dir = "/home/jiaqi/workspace/prj/Lane-Detection-with-ERFNet/results/result"
output_dir = "/home/jiaqi/workspace/prj/Lane-Detection-with-ERFNet/overlayMaker"

# 获取所有的原图文件名
original_images_paths = glob.glob(os.path.join(original_images_dir, "*.jpg"))  # 如果你的图片格式不是jpg，需要修改这里

for original_image_path in original_images_paths:
    # 读取原图
    original_img = cv2.imread(original_image_path)

    # 根据原图的文件名，获取二值图像的路径
    binary_image_path = os.path.join(binary_images_dir, os.path.basename(original_image_path[:-4] + ".png"))
    # 读取二值图像
    binary_img = cv2.imread(binary_image_path, cv2.IMREAD_GRAYSCALE)  # 读取为灰度图

    # 将二值图像转换为三通道图像
    binary_img_color = cv2.cvtColor(binary_img, cv2.COLOR_GRAY2BGR)

    # 叠加图像
    overlay_img = cv2.addWeighted(original_img, 0.8, binary_img_color, 0.2, 0)

    # 保存叠加后的图像
    output_image_path = os.path.join(output_dir, os.path.basename(original_image_path))
    cv2.imwrite(output_image_path, overlay_img)