using BlinkReminder.Native.Models;

namespace BlinkReminder.Native.Services;

public sealed class OpenVinoFrameProcessor : IPipelineFrameProcessor
{
    public Task<PipelineFrameResult> ProcessAsync(CameraFrame frame, CancellationToken cancellationToken)
    {
        var result = new PipelineFrameResult(
            EyeSignal: null,
            EarValue: null,
            EyeState: new PerEyeState(null, null, null, null),
            PoseState: null,
            StatusText: "等待模型推理实现"
        );

        return Task.FromResult(result);
    }
}
