using BlinkReminder.Native.Models;

namespace BlinkReminder.Native.Services;

public interface IPipelineFrameProcessor
{
    Task<PipelineFrameResult> ProcessAsync(CameraFrame frame, CancellationToken cancellationToken);
}
