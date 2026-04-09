
# 🚀 FocusWatch Dust (FocusWatch-灰尘)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-0078D6.svg)](https://www.microsoft.com/windows)

**FocusWatch Dust** 是一款基于本地 OCR 技术的实时屏幕监控与强提醒工具。它能够精准识别屏幕特定区域的关键词，并通过视觉监控指示灯、听觉蜂鸣以及移动端推送，确保你在第一时间获取关键信息。

---

## 🌟 核心特性

* **🔍 本地 OCR 识别**：保护隐私，所有识别均在本地完成，无需上传网络截图。
* **⚡ 毫秒级响应**：实时监测屏幕变化，毫秒级关键词命中反馈，第一时间触发警报。
* **🚨 多维度提醒**：支持屏幕红框闪烁、窗口强制置顶、以及自定义高频蜂鸣提醒。
* **📱 Bark 联动**：深度集成 Bark 推送协议，支持 iOS 设备远程同步接收实时提醒。

---

## 🛠️ 环境部署与运行

### 1. 克隆仓库
```bash
git clone [https://github.com/你的用户名/FocusWatch-Dust.git](https://github.com/你的用户名/FocusWatch-Dust.git)
cd FocusWatch-Ultimate
```

### 2. 配置虚拟环境 (推荐)
为了保持系统环境运行整洁，建议创建虚拟环境：
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate
```

### 3. 安装依赖包
本项目基于 **PySide6** 框架开发，请运行以下命令一键安装所有依赖：
```bash
pip install --upgrade pip
pip install numpy opencv-python mss requests PySide6 rapidocr_onnxruntime
```

### 4. 运行程序
```bash
python main.py
```

---

## 📖 快速使用手册

### 一、 开始配置

1. **定位监测区域**
   * 启动程序后，点击 **“1. 定位监测区域”** 按钮。
   * 此时屏幕将变暗，使用鼠标左键拖拽，框选你想要监控的屏幕范围（如：在线考试的题目区、聊天软件的特定窗口等）。
   * 松开鼠标，区域即被锁定。

2. **配置关键字**
   * 在 **“检测关键字”** 输入框中输入您想要触发报警的词汇。
   * 支持多个词汇，请使用**英文逗号 `,`** 分隔。
   * *示例：题目,测试,习题,异常*

3. **选择提醒模式**
   * **强提醒 (推荐)**：命中时屏幕发出红光提示，窗口强制置顶，并伴随高频蜂鸣。
   * **弱提醒**：仅播放系统默认提示音，适合安静环境。

### 二、 手机端 Bark 推送配置

为了实现远程接收警报，本项目集成了 **Bark** 推送功能：

1. **什么是 Bark？** Bark 是一款 iOS 端极简的推送工具。它完全免费，且不需要常驻后台即可接收来自 PC 端的实时提醒。
2. **如何获取 Bark Key？**
   * 在 iPhone 的 App Store 下载 Bark。
   * 打开 App，在主界面你会看到一串类似 `https://api.day.app/XXXXXXXX/` 的链接。
   * 其中中间那串随机字符（如 `dpX5...`）就是你的 **Device Key**。
3. **在 FocusWatch 中激活**
   * 将复制好的 Key 粘贴到软件的 **“Bark 推送 Key”** 输入框中。
   * 开启监控后，一旦 PC 端命中关键词，你的手机将同步接收通知。

### 三、 开始运行

* 点击 **“2. 开启运行”**。按钮变为红色显示“停止运行”，说明程序已进入实时监测状态。
* 程序默认每 5 秒扫描一次目标区域，此时您可以最小化软件或进行其他操作。
* **⚠️ 注意**：被检测程序窗口**不应最小化**，需保持在屏幕可见状态（可被其他窗口覆盖，但不能最小化到任务栏）。

---

## 📦 如何打包成 EXE？

如果你希望将本项目打包为独立执行文件（单文件版），请使用以下命令：

```bash
# 安装打包工具
pip install pyinstaller

# 执行打包命令
python -m PyInstaller -F -w -i logo.ico --add-data "logo.ico;." --collect-all rapidocr_onnxruntime main.py
```


## 📄 开源协议

本项目采用 **MIT License** 开源协议。您可以自由地使用、修改和分发，但请务必保留原作者信息。
```
