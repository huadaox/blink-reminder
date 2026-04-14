using BlinkReminder.Native.Models;

namespace BlinkReminder.Native.Services;

public interface ICameraFrameSource : IAsyncDisposable
{
    Task InitializeAsync(CancellationToken cancellationToken);
    IAsyncEnumerable<CameraFrame> GetFramesAsync(CancellationToken cancellationToken);
}
