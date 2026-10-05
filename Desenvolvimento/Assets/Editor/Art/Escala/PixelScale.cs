using System;
using System.Linq;

namespace Braziliation.Editor.Art
{
    /// <summary>
    /// Fonte única do PPU de importação durante a migração do ADR-011
    /// (640×360 @ 32 PPU → 960×540 @ 48 PPU).
    ///
    /// Por que existe: 1,5 não é escala inteira, então a arte não pode ser
    /// ampliada — precisa ser re-autorada asset a asset. Enquanto isso, o
    /// projeto convive com duas densidades. Se o PPU fosse global, virar a
    /// chave para 48 encolheria todo asset legado para 2/3 do tamanho em
    /// mundo e quebraria tilemap e colisão. Amarrando o PPU ao grid em que
    /// cada asset foi autorado, **o tamanho em mundo não muda** — o legado só
    /// parece menos denso ao lado do novo, que é exatamente o estado de
    /// transição que o ADR-011 prevê.
    ///
    /// Como usar: ao re-autorar um asset no grid de 48, **apague a linha dele
    /// de <see cref="Legado"/>** e reimporte. Quando a lista esvaziar, a
    /// migração acabou e esta classe pode virar uma constante só.
    /// </summary>
    public static class PixelScale
    {
        /// <summary>Grid atual — ADR-011.</summary>
        public const float Atual = 48f;

        /// <summary>Grid anterior — ADR-004, substituído.</summary>
        public const float Anterior = 32f;

        /// <summary>
        /// Assets ainda autorados no grid de 32. Só restam os placeholders CC0,
        /// que saem do projeto quando a arte própria os substituir — toda a arte
        /// própria já está no grid de 48 (ADR-011, concluído em 2026-10-05).
        /// </summary>
        public static readonly string[] Legado =
        {
            // Placeholders CC0 (Gothicvania) foram preparados por upscale x2 para 32 PPU.
            // Não serão re-autorados: saem do projeto quando a arte própria os substituir.
            "Assets/Art/ThirdParty/Gothicvania/Environments/env_placeholder_castelo_tileset.png",
            "Assets/Art/ThirdParty/Gothicvania/Resources/Demo/Sheets/chr_placeholder_heroi_idle_sheet.png",
            "Assets/Art/ThirdParty/Gothicvania/Resources/Demo/Sheets/chr_placeholder_heroi_run_sheet.png",
            "Assets/Art/ThirdParty/Gothicvania/Resources/Demo/Sheets/enm_placeholder_cao_idle_sheet.png",
            "Assets/Art/ThirdParty/Gothicvania/Resources/Demo/Sheets/enm_placeholder_cao_walk_sheet.png",
            "Assets/Art/ThirdParty/Gothicvania/Resources/Demo/chr_placeholder_heroi_idle.png",
            "Assets/Art/ThirdParty/Gothicvania/Resources/Demo/enm_placeholder_cao_idle.png",
            "Assets/Art/ThirdParty/Gothicvania/Resources/Demo/env_placeholder_chao_tile.png",
            "Assets/Art/ThirdParty/Gothicvania/Resources/Demo/env_placeholder_fundo_castelo.png",
        };

        /// <summary>PPU esperado para o asset no caminho dado.</summary>
        public static float Para(string assetPath)
        {
            var normalizado = assetPath.Replace('\\', '/');
            return Legado.Any(p => string.Equals(p, normalizado, StringComparison.OrdinalIgnoreCase))
                ? Anterior
                : Atual;
        }
    }
}
