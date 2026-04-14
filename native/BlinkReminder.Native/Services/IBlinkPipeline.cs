using BlinkReminder.Native.Models;

namespace BlinkReminder.Native.Services;

public interface IBlinkPipeline
{
    Task InitializeAsync(CancellationToken cancellationToken);
    Task<BlinkSessionSnapshot> StartAsync(CancellationToken cancellationToken);
    Task PauseAsync();
    Task TriggerReminderPreviewAsync();
}
