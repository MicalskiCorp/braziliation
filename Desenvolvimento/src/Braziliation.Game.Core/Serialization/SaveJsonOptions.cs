using System.Text.Json;

namespace Braziliation.Serialization;

internal static class SaveJsonOptions
{
    /// <summary>
    /// Opções JSON compartilhadas para toda serialização de save e settings.
    /// - WriteIndented = false garante saída de bytes compacta e determinística (segura para Steam Cloud).
    /// - PropertyNameCaseInsensitive = true permite evolução de schema com compatibilidade futura.
    /// </summary>
    internal static readonly JsonSerializerOptions Default = new()
    {
        WriteIndented = false,
        PropertyNameCaseInsensitive = true,
    };
}
