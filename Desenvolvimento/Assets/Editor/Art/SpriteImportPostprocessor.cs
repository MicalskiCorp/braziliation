using UnityEditor;

namespace Braziliation.Editor.Art
{
    /// <summary>
    /// Força os import settings de pixel art definidos em
    /// Design/GuiasDeArte (Point, sem compressão, sem mipmap) para toda textura
    /// que entrar em Assets/Art/. O PPU vem de <see cref="PixelScale"/>: 48 para
    /// o grid atual (ADR-011) e 32 para o que ainda não foi re-autorado.
    /// Garante que nenhum sprite chegue à cena com filtro ou compressão errados.
    /// </summary>
    public class SpriteImportPostprocessor : AssetPostprocessor
    {
        private const string ArtRoot = "Assets/Art/";

        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(ArtRoot))
            {
                return;
            }

            var importer = (TextureImporter)assetImporter;
            importer.textureType = TextureImporterType.Sprite;
            importer.spritePixelsPerUnit = PixelScale.Para(assetPath);
            importer.filterMode = UnityEngine.FilterMode.Point;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.mipmapEnabled = false;
        }
    }
}
