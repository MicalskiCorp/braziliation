using UnityEngine;
using UnityEngine.UI;

namespace Braziliation.UI
{
    /// <summary>
    /// Padrão único de <see cref="CanvasScaler"/> do projeto (ADR-011): Scale With Screen Size sobre a
    /// resolução de referência 960×540, Match 0.5. Todo código que cria canvas passa por aqui; o
    /// <c>AddComponent&lt;CanvasScaler&gt;()</c> cru deixa o padrão do Unity (Constant Pixel Size,
    /// referência 800×600), que foi como o <c>HUD_Demo</c> ficou para trás.
    /// </summary>
    /// <remarks>
    /// Layout de UI se escreve em pixels dessa referência. Em 1920×1080 tudo sai ×2, a escala inteira
    /// que mantém o pixel art nítido.
    /// </remarks>
    public static class UiCanvasScaling
    {
        public const float ReferenceWidth = 960f;
        public const float ReferenceHeight = 540f;
        public const float MatchWidthOrHeight = 0.5f;

        public static Vector2 ReferenceResolution => new Vector2(ReferenceWidth, ReferenceHeight);

        /// <summary>Configura o <see cref="CanvasScaler"/> do objeto, criando-o se faltar.</summary>
        public static CanvasScaler Apply(GameObject canvasObject)
        {
            var scaler = canvasObject.GetComponent<CanvasScaler>();
            if (scaler == null)
                scaler = canvasObject.AddComponent<CanvasScaler>();

            Apply(scaler);
            return scaler;
        }

        /// <summary>Aplica o padrão do projeto a um <see cref="CanvasScaler"/> existente. Idempotente.</summary>
        public static void Apply(CanvasScaler scaler)
        {
            scaler.uiScaleMode         = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = ReferenceResolution;
            scaler.screenMatchMode     = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            scaler.matchWidthOrHeight  = MatchWidthOrHeight;
        }
    }
}
