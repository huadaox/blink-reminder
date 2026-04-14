param(
    [string]$Destination = ".\BlinkReminder.Native\Assets\Models\openvino",
    [string]$OmzVersion = "2022.1"
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path $Destination | Out-Null

$models = @(
    @{
        Name = "face-detection-retail-0004.onnx"
        Url = "https://storage.openvinotoolkit.org/repositories/open_model_zoo/public/$OmzVersion/face-detection-retail-0004/face-detection-retail-0004.onnx"
    },
    @{
        Name = "facial-landmarks-35-adas-0002.onnx"
        Url = "https://storage.openvinotoolkit.org/repositories/open_model_zoo/public/$OmzVersion/facial-landmarks-35-adas-0002/facial-landmarks-35-adas-0002.onnx"
    },
    @{
        Name = "open-closed-eye-0001.onnx"
        Url = "https://storage.openvinotoolkit.org/repositories/open_model_zoo/public/$OmzVersion/open-closed-eye-0001/open_closed_eye.onnx"
    },
    @{
        Name = "head-pose-estimation-adas-0001.onnx"
        Url = "https://storage.openvinotoolkit.org/repositories/open_model_zoo/public/$OmzVersion/head-pose-estimation-adas-0001/head-pose-estimation-adas-0001.onnx"
    }
)

Write-Host "Downloading OpenVINO models to $Destination" -ForegroundColor Cyan

foreach ($model in $models) {
    $target = Join-Path $Destination $model.Name
    Write-Host "-> $($model.Name)" -ForegroundColor Green
    Invoke-WebRequest -Uri $model.Url -OutFile $target
}

Write-Host "Done." -ForegroundColor Cyan
