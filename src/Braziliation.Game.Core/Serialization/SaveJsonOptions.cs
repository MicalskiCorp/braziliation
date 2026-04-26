using System.Text.Json;

namespace Braziliation.Serialization;

internal static class SaveJsonOptions
{
    /// <summary>
    /// Shared JSON options for all save and settings serialization.
    /// - WriteIndented = false ensures compact, deterministic byte output (Steam Cloud safe).
    /// - PropertyNameCaseInsensitive = true allows forward-compatible schema evolution.
    /// </summary>
    internal static readonly JsonSerializerOptions Default = new()
    {
        WriteIndented = false,
        PropertyNameCaseInsensitive = true,
    };
//teste
}
