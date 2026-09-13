using UnityEditor;

namespace Braziliation.Editor.Art
{
    /// <summary>
    /// Força os import settings de pixel art definidos em
    /// Design/GuiasDeArte (32 PPU — ADR-004, Point, sem compressão, sem mipmap)
    /// para toda textura que entrar em Assets/Art/.
    /// Garante que nenhum sprite chegue à cena com filtro ou compressão errados.
    /// </summary>
    public class SpriteImportPostprocessor : AssetPostprocessor
    {
        private const string ArtRoot = "Assets/Art/";
        private const float PixelsPerUnit = 32f;

        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(ArtRoot))
            {
                return;
            }

            var importer = (TextureImporter)assetImporter;
            importer.textureType = TextureImporterType.Sprite;
            importer.spritePixelsPerUnit = PixelsPerUnit;
            importer.filterMode = UnityEngine.FilterMode.Point;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.mipmapEnabled = false;
        }
    }
}
