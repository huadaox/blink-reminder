# 原生重构说明

这个目录对应新的 Windows 原生重构方向：

- `WinUI 3`
- `Windows ML`
- `OpenVINO` 多模型管线

## 为什么要重构

之前的 Python 版适合快速迭代，但在这些场景上已经碰到上限：

- 用户疲倦、自然睁眼变小时，阈值和稳定性会明显波动
- 单眼遮挡时，识别结果容易崩掉
- 与摄像头距离变化时，固定逻辑不够稳
- 打包体积和分发稳定性一般

原生版要解决的就是这些问题。

## 新的识别主链

原生版会把识别拆成明确的多阶段：

1. `face-detection-retail-0004`：做人脸检测
2. `facial-landmarks-35-adas-0002`：做人脸关键点和眼区定位
3. `open-closed-eye-0001`：对左右眼分别做开闭分类
4. `head-pose-estimation-adas-0001`：过滤偏头过大场景
5. 眨眼状态机：把时间序列信号转成眨眼事件和提醒条件

## 当前已经完成

- 原生工程结构
- `WinUI 3` 主窗口骨架
- `Windows ML` 启动入口
- 模型目录约定
- ViewModel / Service 分层
- 相机帧源、提醒展示、管线协调器接口
- OpenVINO 模型准备脚本

## 需要在 Windows 机器上继续完成的部分

这些部分无法在当前 Linux 终端里完整验证，需要在 Windows 开发环境上继续：

- `MediaCapture` 真正接入摄像头
- 4 个模型的实际推理 session
- 帧预处理和后处理
- 头姿过滤策略
- 原生提醒浮层
- 原生打包和发布

## 开发环境

建议在 Windows 上准备：

- Visual Studio 2022
- .NET 8 SDK
- Windows application development workload
- Windows App SDK 相关工具链

## 推荐顺序

1. 跑 `prepare-models.ps1`
2. 打开 `BlinkReminder.Native.sln`
3. 先让 WinUI 工程成功编译
4. 接 `MediaCapture`
5. 接 `OpenVinoFrameProcessor`
6. 再实现提醒浮层和设置页
