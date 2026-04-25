using System.Text.Json;
using Braziliation.Serialization;

namespace Braziliation.SaveSystem;

/// <summary>
/// Saves and loads <see cref="SaveSlot"/> instances through a pluggable storage backend.
/// Each slot is independent; corrupted or missing slots return null rather than throwing.
/// </summary>
public sealed class SaveGameService
{
    private readonly ISaveStorage _storage;

    public SaveGameService(ISaveStorage storage)
    {
        if (storage is null) throw new ArgumentNullException(nameof(storage));
        _storage = storage;
    }

    public void Save(SaveSlot slot)
    {
        if (slot is null) throw new ArgumentNullException(nameof(slot));
        var bytes = JsonSerializer.SerializeToUtf8Bytes(slot, SaveJsonOptions.Default);
        _storage.Write(slot.SlotIndex, bytes);
    }

    public SaveSlot? Load(int slotIndex)
    {
        var bytes = _storage.Read(slotIndex);
        if (bytes is null || bytes.Length == 0)
            return null;

        try
        {
            var slot = JsonSerializer.Deserialize<SaveSlot>(bytes, SaveJsonOptions.Default);
            if (slot is null || slot.SchemaVersion != SaveSlot.CurrentSchemaVersion)
                return null;
            return slot;
        }
        catch (JsonException)
        {
            return null;
        }
    }

    public bool SlotExists(int slotIndex) => _storage.Exists(slotIndex);

    public void DeleteSlot(int slotIndex) => _storage.Delete(slotIndex);
}
