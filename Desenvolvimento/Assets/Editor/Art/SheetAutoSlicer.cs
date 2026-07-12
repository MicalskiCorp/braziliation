using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.U2D.Sprites;
using UnityEngine;

namespace Braziliation.Editor.Art
{
    /// <summary>
    /// Fatia automaticamente spritesheets que entram em Assets/Art/.
    /// Convenção (animation-guide.md): arquivos "*_sheet.png" são sheets
    /// horizontais de frames quadrados (largura múltipla da altura).
    /// Aplica Sprite Mode Multiple + grid de {altura}x{altura} com pivot
    /// bottom-center, preservando os IDs quando o sheet já está fatiado
    /// (para não quebrar AnimationClips existentes).
    /// </summary>
    public class SheetAutoSlicer : AssetPostprocessor
    {
        private const string ArtRoot = "Assets/Art/";

        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(ArtRoot) || !assetPath.EndsWith(".png"))
            {
                return;
            }

            var name = Path.GetFileNameWithoutExtension(assetPath);
            if (!name.EndsWith("_sheet"))
            {
                return;
            }

            var (width, height) = ReadPngSize(assetPath);
            if (height <= 0 || width <= height || width % height != 0)
            {
                return;
            }

            var importer = (TextureImporter)assetImporter;
            importer.spriteImportMode = SpriteImportMode.Multiple;

            var factory = new SpriteDataProviderFactories();
            factory.Init();
            var provider = factory.GetSpriteEditorDataProviderFromObject(importer);
            provider.InitSpriteEditorDataProvider();

            int frames = width / height;
            if (provider.GetSpriteRects().Length == frames)
            {
                return;
            }

            var rects = new List<SpriteRect>(frames);
            var pairs = new List<SpriteNameFileIdPair>(frames);
            for (int i = 0; i < frames; i++)
            {
                var id = GUID.Generate();
                rects.Add(new SpriteRect
                {
                    name = $"{name}_{i}",
                    spriteID = id,
                    rect = new Rect(i * height, 0, height, height),
                    alignment = SpriteAlignment.BottomCenter,
                    pivot = new Vector2(0.5f, 0f),
                });
                pairs.Add(new SpriteNameFileIdPair($"{name}_{i}", id));
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
