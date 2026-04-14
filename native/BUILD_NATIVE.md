# 原生版构建说明

这个目录对应新的 Windows 原生重构方向：

- `WinUI 3`
- `Windows ML`
- `OpenVINO` 多模型管线

## 目标机器

请在 Windows 开发机上完成构建，推荐环境：

- Visual Studio 2022
- .NET 8 SDK
- Windows App SDK 对应工作负载

## 第一步：准备模型

在 `native` 目录下执行：

```powershell
cd D:\windows_blink_monitor\native
.\prepare-models.ps1
```

模型会下载到：

```text
BlinkReminder.Native\Assets\Models\openvino\
```

默认会准备这 4 个模型：

- `face-detection-retail-0004.onnx`
- `facial-landmarks-35-adas-0002.onnx`
- `open-closed-eye-0001.onnx`
- `head-pose-estimation-adas-0001.onnx`

## 第二步：打开解决方案

```text
native\BlinkReminder.Native.sln
```

## 第三步：恢复并运行

第一次打开时先做：

1. 恢复 NuGet 包
2. 选择 `x64`
3. 以 `Debug` 启动

## 当前代码状态

当前已经完成：

- 原生工程结构
- WinUI 3 主窗口
- ViewModel / Service 分层
- Windows ML 启动入口
- OpenVINO 模型目录约定

当前还没有在 Linux 端验证编译，因为 WinUI 3 / Windows SDK 只能在 Windows 开发环境里完整构建。

## 下一步实现顺序

建议按这个顺序继续：

1. `MediaCapture` 相机采集
2. 人脸检测模型推理
3. landmarks 模型推理
4. 左右眼开闭模型推理
5. 头姿过滤
6. blink 状态机
7. 原生提醒浮层
