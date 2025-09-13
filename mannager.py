import re
from mumucontroller import MuMuController
from piccheck import compare_images
from time import sleep
from PIL import ImageGrab, Image
import numpy as np
import os
import time
def load_pic(path):
    """
    加载图片并转换为RGB数组
    """
    info = os.path.basename(path)[:-4].split("_")
    top_x, top_y, bottom_x, bottom_y = map(int, info[1:])
    return [np.array(Image.open(path).convert('RGB')),[top_x, top_y, bottom_x, bottom_y]]


class Manager:
    def __init__(self):
        self.win_controller = MuMuController()
        self.original_pic_data = {}
        self.dict_key = {}
        self.loadpicinfo("pictures")
        self.loadkeyinfo("key_xy.txt")
        self.has_connected = False
        
    def connect(self, title):
        if self.win_controller.connect(title):
            self.has_connected = True
            return True
        return False


    def click(self, x, y):
        self.win_controller.click(x, y)

    def press(self, key, times=1):
        key_x, key_y = self.dict_key[key]
        for i in range(times):
            self.click(key_x, key_y)
            self.wait(0.05)
    # def press(self, key, times=1):
    #     for i in range(times):
    #         self.win_controller.press_key(key)
    #         self.wait(0.05)

    def wait(self, seconds):
        sleep(seconds)

    def grab(self,x_top, y_top, x_bottom, y_bottom):
        region = (
            self.win_controller.window_left + x_top,
            self.win_controller.window_top + y_top,
            self.win_controller.window_left + x_bottom,
            self.win_controller.window_top + y_bottom,
        )

        # 截图
        return ImageGrab.grab(bbox=region)
    def picmath(self, name, threshold=0.8):
        original_pic_data = self.original_pic_data[name][0]
        original_pic_location = self.original_pic_data[name][1]

        grap_pic = self.grab(original_pic_location[0], original_pic_location[1], original_pic_location[2], original_pic_location[3])
        grap_pic = np.array(grap_pic.convert('RGB'))

            # 计算绝对差异
        score = compare_images(original_pic_data, grap_pic)

        # 判断是否在阈值范围内
        return score >= threshold
    
    def loadpicinfo(self, path):
        #递归遍历目录下所有png图片
        name_pattern = re.compile('(\w+)_(\d+)_(\d+)_(\d+)_(\d+).png')
        for root, dirs, files in os.walk(path):
            for file in files:
                math_obj = name_pattern.match(file)
                if math_obj:
                    #print(os.path.join(root, file))

                    name = math_obj.group(1)
                    top_x = int(math_obj.group(2))
                    top_y = int(math_obj.group(3))
                    bottom_x = int(math_obj.group(4))
                    bottom_y = int(math_obj.group(5))
                    if name in self.original_pic_data:
                        print(f"图片 {name} 已存在，跳过加载")
                    else:
                        file_path = os.path.join(root, file)
                        self.original_pic_data[name] = [np.array(Image.open(file_path).convert('RGB')),[top_x, top_y, bottom_x, bottom_y]]

    def loadkeyinfo(self, path):
        key_pattern = re.compile(r"(\w+):\((\d+), (\d+)\),?")
        with open(path, 'r') as f:
            for line in f:
                math_obj = key_pattern.match(line.strip())
                if math_obj:
                    key = math_obj.group(1)
                    x = int(math_obj.group(2))
                    y = int(math_obj.group(3))
                    self.dict_key[key] = (x, y)
                else:
                    print(f"无法解析行: {line.strip()}")

#执行一段时间
def run_duration(func, hours, mins = 0, secs = 0):
    total_seconds = hours * 3600 + mins * 60 + secs
    end_time = time.time() + total_seconds
    while time.time() < end_time:
        func()



if __name__ == "__main__":
    manager = Manager()
    manager.connect("部落冲突 - MuMu安卓设备")  # 修改为你的游戏窗口标题
    manager.loadpicinfo("pictures")
    manager.loadkeyinfo("key_xy.txt")




    #Xij = 798 - 12i + 12j
    #Yij = 143 -10i -10j
    #i \in [0,22] j \in [0, 12]

    
    # def update_wall(manager, XY,lastxy_i, source="G"):
    #     for i in range(lastxy_i, len(XY)):
    #         manager.click(XY[i][0], XY[i][1])
    #         manager.wait(1)
    #         if manager.picmath("wall"):
    #             manager.press("K", 5)
    #             manager.wait(0.5)
    #             # while manager.picmath("update"):
    #             #     manager.press("K")
    #             #     manager.wait(0.5)
    #             manager.press(source)
    #             manager.wait(0.5)
    #             manager.press("B")
    #             return i+1
    #     return -1

    # XY = []
    # for i in range(15):
    #     for j in range(15):
    #         XY.append((798 + 12*i - 12*j, 143 + 10*i + 10*j))
    # #print(XY)
    # print("开始执行")
    # lastxu_i = 0
    # def task():
    #     global lastxu_i
    #     global XY
    #     while not manager.picmath("home"):
    #         manager.wait(2)
    #         manager.press("D")

    #     if manager.picmath("gold"):
    #         print("有金")
    #         lastxu_i = update_wall(manager, XY, lastxu_i, "G")

    #     if manager.picmath("water"):
    #         print("有水")
    #         lastxu_i = update_wall(manager, XY, lastxu_i, "H")

    #     if lastxu_i == -1:
    #         exit(0)
    #     while not manager.picmath("home"):
    #         manager.wait(2)
            
    #     manager.press("Z")
    #     manager.wait(0.5)
    #     manager.press("C")
    #     manager.wait(0.5)
    #     manager.press("B")
    #     manager.wait(0.5)
    #     manager.press("0")
    #     manager.wait(0.5)
    #     manager.press("B")
    #     manager.wait(0.5)

    #     while not manager.picmath("ready"):
    #         manager.wait(2)

    #     manager.press("3")
    #     manager.wait(0.05)
    #     manager.press("X")
    #     manager.wait(0.05)

    #     manager.press("7")
    #     manager.wait(0.05)
    #     manager.press("X", 3)
    #     manager.wait(0.05)

    #     manager.press("1")
    #     manager.wait(0.05)
    #     manager.press("X", 15)

    #     manager.press("2")
    #     manager.wait(0.05)
    #     manager.press("X")
    #     manager.wait(0.05)

    #     manager.press("4")
    #     manager.wait(0.05)
    #     manager.press("X")
    #     manager.wait(0.05)

    #     manager.press("5")
    #     manager.wait(0.05)
    #     manager.press("X")
    #     manager.wait(0.05)

    #     manager.press("6")
    #     manager.wait(0.05)
    #     manager.press("X")
    #     manager.wait(0.05)

    #     manager.press("3")
    #     manager.wait(4)

    #     manager.press("4")
    #     manager.wait(0.05)
    #     manager.press("5")
    #     manager.wait(0.05)
    #     manager.press("6")
    #     manager.wait(0.05)


    #     while not manager.picmath("hui"):
    #         manager.wait(2)

    #     manager.press("V")
    


    # #task()

    # run_duration(task, 11, 40, 0)

        
