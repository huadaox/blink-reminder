using BlinkReminder.Native.Models;

namespace BlinkReminder.Native.Services;

public sealed class MediaCaptureFrameSource : ICameraFrameSource
{
    public Task InitializeAsync(CancellationToken cancellationToken)
    {
        // This is the Windows-only implementation point for MediaCapture initialization.
        return Task.CompletedTask;
    }

    public async IAsyncEnumerable<CameraFrame> GetFramesAsync([System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken)
    {
        while (!cancellationToken.IsCancellationRequested)
        {
            await Task.Delay(100, cancellationToken);
            yield return new CameraFrame(Array.Empty<byte>(), 0, 0, DateTime.UtcNow.Ticks);
        }
    }

    public ValueTask DisposeAsync()
    {
        return ValueTask.CompletedTask;
    }
}
