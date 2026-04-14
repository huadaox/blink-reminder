namespace BlinkReminder.Native.Services;

public interface IReminderPresenter
{
    Task ShowReminderAsync(CancellationToken cancellationToken);
    Task HideReminderAsync();
}
