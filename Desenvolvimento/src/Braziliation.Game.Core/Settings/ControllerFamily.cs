namespace Braziliation.Settings;

/// <summary>
/// Família de dispositivo para escolher glifo (ADR-017): o que o <c>GameInput</c> detecta no último
/// input e o que a UI desenha. Com o Steam Input ligado, todo controle chega como <see cref="Xbox"/>.
/// </summary>
public enum ControllerFamily
{
    KeyboardMouse = 0,
    Xbox = 1,
    PlayStation = 2,
    Switch = 3,
}

/// <summary>Regra de glifo: função pura, testada no core; o Unity só detecta o dispositivo e aplica.</summary>
public static class GlyphRules
{
    /// <summary>
    /// Família de glifo a mostrar. Teclado e mouse mostram sempre glifo de teclado. De controle, a
    /// preferência manual (<see cref="GlyphStyle"/> diferente de <c>Auto</c>) vence o dispositivo
    /// detectado; no <c>Auto</c>, vale o detectado. Valor fora dos enums cai em Auto e em Xbox.
    /// </summary>
    public static ControllerFamily Resolve(ControllerFamily activeDevice, GlyphStyle style)
    {
        if (activeDevice == ControllerFamily.KeyboardMouse)
            return ControllerFamily.KeyboardMouse;

        switch (style)
        {
            case GlyphStyle.Xbox: return ControllerFamily.Xbox;
            case GlyphStyle.PlayStation: return ControllerFamily.PlayStation;
            case GlyphStyle.Switch: return ControllerFamily.Switch;
        }

        return activeDevice is ControllerFamily.Xbox or ControllerFamily.PlayStation or ControllerFamily.Switch
            ? activeDevice
            : ControllerFamily.Xbox;
    }
}
