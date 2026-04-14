using System.IO;

namespace BlinkReminder.Native.Models;

public sealed class OpenVinoModelPaths
{
    public string FaceDetectionPath { get; init; } = @"Assets\Models\openvino\face-detection-retail-0004.onnx";
    public string Landmarks35Path { get; init; } = @"Assets\Models\openvino\facial-landmarks-35-adas-0002.onnx";
    public string EyeStatePath { get; init; } = @"Assets\Models\openvino\open-closed-eye-0001.onnx";
    public string HeadPosePath { get; init; } = @"Assets\Models\openvino\head-pose-estimation-adas-0001.onnx";

    public IEnumerable<string> EnumerateRequiredFiles()
    {
        yield return FaceDetectionPath;
        yield return Landmarks35Path;
        yield return EyeStatePath;
        yield return HeadPosePath;
    }

    public IEnumerable<string> FindMissingFiles()
    {
        return EnumerateRequiredFiles().Where(path => !File.Exists(path));
    }
}
