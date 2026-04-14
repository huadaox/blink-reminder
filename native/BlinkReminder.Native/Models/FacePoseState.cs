namespace BlinkReminder.Native.Models;

public sealed record FacePoseState(
    double YawDegrees,
    double PitchDegrees,
    double RollDegrees,
    bool IsPoseAcceptable
);
