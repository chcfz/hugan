from pynput import keyboard
import pyautogui
from mannager import Manager
import json

class CallBacker:
    def __init__(self, manager:Manager):
        self.manager = manager
        self.isgrab = False
        self.last_x = 0
        self.last_y = 0
        self.last_client_x = 0
        self.last_client_y = 0
        self.key_xy = {}
    def on_press(self, key):
        
        """键盘按键监听"""
        if key.char == 'a':  # 检测按下的是 A 键
            x, y = pyautogui.position()
            print(f"点击：({x}, {y})")
            # manager.click(x, y)  # 点击坐标
            client_x = x - self.manager.win_controller.window_left
            client_y = y - self.manager.win_controller.window_top
            print(f"客户端坐标：({client_x}, {client_y})")
            if self.isgrab:
                print(f"截图：({self.last_x}, {self.last_y}, {x}, {y})")
                screenshot = self.manager.grab(self.last_client_x, self.last_client_y, client_x, client_y)
                name = input("请输入截图名称：")
                screenshot.save(f"pictures/{name}_{self.last_client_x}_{self.last_client_y}_{client_x}_{client_y}.png")
                self.isgrab = False
            else:
                self.last_x = x
                self.last_y = y
                self.last_client_x = client_x
                self.last_client_y = client_y
                self.isgrab = True
        elif key.char == 's':  # 检测按下的是 S 键
            #print(f"客户端顶点坐标：({self.manager.win_controller.window_left}, {self.manager.win_controller.window_top})")
            x, y = pyautogui.position()
            client_x = x - self.manager.win_controller.window_left
            client_y = y - self.manager.win_controller.window_topss
            name = input("请输入坐标名称：")
            self.key_xy[name] = (client_x, client_y)
            #print(f'点击：({x}, {y})')
            print(f"({client_x}, {client_y})")
        elif key.char == 'q':
            print("退出监听")
            with open('key_xy.txt', 'w') as f:
                for k, v in self.key_xy.items():
                    f.write(f"{k}:{v}\n")
            return False



if __name__ == "__main__":
      # 修改为你的游戏窗口标题
    manager = Manager()
    manager.connect("部落冲突 - MuMu安卓设备")  # 修改为你的游戏窗口标题
    callback = CallBacker(manager)
    listener =  keyboard.Listener(on_press=callback.on_press)
    listener.start()
    listener.join()