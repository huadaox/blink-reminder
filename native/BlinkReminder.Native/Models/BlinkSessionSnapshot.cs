namespace BlinkReminder.Native.Models;

public sealed record BlinkSessionSnapshot(
    double BlinksPerMinute,
    int TotalBlinkCount,
    string LastBlinkText,
    string PipelineMode,
    string StatusText,
    string DetailText,
    IReadOnlyList<string> RecentEvents
);
