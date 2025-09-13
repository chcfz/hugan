import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

def compare_images(img1, img2, threshold1=100, threshold2=200):
    """
    比较两张图片的线条相似性
    
    参数:
    image1_path: 第一张图片的路径
    image2_path: 第二张图片的路径
    threshold1: Canny边缘检测低阈值
    threshold2: Canny边缘检测高阈值
    
    返回:
    相似度分数 (0-1之间，1表示完全相同)
    """
    
    # 转换为灰度图
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # 使用Canny算法检测边缘
    edges1 = cv2.Canny(gray1, threshold1, threshold2)
    edges2 = cv2.Canny(gray2, threshold1, threshold2)
    
    # 计算结构相似性指数 (SSIM)
    score, _ = ssim(edges1, edges2, full=True)
    
    # 也可以使用其他比较方法，如计算重合度
    # intersection = np.logical_and(edges1, edges2)
    # union = np.logical_or(edges1, edges2)
    # iou_score = np.sum(intersection) / np.sum(union)
    #visualize_comparison(img1, img2, threshold1, threshold2)
    return score

def visualize_comparison(img1, img2, threshold1=100, threshold2=200):
    """
    可视化比较结果
    """
    # 读取图片
    
    # 转换为灰度图
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # 使用Canny算法检测边缘
    edges1 = cv2.Canny(gray1, threshold1, threshold2)
    edges2 = cv2.Canny(gray2, threshold1, threshold2)
    
    # 创建一个对比图像
    comparison = np.hstack((edges1, np.ones((edges1.shape[0], 10)), edges2))
    
    # 显示结果
    cv2.imshow('Edges Comparison', comparison)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return edges1, edges2

# 使用示例
if __name__ == "__main__":
    # 替换为您的图片路径
    image1_path = ".\pictures\home_1533_485_1605_833.png"
    image2_path = ".\pictures\home_1533_485_1605_833.png"
    
    # 比较图片
    similarity_score = compare_images(image1_path, image2_path)
    print(f"相似度得分: {similarity_score:.4f}")
    
    # 可视化比较
    edges1, edges2 = visualize_comparison(image1_path, image2_path)
    
    # 可以根据需要调整Canny算法的阈值
    # 对于更细致的边缘检测，可以降低阈值
    # similarity_score_adjusted = compare_images_lines(image1_path, image2_path, 50, 100)