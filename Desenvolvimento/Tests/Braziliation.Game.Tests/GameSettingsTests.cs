using Braziliation.Settings;
using Xunit;

namespace Braziliation.Game.Tests;

public sealed class GameSettingsTests
{
    // ── Defaults ──────────────────────────────────────────────────────────────

    [Fact]
    public void Constructor_DefaultMasterVolume_IsOne()
    {
        var s = new GameSettings();
        Assert.Equal(1f, s.MasterVolume);
    }

    [Fact]
    public void Constructor_DefaultMusicVolume_IsOne()
    {
        var s = new GameSettings();
        Assert.Equal(1f, s.MusicVolume);
    }

    [Fact]
    public void Constructor_DefaultSfxVolume_IsOne()
    {
        var s = new GameSettings();
        Assert.Equal(1f, s.SfxVolume);
    }

    // ── MasterVolume clamping ─────────────────────────────────────────────────

    [Theory]
    [InlineData(-0.001f)]
    [InlineData(-1f)]
    [InlineData(-100f)]
    [InlineData(float.NegativeInfinity)]
    public void MasterVolume_SetBelowZero_ClampsToZero(float value)
    {
        var s = new GameSettings { MasterVolume = value };
        Assert.Equal(0f, s.MasterVolume);
    }

    [Theory]
    [InlineData(1.001f)]
    [InlineData(2f)]
    [InlineData(100f)]
    [InlineData(float.PositiveInfinity)]
    public void MasterVolume_SetAboveOne_ClampsToOne(float value)
    {
        var s = new GameSettings { MasterVolume = value };
        Assert.Equal(1f, s.MasterVolume);
    }

    [Theory]
    [InlineData(0f)]
    [InlineData(0.25f)]
    [InlineData(0.5f)]
    [InlineData(0.75f)]
    [InlineData(1f)]
    public void MasterVolume_SetValidValue_IsPreserved(float value)
    {
        var s = new GameSettings { MasterVolume = value };
        Assert.Equal(value, s.MasterVolume);
    }

    [Fact]
    public void MasterVolume_SetNaN_ClampsToZero()
    {
        var s = new GameSettings { MasterVolume = float.NaN };
        Assert.Equal(0f, s.MasterVolume);
    }

    // ── MusicVolume clamping ──────────────────────────────────────────────────

    [Theory]
    [InlineData(-1f, 0f)]
    [InlineData(2f, 1f)]
    [InlineData(0.5f, 0.5f)]
    public void MusicVolume_Clamping_IsCorrect(float input, float expected)
    {
        var s = new GameSettings { MusicVolume = input };
        Assert.Equal(expected, s.MusicVolume);
    }

    [Fact]
    public void MusicVolume_SetNaN_ClampsToZero()
    {
        var s = new GameSettings { MusicVolume = float.NaN };
        Assert.Equal(0f, s.MusicVolume);
    }

    // ── SfxVolume clamping ────────────────────────────────────────────────────

    [Theory]
    [InlineData(-1f, 0f)]
    [InlineData(2f, 1f)]
    [InlineData(0.5f, 0.5f)]
    public void SfxVolume_Clamping_IsCorrect(float input, float expected)
    {
        var s = new GameSettings { SfxVolume = input };
        Assert.Equal(expected, s.SfxVolume);
    }

    [Fact]
    public void SfxVolume_SetNaN_ClampsToZero()
    {
        var s = new GameSettings { SfxVolume = float.NaN };
        Assert.Equal(0f, s.SfxVolume);
    }

    // ── ResetToDefaults ───────────────────────────────────────────────────────

    [Fact]
    public void ResetToDefaults_RestoresAllVolumesToOne()
    {
        var s = new GameSettings { MasterVolume = 0.2f, MusicVolume = 0.4f, SfxVolume = 0.6f };
        s.ResetToDefaults();
        Assert.Equal(1f, s.MasterVolume);
        Assert.Equal(1f, s.MusicVolume);
        Assert.Equal(1f, s.SfxVolume);
    }

    // ── Independence ──────────────────────────────────────────────────────────

    [Fact]
    public void Volumes_AreIndependent_ChangingOneDoesNotAffectOthers()
    {
        var s = new GameSettings { MasterVolume = 0.2f };
        Assert.Equal(1f, s.MusicVolume);
        Assert.Equal(1f, s.SfxVolume);
    }

    [Fact]
    public void TwoInstances_HaveIndependentState()
    {
        var a = new GameSettings { MasterVolume = 0.1f };
        var b = new GameSettings { MasterVolume = 0.9f };
        Assert.Equal(0.1f, a.MasterVolume);
        Assert.Equal(0.9f, b.MasterVolume);
    }


    // ── Controles: overrides de binding e estilo de glifo (ADR-017) ──────────

    [Fact]
    public void Constructor_DefaultInputBindingOverrides_IsEmpty()
    {
        Assert.Equal(string.Empty, new GameSettings().InputBindingOverrides);
    }

    [Fact]
    public void Constructor_DefaultGlyphStyle_IsAuto()
    {
        Assert.Equal(GlyphStyle.Auto, new GameSettings().GlyphStyle);
    }

    [Fact]
    public void InputBindingOverrides_SetNull_BecomesEmpty()
    {
        var s = new GameSettings { InputBindingOverrides = null! };
        Assert.Equal(string.Empty, s.InputBindingOverrides);
    }

    [Theory]
    [InlineData(GlyphStyle.Auto)]
    [InlineData(GlyphStyle.Xbox)]
    [InlineData(GlyphStyle.PlayStation)]
    [InlineData(GlyphStyle.Switch)]
    public void GlyphStyle_SetDefinedValue_IsKept(GlyphStyle style)
    {
        Assert.Equal(style, new GameSettings { GlyphStyle = style }.GlyphStyle);
    }

    [Fact]
    public void GlyphStyle_SetUndefinedValue_FallsBackToAuto()
    {
        var s = new GameSettings { GlyphStyle = (GlyphStyle)99 };
        Assert.Equal(GlyphStyle.Auto, s.GlyphStyle);
    }

    [Fact]
    public void GlyphStyle_PersistedValues_NeverChange()
    {
        // O valor numérico vai para o arquivo de settings: renumerar muda a preferência de quem já jogou.
        Assert.Equal(0, (int)GlyphStyle.Auto);
        Assert.Equal(1, (int)GlyphStyle.Xbox);
        Assert.Equal(2, (int)GlyphStyle.PlayStation);
        Assert.Equal(3, (int)GlyphStyle.Switch);
    }

    [Fact]
    public void ResetToDefaults_ClearsControlsToo()
    {
        var s = new GameSettings
        {
            MasterVolume = 0.3f,
            InputBindingOverrides = "{\"bindings\":[]}",
            GlyphStyle = GlyphStyle.PlayStation,
        };

        s.ResetToDefaults();

        Assert.Equal(1f, s.MasterVolume);
        Assert.Equal(string.Empty, s.InputBindingOverrides);
        Assert.Equal(GlyphStyle.Auto, s.GlyphStyle);
    }
}
