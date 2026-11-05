using System;
using System.IO;
using UnityEngine;

namespace Braziliation.Editor.Art
{
    /// <summary>
    /// O JSON lateral de um sheet gerado pelo pxfx (ADR-016): <c>{nome}_sheet.json</c> ao lado do
    /// <c>{nome}_sheet.png</c>. Diz o tamanho de cada quadro (que não precisa ser quadrado), o pivô em
    /// pixels a partir do canto superior esquerdo do quadro, a duração de cada quadro (os "segurados"
    /// da antecipação e do impacto) e se a animação é loop. Sem o JSON, o slicer e o gerador de clipe
    /// seguem a convenção antiga (quadros quadrados, pivô no centro-inferior, 8 fps).
    /// Os campos espelham o formato "braziliation-sheet/1" de Design/ArteFonte/Ferramentas/pxfx.
    /// </summary>
    [Serializable]
    public sealed class SheetMetadata
    {
        public string formato;
        public string imagem;
        public int[] quadro;
        public int quadros;
        public int[] pivo;
        public bool loop;
        public int fps;
        public int[] duracoes_ms;

        public int FrameWidth => quadro != null && quadro.Length == 2 ? quadro[0] : 0;
        public int FrameHeight => quadro != null && quadro.Length == 2 ? quadro[1] : 0;

        /// <summary>Pivô normalizado do Unity (origem embaixo à esquerda).</summary>
        public Vector2 NormalizedPivot
        {
            get
            {
                if (pivo == null || pivo.Length != 2 || FrameWidth <= 0 || FrameHeight <= 0)
                {
                    return new Vector2(0.5f, 0f);
                }

                return new Vector2((float)pivo[0] / FrameWidth, 1f - (float)pivo[1] / FrameHeight);
            }
        }

        /// <summary>Lê o JSON ao lado da textura; falso se não existe ou não é do formato do pxfx.</summary>
        public static bool TryLoadFor(string texturePath, out SheetMetadata meta)
        {
            meta = null;
            var jsonPath = Path.ChangeExtension(texturePath, ".json");
            if (!File.Exists(jsonPath))
            {
                return false;
            }

            try
            {
                meta = JsonUtility.FromJson<SheetMetadata>(File.ReadAllText(jsonPath));
            }
            catch (ArgumentException e)
            {
                Debug.LogWarning($"[SheetMetadata] JSON inválido em '{jsonPath}': {e.Message}");
                return false;
            }

            var valido = meta != null
                && meta.formato != null
                && meta.formato.StartsWith("braziliation-sheet/")
                && meta.FrameWidth > 0
                && meta.FrameHeight > 0
                && meta.quadros > 0;
            if (!valido)
            {
                meta = null;
            }

            return valido;
        }
    }
}
