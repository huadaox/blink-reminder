namespace BlinkReminder.Native.Models;

public sealed record PipelineFrameResult(
    double? EyeSignal,
    double? EarValue,
    PerEyeState EyeState,
    FacePoseState? PoseState,
    string StatusText
);
