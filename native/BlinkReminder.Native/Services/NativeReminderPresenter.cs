namespace BlinkReminder.Native.Services;

public sealed class NativeReminderPresenter : IReminderPresenter
{
    public Task ShowReminderAsync(CancellationToken cancellationToken)
    {
        // The actual native overlay should be implemented with a top-most WinUI window
        // or AppWindow-based lightweight surface on Windows.
        return Task.CompletedTask;
    }

    public Task HideReminderAsync()
    {
        return Task.CompletedTask;
    }
}
