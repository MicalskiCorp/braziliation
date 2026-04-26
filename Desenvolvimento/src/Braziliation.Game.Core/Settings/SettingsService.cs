using System.Text.Json;
using Braziliation.Serialization;

namespace Braziliation.Settings;

/// <summary>
/// Saves and loads <see cref="GameSettings"/> through a pluggable storage backend.
/// Corrupted or missing data silently returns default settings (all volumes = 1).
/// </summary>
public sealed class SettingsService
{
    private readonly ISettingsStorage _storage;

    public SettingsService(ISettingsStorage storage)
    {
        if (storage is null) throw new ArgumentNullException(nameof(storage));
        _storage = storage;
    }

    public void Save(GameSettings settings)
    {
        if (settings is null) throw new ArgumentNullException(nameof(settings));
        var bytes = JsonSerializer.SerializeToUtf8Bytes(settings, SaveJsonOptions.Default);
        _storage.Write(bytes);
    }

    public GameSettings Load()
    {
        var bytes = _storage.Read();
        if (bytes is null || bytes.Length == 0)
            return new GameSettings();

        try
        {
            return JsonSerializer.Deserialize<GameSettings>(bytes, SaveJsonOptions.Default)
                   ?? new GameSettings();
        }
        catch (JsonException)
        {
            return new GameSettings();
        }
    }
}
