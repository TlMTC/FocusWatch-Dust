🚀 FocusWatch Ultimate
FocusWatch Ultimate 是一款基于本地 OCR 技术的实时屏幕监控与强提醒工具。它能精准识别屏幕特定区域的关键词，并通过视觉闪烁、听觉蜂鸣以及移动端推送，确保你在第一时间获取关键信息。

🌟 核心特性
本地 OCR 识别：保护隐私，无需联网上传截图。

毫秒级响应：实时监测屏幕变化，第一时间触发警报。

多维度提醒：支持屏幕红框闪烁、置顶弹窗、高频蜂鸣。

Bark 联动：深度集成 Bark 推送，让你的 iOS 设备也能同步接收提醒。

🛠️ 环境部署与运行
1. 克隆仓库
Bash
git clone https://github.com/你的用户名/FocusWatch-Ultimate.git
cd FocusWatch-Ultimate
2. 配置虚拟环境 (推荐)
为了保持系统环境整洁，建议创建虚拟环境运行：

Bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate
3. 安装依赖包
Bash
pip install --upgrade pip
pip install numpy opencv-python mss requests PySide6 rapidocr_onnxruntime
4. 运行程序
Bash
python main.py
📖 使用手册
一、 快速开始
1. 定位监控区域
启动程序后，点击 “1. 定位监测区域” 按钮。

此时屏幕将变暗。

使用鼠标左键拖拽，框选你想要监控的屏幕范围（如：在线考试的题目区、聊天软件的特定窗口等）。

松开鼠标，区域即被锁定。

2. 配置关键词
在 “检测关键字” 输入框中输入你想要触发报警的词汇。

支持多个词汇，请使用英文逗号 , 分隔。

例如：题目,测试,习题,异常

3. 选择提醒模式
强提醒 (推荐)：屏幕会发出红光闪烁，窗口强制置顶，并伴随高频蜂鸣声。

弱提醒：仅播放系统默认提示音，适合环境安静时使用。

二、 手机端 Bark 推送配置
为了实现远程接收警报，我们集成了 Bark 推送功能。

1. 什么是 Bark？
Bark 是一款 iOS 端极简的推送工具。它完全免费，且不需要常驻后台即可接收来自 PC 端的实时提醒。

2. 如何获取 Bark Key？
在 iPhone 的 App Store 搜索并下载 Bark。

打开 App，在主界面你会看到一串类似 https://api.day.app/XXXXXXXX/BodyText 的链接。

其中中间那串随机的字符（如 dpX5...）就是你的 Device Key。

点击界面上的“复制”按钮获取该 Key。

3. 在 FocusWatch 中启用推送
将复制好的 Key 粘贴到软件的 “Bark 推送 Key” 输入框中。（仅需输入 XXXXXXXX 区域内的文本）

开启监控后，一旦 PC 端命中关键词，你的手机将同步收到推送通知。

三、 开始运行
点击 “2. 开启运行”。

按钮变为红色，显示“停止运行”，说明程序已进入后台监测状态。

程序默认每 5 秒扫描一次目标区域，此时你可以最小化软件或进行其他操作。

注意：被检测程序不应最小化，需保持在屏幕可见状态。

如何打包成 EXE？
如果你希望将本项目打包为可执行文件，请使用以下命令（需安装 pyinstaller）：

Bash
pip install pyinstaller
python -m PyInstaller -F -w -i logo.ico --add-data "logo.ico;." --collect-all rapidocr_onnxruntime main.py
📄 开源协议
本项目采用 MIT License 协议开源。你可以自由地使用、修改和分发，但请保留原作者信息。