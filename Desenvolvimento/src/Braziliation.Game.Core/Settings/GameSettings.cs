namespace Braziliation.Settings;

/// <summary>
/// Pure-data settings model for audio volumes.
/// All volumes are clamped to [0, 1] on assignment; NaN is treated as 0.
/// Serializable via System.Text.Json with no Unity dependency.
/// </summary>
public sealed class GameSettings
{
    private float _masterVolume = 1f;
    private float _musicVolume = 1f;
    private float _sfxVolume = 1f;

    public float MasterVolume
    {
        get => _masterVolume;
        set => _masterVolume = ClampVolume(value);
    }

    public float MusicVolume
    {
        get => _musicVolume;
        set => _musicVolume = ClampVolume(value);
    }

    public float SfxVolume
    {
        get => _sfxVolume;
        set => _sfxVolume = ClampVolume(value);
    }

    public void ResetToDefaults()
    {
        _masterVolume = 1f;
        _musicVolume = 1f;
        _sfxVolume = 1f;
    }

    private static float ClampVolume(float value) =>
        float.IsNaN(value) ? 0f : Math.Clamp(value, 0f, 1f);
}
