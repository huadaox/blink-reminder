using Microsoft.ML.OnnxRuntime;
using Microsoft.Windows.AI.MachineLearning;

namespace BlinkReminder.Native.Services;

public sealed class WindowsMlBootstrapper
{
    public async Task<OrtEnv> InitializeAsync(CancellationToken cancellationToken)
    {
        EnvironmentCreationOptions envOptions = new()
        {
            logId = "BlinkReminder",
            logLevel = OrtLoggingLevel.ORT_LOGGING_LEVEL_WARNING
        };

        var environment = OrtEnv.CreateInstanceWithOptions(ref envOptions);
        var catalog = ExecutionProviderCatalog.GetDefault();
        await catalog.EnsureAndRegisterCertifiedAsync().AsTask(cancellationToken);
        return environment;
    }
}
