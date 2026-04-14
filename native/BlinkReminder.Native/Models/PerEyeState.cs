namespace BlinkReminder.Native.Models;

public sealed record PerEyeState(
    double? LeftClosedProbability,
    double? RightClosedProbability,
    double? LeftOpenSignal,
    double? RightOpenSignal
);
