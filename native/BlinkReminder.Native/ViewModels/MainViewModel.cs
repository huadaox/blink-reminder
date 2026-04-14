using BlinkReminder.Native.Services;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace BlinkReminder.Native.ViewModels;

public sealed partial class MainViewModel : ObservableObject
{
    private readonly IBlinkPipeline _pipeline = new OpenVinoBlinkPipeline();
    private readonly NativePipelineCoordinator _coordinator = new(
        new MediaCaptureFrameSource(),
        new OpenVinoFrameProcessor(),
        new NativeReminderPresenter()
    );

    [ObservableProperty]
    private string _statusText = "等待初始化";

    [ObservableProperty]
    private string _detailText = "这个原生版骨架已准备好，接下来要在 Windows 开发环境内接通四模型推理链路。";

    [ObservableProperty]
    private string _blinksPerMinuteText = "--";

    [ObservableProperty]
    private string _totalBlinkCountText = "--";

    [ObservableProperty]
    private string _lastBlinkText = "--";

    [ObservableProperty]
    private string _pipelineModeText = "OpenVINO / WinML";

    public IList<string> RecentEvents { get; } = new List<string>
    {
        "等待启动",
        "推荐先准备 OpenVINO 官方模型",
        "推荐在 Visual Studio 2022 + .NET 8 下继续实现"
    };

    [RelayCommand]
    private async Task StartAsync()
    {
        try
        {
            StatusText = "正在初始化";
            DetailText = "注册 Windows ML 执行提供程序并检查 OpenVINO 模型文件。";

            await _pipeline.InitializeAsync(CancellationToken.None);
            var snapshot = await _pipeline.StartAsync(CancellationToken.None);
            var warmupEvents = await _coordinator.WarmupAsync(CancellationToken.None);

            StatusText = snapshot.StatusText;
            DetailText = snapshot.DetailText;
            BlinksPerMinuteText = snapshot.BlinksPerMinute.ToString("0.0");
            TotalBlinkCountText = snapshot.TotalBlinkCount.ToString();
            LastBlinkText = snapshot.LastBlinkText;
            PipelineModeText = snapshot.PipelineMode;

            RecentEvents.Clear();
            foreach (var item in snapshot.RecentEvents)
            {
                RecentEvents.Add(item);
            }

            foreach (var item in warmupEvents)
            {
                RecentEvents.Add(item);
            }

            OnPropertyChanged(nameof(RecentEvents));
        }
        catch (Exception ex)
        {
            StatusText = "初始化失败";
            DetailText = ex.Message;
            RecentEvents.Insert(0, $"初始化失败: {ex.GetType().Name}");
            OnPropertyChanged(nameof(RecentEvents));
        }
    }

    [RelayCommand]
    private async Task PauseAsync()
    {
        await _pipeline.PauseAsync();
        StatusText = "已暂停";
        DetailText = "原生推理管线已暂停。";
    }

    [RelayCommand]
    private async Task TestReminderAsync()
    {
        await _pipeline.TriggerReminderPreviewAsync();
        await _coordinator.ShowReminderPreviewAsync(CancellationToken.None);
        RecentEvents.Insert(0, "已触发提醒预览");
        OnPropertyChanged(nameof(RecentEvents));
    }

    [RelayCommand]
    private void OpenModelsFolder()
    {
        StatusText = "模型目录";
        DetailText = @"请把 OpenVINO 模型放到 native\BlinkReminder.Native\Assets\Models\openvino\ 下。";
    }
}
