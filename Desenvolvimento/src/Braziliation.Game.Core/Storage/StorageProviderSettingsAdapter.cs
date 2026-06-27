using System.Text;
using Braziliation.Settings;

namespace Braziliation.Storage;

/// <summary>
/// Adapta um <see cref="IStorageProvider"/> para a interface <see cref="ISettingsStorage"/>.
/// Configurações são armazenadas sob a chave fixa <c>"settings"</c>.
/// Arrays de bytes produzidos pela camada de serialização são convertidos para strings JSON UTF-8
/// esperadas por <see cref="IStorageProvider"/>.
/// </summary>
public sealed class StorageProviderSettingsAdapter : ISettingsStorage
{
    private readonly IStorageProvider _provider;
    private const string SettingsKey = "settings";

    public StorageProviderSettingsAdapter(IStorageProvider provider)
    {
        if (provider is null) throw new ArgumentNullException(nameof(provider));
        _provider = provider;
    }

    /// <inheritdoc/>
    public void Write(byte[] data) =>
        _provider.Save(SettingsKey, Encoding.UTF8.GetString(data));

    /// <inheritdoc/>
    public byte[]? Read()
    {
        var json = _provider.Load(SettingsKey);
        return json is null ? null : Encoding.UTF8.GetBytes(json);
    }
}
