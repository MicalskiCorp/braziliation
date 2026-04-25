namespace Braziliation.SaveSystem;

/// <summary>
/// Persistent data for a single save slot.
/// All fields must be JSON-serializable and free of Unity types
/// to ensure Steam Cloud compatibility and deterministic round-trips.
/// </summary>
public sealed class SaveSlot
{
    /// <summary>
    /// Increment whenever a breaking change is made to the save schema.
    /// <see cref="SaveGameService"/> rejects slots whose version does not match.
    /// </summary>
    public const int CurrentSchemaVersion = 1;

    /// <summary>Schema version written at save time. Validated on load.</summary>
    public int SchemaVersion { get; set; } = CurrentSchemaVersion;

    public int SlotIndex { get; set; }
    public string PlayerName { get; set; } = string.Empty;
    public double PlaytimeSeconds { get; set; }
    public DateTimeOffset LastSaved { get; set; }
    public string SceneName { get; set; } = string.Empty;
    public int CheckpointId { get; set; }
}
