import win32gui
import win32api
import win32con
import time
import random
import ctypes

class MuMuController:
    def __init__(self):
        self.simulator_hwnd = None      # 模拟器主窗口句柄
        self.game_hwnd = None           # 游戏子窗口句柄
        self.client_rect = (0, 0, 0, 0) # 客户区坐标
        self.dpi_scale = 1.0           # DPI缩放因子
        
    def connect(self, window_title):
        """连接到MuMu模拟器窗口"""
        try:
            # 获取模拟器主窗口
            self.simulator_hwnd = win32gui.FindWindow("Qt5154QWindowIcon", window_title)
            if not self.simulator_hwnd:
                self.simulator_hwnd = win32gui.FindWindow(None, window_title)
                if not self.simulator_hwnd:
                    raise Exception("未找到MuMu模拟器窗口")
            
            # 获取游戏渲染窗口(可能是DirectX子窗口)
            self.game_hwnd = self._find_game_window()
            
            # 获取DPI缩放比例
            self._get_dpi_scaling()
            
            # 获取客户区坐标
            rect = win32gui.GetClientRect(self.game_hwnd)
            self.client_rect = (rect[0], rect[1], rect[2], rect[3])
            self.window_left, self.window_top,_,_ = win32gui.GetWindowRect(self.game_hwnd)
            # print(f"成功连接到MuMu模拟器 | 主窗口: {self.simulator_hwnd} | 游戏窗口: {self.game_hwnd}")
            # print(f"游戏区域: {self.client_rect[2]}x{self.client_rect[3]} (DPI缩放: {self.dpi_scale:.1f})")
            return True
            
        except Exception as e:
            return False
    
    def _find_game_window(self):
        """查找MuMu模拟器内的游戏窗口"""
        # 尝试查找常见的渲染窗口类
        classes_to_try = [
            "RenderWindow", 
            "UnityWndClass",
            "CEF-OSC-WIDGET",
            "Windows.UI.Core.CoreWindow"
        ]
        
        for class_name in classes_to_try:
            hwnd = win32gui.FindWindowEx(self.simulator_hwnd, None, class_name, None)
            if hwnd:
                return hwnd
        
        # 如果没找到特定类，尝试枚举子窗口
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                extra.append(hwnd)
            return True
            
        children = []
        win32gui.EnumChildWindows(self.simulator_hwnd, callback, children)
        
        return children[0] if children else self.simulator_hwnd
    
    def _get_dpi_scaling(self):
        """获取DPI缩放比例"""
        try:
            user32 = ctypes.windll.user32
            self.dpi_scale = user32.GetDpiForWindow(self.simulator_hwnd) / 96.0
        except:
            self.dpi_scale = 1.0
    
    def _adjust_coords(self, x, y):
        """调整坐标考虑DPI缩放"""
        return int(x * self.dpi_scale), int(y * self.dpi_scale)
    
    def click(self, x, y, button="left"):
        """后台模拟点击(不移动物理鼠标)"""
        if not self.game_hwnd:
            print("未连接到游戏窗口")
            return False
        
        # 调整DPI缩放后的坐标
        x, y = self._adjust_coords(x, y)
        
        # 确保坐标在客户区内
        if not (0 <= x <= self.client_rect[2] and 0 <= y <= self.client_rect[3]):
            print(f"坐标超出范围: ({x}, {y})")
            return False
        
        # 创建LPARAM (低16位=x, 高16位=y)
        lparam = win32api.MAKELONG(x, y)
        
        # 根据按钮类型选择消息
        msg_down = win32con.WM_LBUTTONDOWN if button == "left" else win32con.WM_RBUTTONDOWN
        msg_up = win32con.WM_LBUTTONUP if button == "left" else win32con.WM_RBUTTONUP
        key_state = win32con.MK_LBUTTON if button == "left" else win32con.MK_RBUTTON
        
        # 发送鼠标消息
        win32gui.PostMessage(self.game_hwnd, msg_down, key_state, lparam)
        time.sleep(random.uniform(0.05, 0.15))
        win32gui.PostMessage(self.game_hwnd, msg_up, 0, lparam)
        return True
    
    def press_key(self, vk_code, press_time=0.1):
        """后台模拟按键(不干扰物理键盘)"""
        if not self.game_hwnd:
            print("未连接到游戏窗口")
            return False
        
        # 发送按键消息
        win32gui.PostMessage(self.game_hwnd, win32con.WM_KEYDOWN, vk_code, 0)
        time.sleep(press_time)
        win32gui.PostMessage(self.game_hwnd, win32con.WM_KEYUP, vk_code, 0)
        return True
    
    def swipe(self, start_x, start_y, end_x, end_y, duration=0.5):
        """模拟滑动操作"""
        if not self.game_hwnd:
            return False
            
        start_x, start_y = self._adjust_coords(start_x, start_y)
        end_x, end_y = self._adjust_coords(end_x, end_y)
        
        steps = int(duration * 10)
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        
        # 发送鼠标按下
        lparam = win32api.MAKELONG(start_x, start_y)
        win32gui.PostMessage(self.game_hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
        
        # 模拟移动
        for i in range(steps):
            x = int(start_x + dx * i)
            y = int(start_y + dy * i)
            lparam = win32api.MAKELONG(x, y)
            win32gui.PostMessage(self.game_hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, lparam)
            time.sleep(duration/steps)
        
        # 发送鼠标释放
        lparam = win32api.MAKELONG(end_x, end_y)
        win32gui.PostMessage(self.game_hwnd, win32con.WM_LBUTTONUP, 0, lparam)
        return True

if __name__ == "__main__":
    # 虚拟键码表 (MuMu模拟器常用)
    KEY_MAP = {
        'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
        'enter': 0x0D, 'space': 0x20, 'esc': 0x1B,
        'f1': 0x70, 'f2': 0x71, 'f3': 0x72
    }
    
    controller = MuMuController()
    if controller.connect("部落冲突 - MuMu模拟器12"):
        print("开始后台自动化...")
        
        # 示例操作序列
        controller.click(100, 200)  # 点击坐标(100,200)
        time.sleep(1)
        
        controller.press_key(KEY_MAP['enter'])  # 按Enter键
        time.sleep(1)
        
        controller.swipe(300, 300, 600, 600, 0.8)  # 从(300,300)滑动到(600,600)
        
        print("自动化完成")
    else:
        print("连接MuMu模拟器失败")