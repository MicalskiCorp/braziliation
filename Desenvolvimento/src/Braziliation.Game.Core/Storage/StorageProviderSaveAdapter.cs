using System.Text;
using Braziliation.SaveSystem;

namespace Braziliation.Storage;

/// <summary>
/// Adapta um <see cref="IStorageProvider"/> para a interface <see cref="ISaveStorage"/>.
/// Índices de slot são mapeados para chaves do provedor usando a convenção <c>save_N</c>
/// (ex.: slot 0 → chave <c>"save_0"</c>).
/// Arrays de bytes produzidos pela camada de serialização são convertidos para strings JSON UTF-8
/// esperadas por <see cref="IStorageProvider"/>.
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
