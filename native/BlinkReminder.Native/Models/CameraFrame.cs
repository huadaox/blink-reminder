namespace BlinkReminder.Native.Models;

public sealed record CameraFrame(
    byte[] PixelBuffer,
    int Width,
    int Height,
    long TimestampTicks
);
