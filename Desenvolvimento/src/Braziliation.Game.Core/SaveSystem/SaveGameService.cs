using System.Text.Json;
using Braziliation.Serialization;

namespace Braziliation.SaveSystem;

/// <summary>
/// Salva e carrega instâncias de <see cref="SaveSlot"/> por meio de um backend de armazenamento plugável.
/// Cada slot é independente; slots corrompidos ou ausentes retornam null em vez de lançar exceção.
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
