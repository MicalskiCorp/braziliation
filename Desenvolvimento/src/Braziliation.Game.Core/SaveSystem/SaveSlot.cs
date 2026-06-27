namespace Braziliation.SaveSystem;

/// <summary>
/// Dados persistentes de um único slot de save.
/// Todos os campos devem ser serializáveis em JSON e sem tipos Unity
/// para garantir compatibilidade com Steam Cloud e round-trips determinísticos.
/// </summary>
public sealed class SaveSlot
{
    /// <summary>
    /// Incrementar sempre que houver mudança incompatível no schema de save.
    /// <see cref="SaveGameService"/> rejeita slots cuja versão não corresponda.
    /// </summary>
    public const int CurrentSchemaVersion = 1;

    /// <summary>Versão de schema gravada no momento do save. Validada no carregamento.</summary>
    public int SchemaVersion { get; set; } = CurrentSchemaVersion;

    public int SlotIndex { get; set; }
    public string PlayerName { get; set; } = string.Empty;
    public double PlaytimeSeconds { get; set; }
    public DateTimeOffset LastSaved { get; set; }
    public string SceneName { get; set; } = string.Empty;
    public int CheckpointId { get; set; }
}
