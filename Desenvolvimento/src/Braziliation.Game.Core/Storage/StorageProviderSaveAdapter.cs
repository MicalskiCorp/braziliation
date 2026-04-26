using System.Text;
using Braziliation.SaveSystem;

namespace Braziliation.Storage;

/// <summary>
/// Adapts an <see cref="IStorageProvider"/> into the <see cref="ISaveStorage"/> interface.
/// Slot indices are mapped to provider keys using the <c>save_N</c> convention
/// (e.g. slot 0 → key <c>"save_0"</c>).
/// Byte arrays produced by the serialization layer are bridged to UTF-8 JSON strings
/// expected by <see cref="IStorageProvider"/>.
/// </summary>
public sealed class StorageProviderSaveAdapter : ISaveStorage
{
    private readonly IStorageProvider _provider;
    private const string SlotKeyPrefix = "save_";

    public StorageProviderSaveAdapter(IStorageProvider provider)
    {
        if (provider is null) throw new ArgumentNullException(nameof(provider));
        _provider = provider;
    }

    /// <inheritdoc/>
    public void Write(int slotIndex, byte[] data) =>
        _provider.Save(SlotKeyPrefix + slotIndex, Encoding.UTF8.GetString(data));

    /// <inheritdoc/>
    public byte[]? Read(int slotIndex)
    {
        var json = _provider.Load(SlotKeyPrefix + slotIndex);
        return json is null ? null : Encoding.UTF8.GetBytes(json);
    }

    /// <inheritdoc/>
    public bool Exists(int slotIndex) =>
        _provider.Exists(SlotKeyPrefix + slotIndex);

    /// <inheritdoc/>
    public void Delete(int slotIndex) =>
        _provider.Delete(SlotKeyPrefix + slotIndex);
}
