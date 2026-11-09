using Braziliation.Settings;
using Xunit;

namespace Braziliation.Game.Tests;

/// <summary>
/// Qual família de glifo a UI mostra (ADR-017): a do dispositivo ativo, ou a preferência manual
/// do jogador quando ele joga de controle — o Steam Input entrega todo controle como Xbox.
/// </summary>
public sealed class GlyphRulesTests
{
    [Theory]
    [InlineData(GlyphStyle.Auto)]
    [InlineData(GlyphStyle.Xbox)]
    [InlineData(GlyphStyle.PlayStation)]
    [InlineData(GlyphStyle.Switch)]
    public void Keyboard_And_Mouse_Always_Show_Keyboard_Glyphs(GlyphStyle style)
    {
        Assert.Equal(ControllerFamily.KeyboardMouse, GlyphRules.Resolve(ControllerFamily.KeyboardMouse, style));
    }

    [Theory]
    [InlineData(ControllerFamily.Xbox)]
    [InlineData(ControllerFamily.PlayStation)]
    [InlineData(ControllerFamily.Switch)]
    public void Auto_Follows_The_Active_Controller(ControllerFamily device)
    {
        Assert.Equal(device, GlyphRules.Resolve(device, GlyphStyle.Auto));
    }

    [Theory]
    [InlineData(GlyphStyle.Xbox, ControllerFamily.Xbox)]
    [InlineData(GlyphStyle.PlayStation, ControllerFamily.PlayStation)]
    [InlineData(GlyphStyle.Switch, ControllerFamily.Switch)]
    public void Manual_Style_Overrides_What_Steam_Input_Reports(GlyphStyle style, ControllerFamily expected)
    {
        // Controle de PlayStation pelo Steam Input chega como Xbox; a preferência corrige o glifo.
        Assert.Equal(expected, GlyphRules.Resolve(ControllerFamily.Xbox, style));
    }

    [Fact]
    public void Undefined_Style_Behaves_As_Auto()
    {
        Assert.Equal(ControllerFamily.PlayStation, GlyphRules.Resolve(ControllerFamily.PlayStation, (GlyphStyle)77));
    }

    [Fact]
    public void Undefined_Device_Falls_Back_To_Xbox()
    {
        Assert.Equal(ControllerFamily.Xbox, GlyphRules.Resolve((ControllerFamily)77, GlyphStyle.Auto));
    }
}
