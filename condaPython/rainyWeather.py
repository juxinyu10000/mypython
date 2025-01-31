import cv2
import numpy as np
import os


def get_noise(img, value=2):
    """
    #生成噪声图像
    输入： img图像
    value： 大小控制雨滴的多少
    返回图像大小的模糊噪声图像
    """
    noise = np.random.uniform(0, 256, img.shape[0:2])  # 控制噪声水平，取浮点数，只保留最大的一部分作为噪声
    v = value * 0.01
    noise[np.where(noise < (256 - v))] = 0  # 噪声做初次模糊
    k = np.array([[0, 0.1, 0], [0.1, 8, 0.1], [0, 0.1, 0]])
    noise = cv2.filter2D(noise, -1, k)  # 可以输出噪声看看
    # cv2.imshow('img', noise)  # 查看输出的噪声图片
    # cv2.waitKey()
    # cv2.destroyWindow('img')
    return noise


def rain_blur(noise, length=10, angle=15, w=3):
    """将噪声加上运动模糊,模仿雨滴>>>
    输入noise：输入噪声图，shape = img.shape[0:2]
    length: 对角矩阵大小，表示雨滴的长度
    angle： 倾斜的角度，逆时针为正
    w:      雨滴大小
    输出带模糊的噪声
    """
    # 这里由于对角阵自带45度的倾斜，逆时针为正，所以加了-45度的误差，保证开始为正
    trans = cv2.getRotationMatrix2D((length / 2, length / 2), angle - 45, 1 - length / 100.0)
    dig = np.diag(np.ones(length))  # 生成对焦矩阵
    k = cv2.warpAffine(dig, trans, (length, length))  # 生成模糊核
    k = cv2.GaussianBlur(k, (w, w), 0)  # 高斯模糊这个旋转后的对角核，使得雨有宽度#
    k = k / length  # 是否归一化
    blurred = cv2.filter2D(noise, -1, k)  # 用刚刚得到的旋转后的核，进行滤波#转换到0-255区间
    cv2.normalize(blurred, blurred, 0, 255, cv2.NORM_MINMAX)
    blurred = np.array(blurred, dtype=np.uint8)

    # cv2.imshow('img', blurred)
    # cv2.waitKey()
    # cv2.destroyWindow('img')

    return blurred


##第一种将原始图像和噪声雨点叠加
def alpha_rain(rain, img, beta=0.8):
    # 输入雨滴噪声和图像
    # beta = 0.8   #results weight
    # 显示下雨效果

    # expand dimensin
    # 将二维雨噪声扩张为三维单通道
    # 并与图像合成在一起形成带有alpha通道的4通道图像
    rain = np.expand_dims(rain, 2)
    rain_effect = np.concatenate((img, rain), axis=2)  # add alpha channel

    rain_result = rain_effect.copy()  # 拷贝一个掩膜
    rain = np.array(rain, dtype=np.float32)  # 数据类型变为浮点数，后面要叠加，防止数组越界要用32位
    rain_result[:, :, 0] = rain_result[:, :, 0] * (255 - rain[:, :, 0]) / 255.0 + beta * rain[:, :, 0]
    rain_result[:, :, 1] = rain_result[:, :, 1] * (255 - rain[:, :, 0]) / 255 + beta * rain[:, :, 0]
    rain_result[:, :, 2] = rain_result[:, :, 2] * (255 - rain[:, :, 0]) / 255 + beta * rain[:, :, 0]
    # 对每个通道先保留雨滴噪声图对应的黑色（透明）部分，再叠加白色的雨滴噪声部分（有比例因子）

    cv2.imshow('rain_effct_result', rain_result)
    cv2.waitKey()
    cv2.destroyAllWindows()


###第二种方式就是利用图像加权的方法，将雨滴图叠加到原图上。由于背景是黑色，所以调整后的图像亮度会下降，在某些场景下更适合雨天的模拟（乌云，光线暗）
def add_rain(rain, img, alpha=0.8):
    # 输入雨滴噪声和图像
    # alpha：原图比例因子,调整该参数可降低或升高光线，模拟下雨光线暗场景
    # 显示下雨效果
    # 返回叠加下雨效果后的图片
    rain = np.expand_dims(rain, 2)
    rain = np.repeat(rain, 3, 2)

    # 加权合成新图
    rainPic = cv2.addWeighted(img, alpha, rain, 1 - alpha, 1)
    # cv2.imshow('rain_effct', result)
    # cv2.waitKey()
    # cv2.destroyWindow('rain_effct')
    return rainPic



Output_dir = r".\image\qita\rain"  # 修改后图片保存路径
image_path = r".\image\qita"
picName = "chuyu_fu_"
n = 1

for image in os.listdir(image_path):
    if image[-4:] == ".jpg":

        image_path1 = os.path.join(image_path, image)
        print(image_path1)
        img = cv2.imread(image_path1)
        noise = get_noise(img, 10)
        rain = rain_blur(noise)
        #alpha_rain(rain, img)
        rainPic = add_rain(rain, img)
        cv2.imwrite(os.path.join(Output_dir,picName+str(n)+".jpg"),rainPic)
        n = n + 1

