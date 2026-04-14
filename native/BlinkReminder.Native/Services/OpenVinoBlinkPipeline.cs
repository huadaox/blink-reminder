using BlinkReminder.Native.Models;

namespace BlinkReminder.Native.Services;

public sealed class OpenVinoBlinkPipeline : IBlinkPipeline
{
    private readonly WindowsMlBootstrapper _bootstrapper = new();
    private readonly OpenVinoModelPaths _modelPaths = new();
    private bool _initialized;

    public async Task InitializeAsync(CancellationToken cancellationToken)
    {
        var missing = _modelPaths.FindMissingFiles().ToArray();
        if (missing.Length > 0)
        {
            throw new FileNotFoundException(
                "Missing required OpenVINO model files for the native pipeline.",
                string.Join(Environment.NewLine, missing)
            );
        }

        using var environment = await _bootstrapper.InitializeAsync(cancellationToken);
        _initialized = true;
    }

    public Task<BlinkSessionSnapshot> StartAsync(CancellationToken cancellationToken)
    {
        if (!_initialized)
        {
            throw new InvalidOperationException("Pipeline must be initialized before StartAsync.");
        }

        var snapshot = new BlinkSessionSnapshot(
            BlinksPerMinute: 0,
            TotalBlinkCount: 0,
            LastBlinkText: "等待输入",
            PipelineMode: "OpenVINO / WinML",
            StatusText: "原生管线骨架已就绪",
            DetailText: "下一步是在 Windows 开发机上依次接入相机采集、四模型推理串联、头姿过滤和提醒触发。",
            RecentEvents: new[]
            {
                "已切换到 Windows 原生架构方向",
                "已预留 OpenVINO 多模型目录",
                "已接入 Windows ML 启动入口"
            }
        );

        return Task.FromResult(snapshot);
    }

    public Task PauseAsync()
    {
        return Task.CompletedTask;
    }

    public Task TriggerReminderPreviewAsync()
    {
        return Task.CompletedTask;
    }
}
