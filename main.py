import os, sys, time, requests, threading
import numpy as np, cv2, mss, winsound
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from rapidocr_onnxruntime import RapidOCR

# 适配 PyInstaller 运行时路径定位
if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

# 模块: Bark 推送服务
def push_to_bark(key, content):
    if not key: return
    def t():
        try:
            requests.get(f"https://api.day.app/{key}/FocusWatch/{content}", timeout=5)
        except: pass
    threading.Thread(target=t, daemon=True).start()

# 组件: 全屏闪烁警报遮罩层
class AlertOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()
        self.flash_color = QColor(255, 0, 0, 80)
        self.is_visible = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.toggle_flash)
        self.count = 0

    def start_flash(self):
        self.count = 0
        self.timer.start(250)
        self.show()

    def toggle_flash(self):
        self.is_visible = not self.is_visible
        self.update()
        self.count += 1
        if self.count > 10: 
            self.timer.stop()
            self.hide()

    def paintEvent(self, event):
        if self.is_visible:
            p = QPainter(self)
            p.fillRect(self.rect(), self.flash_color)

# 核心: 屏幕捕获与 OCR 识别线程
class MonitorThread(QThread):
    keyword_detected = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.region = None
        self.keywords = []
        self.interval = 5
        self.ocr = RapidOCR()

    def run(self):
        self.running = True
        with mss.mss() as sct:
            while self.running:
                if self.region and self.keywords:
                    m = {"top": self.region.y(), "left": self.region.x(),
                         "width": self.region.width(), "height": self.region.height()}
                    try:
                        img = np.array(sct.grab(m))
                        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                        res, _ = self.ocr(img)
                        if res:
                            txt = "".join([i[1] for i in res])
                            for k in self.keywords:
                                if k.strip() and k.strip() in txt:
                                    self.keyword_detected.emit(k)
                                    for _ in range(100): 
                                        if not self.running: return
                                        time.sleep(0.1)
                                    break
                    except: pass
                
                for _ in range(int(self.interval * 10)):
                    if not self.running: return
                    time.sleep(0.1)

    def stop(self):
        self.running = False
        self.wait() 

# 组件: 屏幕坐标选区工具
class SelectionOverlay(QWidget):
    region_selected = Signal(QRect)
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.showFullScreen()
        self.s = None; self.e = None

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0, 160))
        if self.s and self.e:
            r = QRect(self.s, self.e).normalized()
            p.setCompositionMode(QPainter.CompositionMode_Clear)
            p.fillRect(r, Qt.transparent)
            p.setCompositionMode(QPainter.CompositionMode_SourceOver)
            p.setPen(QPen(QColor("#FF9500"), 3))
            p.drawRect(r)

    def mousePressEvent(self, e):
        self.s = e.globalPos(); self.e = self.s
    def mouseMoveEvent(self, e):
        self.e = e.globalPos(); self.update()
    def mouseReleaseEvent(self, e):
        r = QRect(self.s, self.e).normalized()
        if r.width() > 10: self.region_selected.emit(r)
        self.close()

# 组件: 自定义状态切换按钮
class CheckButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setCheckable(True)
        self.setChecked(True)
        self.setFixedWidth(180)
        self.setFixedHeight(42)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        bg = QColor("#1D1D1F") if self.isChecked() else QColor("#FFF")
        p.setBrush(bg)
        p.setPen(QPen(QColor("#DDD"), 1))
        p.drawRoundedRect(self.rect(), 22, 22)

        icon_color = QColor("#FFF") if self.isChecked() else QColor("#1D1D1F")
        p.setBrush(icon_color)
        p.setPen(Qt.NoPen)
        p.drawEllipse(15, 14, 16, 16)
        
        p.setPen(QColor("#FFF") if self.isChecked() else QColor("#1D1D1F"))
        p.setFont(QFont("SF Pro Text", 10, QFont.Weight.Bold))
        p.drawText(self.rect().adjusted(25, 0, 0, 0), Qt.AlignCenter, self.text())

# 视图: 主控制面板
class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.monitor = MonitorThread()
        self.monitor.keyword_detected.connect(self.hit)
        self.alert = AlertOverlay()
        self.init_ui()

    def line(self):
        w = QFrame()
        w.setFixedHeight(1)
        w.setStyleSheet("background:#C7C7CC;")
        w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return w

    def init_ui(self):
        self.setFixedSize(650, 650)
        self.setWindowTitle("FocusWatch Dust")
        self.setWindowIcon(QIcon("logo.ico"))
        apple_font = "'SF Pro Display', 'SF Pro Text', 'PingFang SC', sans-serif"

        self.setStyleSheet(f"""
            /* 全局基础样式设置 */
            QWidget {{ 
                background: #e8e7e8; 
                font-family: {apple_font}; 
            }}

            /* 全局焦点状态重置 */
            * {{
                lineedit-password-character: 9679; /* 统一密码占位符样式 */
            }}
            
            /* 移除标准输入控件的焦点虚线框 */
            QPushButton:focus, QLineEdit:focus, QComboBox:focus, QTextEdit:focus {{
                outline: none; /* 重置焦点轮廓 */
                border: 1px solid #D1D1D6; /* 焦点状态保持边框颜色一致 */
            }}
            
            /* 移除无边框按钮的焦点边框 */
            QPushButton:focus {{
                border: none;
            }}

            /* 主容器卡片 */
            QFrame#card {{ 
                background: #f1f2f3; 
                border-radius: 25px; 
                border: 1px solid #c4c3c3; 
            }}
            
            /* QLabel */
            QLabel {{ color: #1D1D1F; font-size: 14px; font-weight: 700; background: transparent; }}
            
            /* QLineEdit */
            QLineEdit {{ 
                background: #fdfdfd; border: 1px solid #D1D1D6; border-radius: 12px; padding: 6px; 
                font-size: 13px; font-weight: 700; color: #1D1D1F;
            }}

            /* QComboBox 系列 */
            QComboBox {{ 
                background: #fdfdfd; border: 1px solid #D1D1D6; border-radius: 12px; padding: 6px; 
                font-size: 13px; font-weight: 700; color: #1D1D1F;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 32px;
                border-left: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                background: #E5E5EA; /* 下拉箭头背景指示器 */
                width: 20px;
                height: 20px;
                margin-right: 6px;
                border-radius: 6px;
                border: none; /* 清除多余边框渲染 */
            }}
            
            QComboBox QAbstractItemView {{
                background-color: white;
                border: 1px solid #D1D1D6;
                border-radius: 12px;
                outline: 0px; /* 轮廓线重置 */
                padding: 4px;
            }}
            
            QComboBox QAbstractItemView::item {{
                min-height: 35px;
                border-radius: 10px;
                margin: 2px;
                padding-left: 10px;
                font-weight: 700;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: #000000;
                color: white;
            }}

            /* 滚动条与文本框组件样式 */
            QScrollBar:vertical {{ border: none; background: transparent; width: 6px; margin: 4px; }}
            QScrollBar::handle:vertical {{ background: #C1C1C1; border-radius: 3px; }}
            QPushButton#action {{ background: #007AFF; color: #FFF; font-weight: 900; border-radius: 22px; }}
            QTextEdit {{ 
                background: #eaeaea; border: none; border-radius: 15px; padding: 10px; 
                color: #424245; font-size: 12px; font-weight: 700;
            }}
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(25, 25, 25, 25)

        card = QFrame(objectName="card")
        # 配置主卡片的全局阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(35)        
        shadow.setXOffset(0)          
        shadow.setYOffset(0)             
        shadow.setColor(QColor(0, 0, 0, 60))
       
        
        card.setGraphicsEffect(shadow)
        
        outer.addWidget(card)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(10)

        # --- Header ---
        title = QLabel("FocusWatch Dust v1.4")
        title.setStyleSheet("font-size: 38px; font-weight: 2000; letter-spacing: -0.8px;")
        layout.addWidget(title)
        layout.addWidget(self.line())

        # --- 关键词 ---
        layout.addSpacing(10)
        kw_row = QHBoxLayout()
        kw_row.addWidget(QLabel("检测关键字"))
        
        self.kw_input = QLineEdit()
        self.kw_input.setFixedWidth(200)
        self.kw_input.setText("习题,选择,课堂")
        self.kw_input.setPlaceholderText("多个词用逗号分隔...")
        kw_row.addWidget(self.kw_input)
        kw_row.addStretch()
        layout.addLayout(kw_row)

        # --- 频率 ---
        freq_row = QHBoxLayout()
        freq_row.addWidget(QLabel("检测间隔(s)"))
        self.combo = QComboBox()
        self.combo.addItems(["2", "5", "10", "30", "没有自定义^^"])
        self.combo.setCurrentText("5")
        # 配置下拉菜单弹出层的无边框与透明属性
        self.combo.view().window().setAttribute(Qt.WA_TranslucentBackground)
        self.combo.view().window().setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        freq_row.addWidget(self.combo)
        freq_row.addStretch()
        layout.addLayout(freq_row)
        
        layout.addSpacing(11)
        # --- Bark ---
        b_head = QHBoxLayout()
        b_head.addWidget(QLabel("输入推送 Key   (见README）"))
        b_head.addWidget(self.line())
        layout.addLayout(b_head)
        layout.addSpacing(5)  # UI 垂直间距调整
        bark_row = QHBoxLayout()
        bark_row.setContentsMargins(20, 0, 0, 0)
        bark_row.setSpacing(15) 
        
        bark_row.addWidget(QLabel("api.day.app/"))
        
        self.bark_input = QLineEdit()
        self.bark_input.setFixedWidth(180)
        bark_row.addWidget(self.bark_input)
        
        bark_row.addWidget(QLabel("/ColorfulEgg"))
        bark_row.addStretch() # 弹性空间占位，维持右侧对齐
        
        layout.addLayout(bark_row)
        layout.addSpacing(10)  # UI 垂直间距调整
       # bark_row.addWidget(QLabel("api.day.app/"))
       # --- 提醒与操作 ---
        op_head = QHBoxLayout()
        op_head.addWidget(QLabel("提醒与操作"))
        op_head.addWidget(self.line())
        layout.addLayout(op_head)
        layout.addSpacing(10)
        # --- 按钮区 ---
        btn_row = QHBoxLayout()
        self.btn_sel = QPushButton("1. 定位区域")
        self.btn_sel.setFixedSize(170, 42)
        self.btn_sel.setStyleSheet("background:#E5E5EA; color:#000; font-size:14px; font-weight:700; border-radius:20px; border:none;")
        
        self.btn_alert = CheckButton("强提醒 (闪烁+声音)")
        
        btn_row.addWidget(self.btn_sel)
        btn_row.addWidget(self.btn_alert)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # --- 主运行按钮 ---
        self.btn_run = QPushButton("2. 开始运行", objectName="action")
        self.btn_run.setFixedSize(170, 42)
        self.btn_run.setStyleSheet("background:#FF9500; color:white; border-radius:20px; font-size:14px; font-weight:900;")
        layout.addWidget(self.btn_run)
        layout.addSpacing(10)
        # --- 日志 ---
        l_head = QHBoxLayout()
        # l_head.addWidget(QLabel("运行日志"))
        # l_head.addWidget(self.line())
        layout.addLayout(l_head)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(self.log_box)

        self.btn_sel.clicked.connect(self.select_area)
        self.btn_run.clicked.connect(self.toggle_monitor)

    def select_area(self):
        self.ov = SelectionOverlay()
        self.ov.region_selected.connect(self.save_region)
        self.log("请拖拽鼠标选择区域...")

    def save_region(self, r):
        self.monitor.region = r
        self.log(f"区域已锁定: {r.width()}x{r.height()}")

    def hit(self, k):
        self.log(f"🚨 命中关键词: {k}")
        if self.bark_input.text():
            push_to_bark(self.bark_input.text(), f"检测到关键字:{k}")
        if self.btn_alert.isChecked():
            self.alert.start_flash()
            winsound.Beep(1000, 600)

    def toggle_monitor(self):
        if self.monitor.running:
            self.monitor.stop()
            self.btn_run.setText("开始运行")
            self.btn_run.setStyleSheet("""
                background: #FF9500; 
                color: white; 
                border-radius: 20px; 
                font-size: 14px; 
                font-weight: 900;
            """)
            self.log("监控已停止")
        else:
            if not self.monitor.region:
                self.log("🔴 错误: 请先定位区域")
                return
            self.monitor.keywords = self.kw_input.text().split(",")
            self.monitor.interval = int(self.combo.currentText()) if self.combo.currentText().isdigit() else 5
            self.monitor.start()
            self.btn_run.setText("停止运行")
            self.btn_run.setStyleSheet("""
                background: #FF3B30; 
                color: white; 
                border-radius: 20px; 
                font-size: 14px; 
                font-weight: 900;
            """)
            self.log("监控启动中...")

    def log(self, msg):
        self.log_box.append(f" {time.strftime('%H:%M:%S')} {msg}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Dashboard()
    w.show()
    sys.exit(app.exec())