namespace Braziliation.Settings;

/// <summary>
/// Família de glifo de controle que a UI mostra (ADR-017). <see cref="Auto"/> segue o dispositivo
/// ativo informado pelo <c>GameInput</c>; os outros forçam uma família, para quem joga com um controle
/// que chega como Xbox pelo Steam Input.
/// </summary>
/// <remarks>
/// O valor numérico é gravado no arquivo de settings: nunca renumerar nem reordenar. Valor novo entra
/// no fim, com o próximo número.
/// </remarks>
public enum GlyphStyle
{
    Auto = 0,
    Xbox = 1,
    PlayStation = 2,
    Switch = 3,
}
