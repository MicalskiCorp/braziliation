namespace Braziliation.Settings;

/// <summary>
/// Modelo de dados puro das configurações do jogador: volumes de áudio e controles.
/// Todos os volumes são limitados para [0, 1] na atribuição; NaN é tratado como 0.
/// Serializável via System.Text.Json sem dependência de Unity. Campo ausente no arquivo
/// (settings de uma versão anterior) carrega o padrão.
/// </summary>
public sealed class GameSettings
{
    private float _masterVolume = 1f;
    private float _musicVolume = 1f;
    private float _sfxVolume = 1f;
    private string _inputBindingOverrides = string.Empty;
    private GlyphStyle _glyphStyle = GlyphStyle.Auto;

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

    /// <summary>
    /// Overrides de binding do Input System (<c>SaveBindingOverridesAsJson</c>), guardados como texto
    /// opaco: o core não interpreta, só persiste (ADR-017). Vazio = bindings padrão do action map.
    /// Null vira vazio.
    /// </summary>
    public string InputBindingOverrides
    {
        get => _inputBindingOverrides;
        set => _inputBindingOverrides = value ?? string.Empty;
    }

    /// <summary>Preferência de glifo de controle. Valor fora do enum vira <see cref="GlyphStyle.Auto"/>.</summary>
    public GlyphStyle GlyphStyle
    {
        get => _glyphStyle;
        set => _glyphStyle = Enum.IsDefined(typeof(GlyphStyle), value) ? value : GlyphStyle.Auto;
    }

    /// <summary>Volta todas as configurações ao padrão, inclusive os controles.</summary>
    public void ResetToDefaults()
    {
        _masterVolume = 1f;
        _musicVolume = 1f;
        _sfxVolume = 1f;
        _inputBindingOverrides = string.Empty;
        _glyphStyle = GlyphStyle.Auto;
    }

    private static float ClampVolume(float value) =>
        float.IsNaN(value) ? 0f : Math.Clamp(value, 0f, 1f);
}
