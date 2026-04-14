# 眨眼提醒 Blink Reminder

人在长时间盯着屏幕时，眨眼次数通常会明显下降。眨眼减少会影响泪膜稳定，容易带来眼干、酸胀、疲劳等问题。

这个项目的目标很直接：做一个本地离线运行的小工具，利用摄像头估计用户的眨眼频率，并在眨眼频率过低时，用尽量温和、不打扰的方式提醒用户主动眨眼。

## 适用场景

- 长时间办公
- 写代码、写文档、做表格
- 长时间阅读网页或 PDF
- 游戏、剪辑、看盘等高专注盯屏场景

## 当前功能

- 实时估计眨眼频率
- 显示每分钟眨眼次数
- 显示最近 5 分钟眨眼时间线
- 显示最近一次眨眼距今时间
- 在眨眼频率过低时弹出低侵入式提醒动画
- 支持本地离线运行，不依赖云端服务
- 提供调试信息，便于继续优化识别效果

## 当前技术方案

- `PySide6`：桌面界面与提醒浮层
- `MediaPipe Face Mesh`：人脸与眼部区域定位
- `ONNX Runtime`：眼睛开闭状态推理
- `EAR` 自适应兜底：在模型不稳定或部分遮挡时维持可用性

当前识别策略不是单纯依赖固定阈值，而是混合使用：

1. 人脸关键点提取眼部区域
2. ONNX 模型估计眼睛开闭状态
3. 当模型输出不稳定时，回退到基于 `EAR` 的自适应估计
4. 将信号转换为眨眼事件和滚动频率

## 原生重构方向

为了明显提高准确度和稳定性，仓库里已经开始并行推进 Windows 原生版重构：

- `WinUI 3`
- `Windows ML`
- `OpenVINO` 多模型管线

对应目录：

```text
native/
```

原生版的目标是把识别主链改成：

1. 人脸检测
2. landmarks / 眼区定位
3. 左右眼独立开闭分类
4. 头姿过滤
5. 眨眼状态机

相比当前 Python 桌面版，这条路线更适合继续做：

- 距离变化下的稳定识别
- 疲倦小眼场景
- 单眼遮挡场景
- 更稳的 Windows 分发

## 为什么要做这个工具

很多人并不会主动意识到自己在盯屏时眨眼变少了。真正等到眼睛明显难受时，往往已经持续很久。

相比复杂的健康平台，这个项目更偏向一个简单、实用的小工具：

- 只做一件事：提醒你别忘了眨眼
- 尽量离线、本地运行
- 尽量弱打扰，不做常驻大悬浮窗
- 允许继续迭代识别准确率和提醒体验

## 项目结构

- `main.py`：程序入口
- `app_qt.py`：Qt 应用启动
- `qt_main_window.py`：主界面
- `qt_overlay.py`：提醒动画浮层
- `qt_monitor_controller.py`：摄像头采集、推理与状态流转
- `blink_tracker.py`：眨眼计数与频率统计
- `models/eye_state_classifier.onnx`：眼睛开闭模型
- `assets/reminder_frames/`：提醒动画帧素材

## 运行环境

- Windows 10 / 11
- 可用摄像头
- Python `3.12`

当前不建议直接使用 Python `3.14`，因为部分视觉依赖在该版本上的 wheel 支持并不完整。

## 本地运行

```powershell
py -m uv python install 3.12
py -m uv venv --python 3.12 .venv
& .\.venv\Scripts\Activate.ps1
python -m ensurepip --upgrade
python -m pip install --upgrade pip
python -m pip install -r .\requirements.txt
python .\main.py
```

如果你的环境里 `uv` 不在 PATH 中，也可以继续使用创建好的 `.venv`，直接通过 `pip` 安装依赖。

## 打包

建议使用 `PyInstaller` 的 `onedir` 方式：

```powershell
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --windowed --onedir --name BlinkMonitorQt --add-data "assets\reminder_frames;assets\reminder_frames" --add-data "models\eye_state_classifier.onnx;models" --collect-all PySide6 --collect-all onnxruntime --collect-all cv2 --collect-all mediapipe main.py
```

输出目录：

```powershell
dist\BlinkMonitorQt\
```

分发时应打包整个目录，而不是只拿单个 `exe` 文件。

## 当前状态

这是一个仍在持续迭代中的桌面版 beta 项目，目前重点放在：

- 提高不同眼型、不同距离下的识别稳定性
- 降低提醒侵入感
- 降低 CPU 占用
- 优化分发和安装体验
- 推进 `native/` 下的原生 Windows 重构

## 已知限制

- 光照过差时识别会下降
- 大角度侧脸时效果有限
- 眼镜强反光会影响识别
- 疲倦导致眼睛自然睁开较小时，虽然已经加入自适应逻辑，但仍有继续优化空间
- 打包体积仍然较大

## 开源协议

本项目采用 `MIT License` 开源。
