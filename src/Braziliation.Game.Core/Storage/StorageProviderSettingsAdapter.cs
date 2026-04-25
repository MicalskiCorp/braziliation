using System.Text;
using Braziliation.Settings;

namespace Braziliation.Storage;

/// <summary>
/// Adapts an <see cref="IStorageProvider"/> into the <see cref="ISettingsStorage"/> interface.
/// Settings are stored under the fixed key <c>"settings"</c>.
/// Byte arrays produced by the serialization layer are bridged to UTF-8 JSON strings
/// expected by <see cref="IStorageProvider"/>.
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
