import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QPushButton, 
                               QVBoxLayout, QWidget, QLabel, QMessageBox,
                               QHBoxLayout, QLineEdit)
from PySide6.QtGui import QPixmap, QPainter, QPen, QScreen, QGuiApplication, QColor, QFont
from PySide6.QtCore import Qt, QRect, QPoint, QTimer, Signal

class ScreenshotSelector(QWidget):
    finished = Signal(QPixmap, QRect)
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 获取屏幕尺寸
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(screen_geometry)
        
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_selecting = False
        self.screenshot = None
        self.selection_rect = QRect()
        
        # 捕获当前屏幕
        self.full_screenshot = QGuiApplication.primaryScreen().grabWindow(0)
        
        # 设置光标样式
        self.setCursor(Qt.CrossCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 绘制当前屏幕
        painter.drawPixmap(0, 0, self.full_screenshot)
        
        # 绘制半透明覆盖层
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        if self.is_selecting:
            # 绘制选择区域
            rect = QRect(self.start_point, self.end_point).normalized()
            self.selection_rect = rect
            
            # 绘制选择区域内的清晰内容
            painter.drawPixmap(rect, self.full_screenshot, rect)
            
            # 绘制选择边框
            painter.setPen(QPen(Qt.red, 2))
            painter.drawRect(rect)
            
            # 显示坐标和尺寸信息
            painter.setPen(QPen(Qt.white))
            font = QFont()
            font.setPointSize(12)
            painter.setFont(font)
            
            info_text = f"左上角: ({rect.x()}, {rect.y()}) 右下角: ({rect.x() + rect.width()}, {rect.y() + rect.height()})"
            size_text = f"尺寸: {rect.width()} x {rect.height()}"
            
            # 在合适的位置显示信息
            info_rect = QRect(10, 10, 500, 30)
            painter.fillRect(info_rect, QColor(0, 0, 0, 150))
            painter.drawText(info_rect, Qt.AlignLeft | Qt.AlignVCenter, info_text)
            
            size_rect = QRect(10, 45, 200, 30)
            painter.fillRect(size_rect, QColor(0, 0, 0, 150))
            painter.drawText(size_rect, Qt.AlignLeft | Qt.AlignVCenter, size_text)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 使用 position() 而不是弃用的 pos()
            self.start_point = event.position().toPoint()
            self.end_point = event.position().toPoint()
            self.is_selecting = True
            
    def mouseMoveEvent(self, event):
        if self.is_selecting:
            # 使用 position() 而不是弃用的 pos()
            self.end_point = event.position().toPoint()
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_selecting:
            # 使用 position() 而不是弃用的 pos()
            self.end_point = event.position().toPoint()
            self.is_selecting = False
            
            # 获取选定区域
            rect = QRect(self.start_point, self.end_point).normalized()
            
            # 确保区域有效
            if rect.width() > 5 and rect.height() > 5:
                # 截取屏幕
                screen = QGuiApplication.primaryScreen()
                self.screenshot = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())
                
            # 发送完成信号和区域信息
            self.finished.emit(
                self.screenshot if self.screenshot and not self.screenshot.isNull() else QPixmap(),
                rect
            )
            self.close()
            
    def keyPressEvent(self, event):
        # 按ESC键退出截图模式
        if event.key() == Qt.Key_Escape:
            self.finished.emit(QPixmap(), QRect())  # 发送空截图和空矩形表示取消
            self.close()

class ScreenshotWindow(QWidget):
    def __init__(self, fixed_x=0, fixed_y=0):
        super().__init__()
        self.fixed_x = fixed_x
        self.fixed_y = fixed_y
        self.setWindowTitle("截图工具")
        self.setGeometry(100, 100, 500, 400)
        
        # 创建UI元素
        layout = QVBoxLayout()
        
        # 按钮区域
        button_layout = QVBoxLayout()
        
        self.screenshot_btn = QPushButton("选择区域截图")
        self.screenshot_btn.clicked.connect(self.start_screenshot)
        button_layout.addWidget(self.screenshot_btn)


        self.save_btn = QPushButton("保存截图")
        self.save_btn.clicked.connect(self.save_screenshot)
        button_layout.addWidget(self.save_btn)
        
        # 文件名输入区域
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel("图片名称:"))
        
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("输入图片名称")
        filename_layout.addWidget(self.filename_input)
        
        layout.addLayout(filename_layout)
        layout.addLayout(button_layout)
        
        # 预览区域
        self.preview_label = QLabel("截图预览区域")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        layout.addWidget(self.preview_label)
        
        # 坐标信息显示
        self.coords_label = QLabel("坐标信息将在这里显示")
        self.coords_label.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        layout.addWidget(self.coords_label)
        
        self.setLayout(layout)

        self.current_screenshot = None
        self.current_rect = QRect()
        
    def start_screenshot(self):
        # 隐藏主窗口
        self.hide()
        
        # 使用定时器确保窗口完全隐藏后再显示选择器
        QTimer.singleShot(100, self.show_screenshot_selector)
        
    def show_screenshot_selector(self):
        try:
            # 创建截图选择器
            self.selector = ScreenshotSelector()
            self.selector.finished.connect(self.on_screenshot_finished)
            self.selector.show()
        except Exception as e:
            print(f"Error creating screenshot selector: {e}")
            self.show()
            QMessageBox.critical(self, "错误", f"创建截图选择器失败: {e}")
        
    def on_screenshot_finished(self, screenshot, rect):
        # 显示主窗口
        self.show()
        
        if screenshot and not screenshot.isNull() and not rect.isNull():
            self.current_screenshot = screenshot
            self.current_rect = rect
            
            # 显示截图预览
            self.preview_label.setPixmap(self.current_screenshot.scaled(
                self.preview_label.width(), 
                self.preview_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            
            # 显示坐标信息
            top_x, top_y = rect.x(), rect.y()
            bottom_x, bottom_y = rect.x() + rect.width(), rect.y() + rect.height()
            self.coords_label.setText(
                f"左上角坐标: ({top_x}, {top_y})\n"
                f"右下角坐标: ({bottom_x}, {bottom_y})\n"
                f"区域尺寸: {rect.width()} x {rect.height()}"
            )
            

            # 自动生成默认文件名

            
            # 自动弹出保存对话框
            #self.save_screenshot()
        else:
            QMessageBox.information(self, "信息", "截图已取消")
        
    def save_screenshot(self):
        if self.current_screenshot and not self.current_rect.isNull():
            # 获取坐标信息
            top_x, top_y = self.current_rect.x(), self.current_rect.y()
            bottom_x, bottom_y = self.current_rect.x() + self.current_rect.width(), self.current_rect.y() + self.current_rect.height()
            
            top_x -= self.fixed_x
            top_y -= self.fixed_y
            bottom_x -= self.fixed_x
            bottom_y -= self.fixed_y
            # if not self.filename_input.text():
            #     default_name = f"screenshot_{top_x}_{top_y}_{bottom_x}_{bottom_y}"
            #     self.filename_input.setText(default_name)
            # 获取文件名
            filename = self.filename_input.text().strip()
            if not filename:
                QMessageBox.warning(self, "警告", "请输入图片名称")
                return
                
            # 创建pictures目录（如果不存在）
            pictures_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pictures")
            if not os.path.exists(pictures_dir):
                os.makedirs(pictures_dir)
            
            # 生成带坐标的文件名
            coord_filename = f"{filename}_{top_x}_{top_y}_{bottom_x}_{bottom_y}.png"
            file_path = os.path.join(pictures_dir, coord_filename)
            
            # 检查文件是否已存在
            if os.path.exists(file_path):
                reply = QMessageBox.question(
                    self, 
                    "确认覆盖", 
                    f"文件 {coord_filename} 已存在，是否覆盖？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return            
            # 保存截图
            if self.current_screenshot.save(file_path):
                QMessageBox.information(self, "保存成功", f"截图已保存到：{file_path}")
            else:
                QMessageBox.warning(self, "保存失败", "无法保存截图")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())