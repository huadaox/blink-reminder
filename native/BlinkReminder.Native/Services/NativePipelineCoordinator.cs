using BlinkReminder.Native.Models;

namespace BlinkReminder.Native.Services;

public sealed class NativePipelineCoordinator
{
    private readonly ICameraFrameSource _cameraFrameSource;
    private readonly IPipelineFrameProcessor _frameProcessor;
    private readonly IReminderPresenter _reminderPresenter;

    public NativePipelineCoordinator(
        ICameraFrameSource cameraFrameSource,
        IPipelineFrameProcessor frameProcessor,
        IReminderPresenter reminderPresenter)
    {
        _cameraFrameSource = cameraFrameSource;
        _frameProcessor = frameProcessor;
        _reminderPresenter = reminderPresenter;
    }

    public async Task<IReadOnlyList<string>> WarmupAsync(CancellationToken cancellationToken)
    {
        await _cameraFrameSource.InitializeAsync(cancellationToken);
        return new[]
        {
            "相机已初始化",
            "等待第一帧进入推理管线",
            "下一步将串联 face detection / landmarks / eye state / head pose"
        };
    }

    public async Task<PipelineFrameResult?> ProcessNextFrameAsync(CancellationToken cancellationToken)
    {
        await foreach (var frame in _cameraFrameSource.GetFramesAsync(cancellationToken))
        {
            return await _frameProcessor.ProcessAsync(frame, cancellationToken);
        }

        return null;
    }

    public Task ShowReminderPreviewAsync(CancellationToken cancellationToken)
    {
        return _reminderPresenter.ShowReminderAsync(cancellationToken);
    }
}
