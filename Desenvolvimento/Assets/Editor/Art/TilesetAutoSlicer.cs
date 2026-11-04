using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.U2D.Sprites;
using UnityEngine;

namespace Braziliation.Editor.Art
{
    /// <summary>
    /// Fatia automaticamente tilesets placeholder que entram em
    /// Assets/Art/ThirdParty/. Convenção: arquivos "*_tileset.png" viram
    /// Sprite Mode Multiple, fatiados em grid de {PixelScale.Para(asset)} x
    /// {mesmo valor}, com nomes "{nome}_{col}_{row}" (col/row contados a
    /// partir do canto superior esquerdo). Espelha o
    /// <see cref="SheetAutoSlicer"/>, mas para folhas de tile (grid completo)
    /// em vez de folhas de animação (uma linha).
    ///
    /// Escopo restrito a ThirdParty de propósito: os tilesets próprios em
    /// Assets/Art/Environments/ (ex.: env_blumenau_*_tileset.png) já têm
    /// fatiamento autorado à mão com outra convenção de nomes — rodar este
    /// postprocessor neles reatribuiria GUID novo a cada sprite e quebraria
    /// qualquer Tile/Tilemap que já referencie os antigos (visto na prática
    /// nesta sessão: 2026-11-04, revertido antes do commit).
    /// </summary>
    public class TilesetAutoSlicer : AssetPostprocessor
    {
        private const string ArtRoot = "Assets/Art/ThirdParty/";

        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(ArtRoot) || !assetPath.EndsWith(".png"))
            {
                return;
            }

            var name = Path.GetFileNameWithoutExtension(assetPath);
            if (!name.EndsWith("_tileset"))
            {
                return;
            }

            var (width, height) = ReadPngSize(assetPath);
            var cell = Mathf.RoundToInt(PixelScale.Para(assetPath));
            if (cell <= 0 || width <= 0 || height <= 0 || width % cell != 0 || height % cell != 0)
            {
                return;
            }

            var importer = (TextureImporter)assetImporter;
            importer.spriteImportMode = SpriteImportMode.Multiple;

            int cols = width / cell;
            int rows = height / cell;

            var factory = new SpriteDataProviderFactories();
            factory.Init();
            var provider = factory.GetSpriteEditorDataProviderFromObject(importer);
            provider.InitSpriteEditorDataProvider();

            // Mesma guarda do SheetAutoSlicer: conferir contagem E tamanho do
            // rect, não só a contagem, para não deixar slicing velho sobrevivendo
            // a uma textura redesenhada no mesmo número de células.
            var existingRects = provider.GetSpriteRects();
            bool alreadySlicedAtCurrentGrid = existingRects.Length == cols * rows
                && existingRects.Length > 0
                && Mathf.RoundToInt(existingRects[0].rect.width) == cell
                && Mathf.RoundToInt(existingRects[0].rect.height) == cell;
            if (alreadySlicedAtCurrentGrid)
            {
                return;
            }

            var rects = new List<SpriteRect>(cols * rows);
            var pairs = new List<SpriteNameFileIdPair>(cols * rows);
            for (int row = 0; row < rows; row++)
            {
                for (int col = 0; col < cols; col++)
                {
                    var id = GUID.Generate();
                    var spriteName = $"{name}_{col}_{row}";
                    rects.Add(new SpriteRect
                    {
                        name = spriteName,
                        spriteID = id,
                        rect = new Rect(col * cell, height - (row + 1) * cell, cell, cell),
                        alignment = SpriteAlignment.Center,
                        pivot = new Vector2(0.5f, 0.5f),
                    });
                    pairs.Add(new SpriteNameFileIdPair(spriteName, id));
                }
            }

            provider.SetSpriteRects(rects.ToArray());
            var nameFileId = provider.GetDataProvider<ISpriteNameFileIdDataProvider>();
            nameFileId?.SetNameFileIdPairs(pairs);
            provider.Apply();
        }

        private static (int width, int height) ReadPngSize(string path)
        {
            using var stream = File.OpenRead(path);
            var buffer = new byte[24];
            if (stream.Read(buffer, 0, 24) < 24)
            {
                return (0, 0);
            }

            int width = (buffer[16] << 24) | (buffer[17] << 16) | (buffer[18] << 8) | buffer[19];
            int height = (buffer[20] << 24) | (buffer[21] << 16) | (buffer[22] << 8) | buffer[23];
            return (width, height);
        }
    }
}
