using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.U2D.Sprites;
using UnityEngine;
using UnityEngine.Tilemaps;

namespace Braziliation.Editor.Art
{
    /// <summary>
    /// Importa um mapa gerado por <c>Design/ArteFonte/Ferramentas/gen_map_wfc.py</c>
    /// para um Tilemap da cena.
    ///
    /// Lê o companheiro <c>{mapa}.unity.json</c>, não o <c>{mapa}.map.json</c>: o
    /// primeiro é o formato de máquina, só com arrays planos de primitivos, porque
    /// <see cref="JsonUtility"/> não desserializa dicionário nem array irregular — que
    /// é exatamente o que o .map.json (formato legível) usa.
    ///
    /// O que faz, em ordem: garante que cada tileset esteja fatiado em grade
    /// (linhas = tipos, colunas = variações), cria/reusa um <see cref="Tile"/> por
    /// célula da grade, e pinta o Tilemap. Reimportar o mesmo mapa reusa os Tiles
    /// já criados em vez de duplicar.
    /// </summary>
    public static class WfcMapImporter
    {
        /// <summary>Espelha o JSON emitido por <c>write_unity_map()</c> no lado Python.</summary>
        [System.Serializable]
        private sealed class WfcMapData
        {
            public string ruleset;
            public int width;
            public int height;
            public int tileSize;
            public string[] tilesetNames;
            public string[] tilesetAssetPaths;
            public int[] tilesetVariations;
            public int[] tilesetRows;
            public string[] tileIds;
            public int[] tileFamily;   // índice em tilesetNames; -1 = tile vazio (céu/ar)
            public int[] tileRow;      // linha dentro do tileset; -1 quando vazio
            public int[] cells;        // width*height, índice em tileIds, row-major do TOPO
            public int[] cellVariation;// width*height, coluna do tileset; -1 quando vazio
        }

        [MenuItem("Assets/Braziliation/Importar Mapa WFC...")]
        public static void ImportMap()
        {
            var path = EditorUtility.OpenFilePanel(
                "Selecione o mapa WFC (.unity.json)", Application.dataPath, "json");
            if (string.IsNullOrEmpty(path))
            {
                return;
            }

            if (!path.EndsWith(".unity.json"))
            {
                EditorUtility.DisplayDialog(
                    "Arquivo errado",
                    "Selecione o arquivo *.unity.json — é o formato de máquina.\n\n" +
                    "O *.map.json ao lado dele é a versão legível e não é lida por este importer.",
                    "Ok");
                return;
            }

            var map = JsonUtility.FromJson<WfcMapData>(File.ReadAllText(path));
            if (map == null || map.cells == null || map.cells.Length == 0)
            {
                EditorUtility.DisplayDialog("Mapa inválido", $"Não foi possível ler:\n{path}", "Ok");
                return;
            }

            var expected = map.width * map.height;
            if (map.cells.Length != expected)
            {
                EditorUtility.DisplayDialog(
                    "Mapa inconsistente",
                    $"O mapa declara {map.width}x{map.height} = {expected} células, " +
                    $"mas traz {map.cells.Length}. Regere com gen_map_wfc.py.",
                    "Ok");
                return;
            }

            var sprites = new Dictionary<int, Sprite[]>();
            for (int i = 0; i < map.tilesetAssetPaths.Length; i++)
            {
                var assetPath = map.tilesetAssetPaths[i];
                if (string.IsNullOrEmpty(assetPath))
                {
                    Debug.LogError(
                        $"[WfcMapImporter] Tileset '{map.tilesetNames[i]}' não está dentro de Assets/. " +
                        "O ruleset precisa apontar o 'sheet' para um PNG do projeto Unity.");
                    return;
                }

                EnsureSlicedAsGrid(assetPath, map.tilesetRows[i], map.tilesetVariations[i], map.tileSize);
                sprites[i] = LoadSpritesInGridOrder(assetPath);
                if (sprites[i].Length == 0)
                {
                    Debug.LogError($"[WfcMapImporter] Nenhum sprite fatiado em {assetPath}.");
                    return;
                }
            }

            var tilemap = CreateTilemapObject(map.ruleset);
            var tileCache = new Dictionary<Sprite, Tile>();
            int painted = 0;

            for (int index = 0; index < map.cells.Length; index++)
            {
                var tileIndex = map.cells[index];
                var family = map.tileFamily[tileIndex];
                if (family < 0)
                {
                    continue; // tile vazio: não pinta, deixa o fundo aparecer
                }

                var column = Mathf.Max(0, map.cellVariation[index]);
                var spriteIndex = map.tileRow[tileIndex] * map.tilesetVariations[family] + column;
                var pool = sprites[family];
                if (spriteIndex < 0 || spriteIndex >= pool.Length)
                {
                    Debug.LogWarning(
                        $"[WfcMapImporter] Sprite {spriteIndex} fora do tileset " +
                        $"'{map.tilesetNames[family]}' ({pool.Length} sprites). Célula pulada.");
                    continue;
                }

                var tile = GetOrCreateTile(pool[spriteIndex], tileCache);

                // O JSON é row-major a partir do TOPO; no Unity o Y cresce para cima.
                int x = index % map.width;
                int yFromTop = index / map.width;
                tilemap.SetTile(new Vector3Int(x, map.height - 1 - yFromTop, 0), tile);
                painted++;
            }

            AssetDatabase.SaveAssets();
            Selection.activeGameObject = tilemap.gameObject;
            Debug.Log($"[WfcMapImporter] '{map.ruleset}' importado: {map.width}x{map.height}, " +
                      $"{painted} células pintadas, {tileCache.Count} tiles distintos.");
        }

        /// <summary>
        /// Fatia o tileset em grade se ainda não estiver na contagem esperada.
        /// Sai cedo quando já está fatiado, para não regerar GUIDs de sprite e quebrar
        /// referências de Tiles já criados — mesma precaução do <see cref="SheetAutoSlicer"/>.
        /// </summary>
        private static void EnsureSlicedAsGrid(string assetPath, int rows, int columns, int tileSize)
        {
            var importer = AssetImporter.GetAtPath(assetPath) as TextureImporter;
            if (importer == null)
            {
                Debug.LogError($"[WfcMapImporter] Não é uma textura: {assetPath}");
                return;
            }

            var factory = new SpriteDataProviderFactories();
            factory.Init();
            var provider = factory.GetSpriteEditorDataProviderFromObject(importer);
            provider.InitSpriteEditorDataProvider();

            int expected = rows * columns;
            if (importer.spriteImportMode == SpriteImportMode.Multiple
                && provider.GetSpriteRects().Length == expected)
            {
                return;
            }

            importer.spriteImportMode = SpriteImportMode.Multiple;

            var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(assetPath);
            int textureHeight = texture != null ? texture.height : rows * tileSize;

            var name = Path.GetFileNameWithoutExtension(assetPath);
            var rects = new List<SpriteRect>(expected);
            var pairs = new List<SpriteNameFileIdPair>(expected);

            for (int row = 0; row < rows; row++)
            {
                for (int col = 0; col < columns; col++)
                {
                    var id = GUID.Generate();
                    var spriteName = $"{name}_{row}_{col}";
                    rects.Add(new SpriteRect
                    {
                        name = spriteName,
                        spriteID = id,
                        // O retângulo do Unity conta a partir do rodapé da textura;
                        // a linha 0 do tileset é a de cima.
                        rect = new Rect(col * tileSize, textureHeight - (row + 1) * tileSize, tileSize, tileSize),
                        alignment = SpriteAlignment.Center,
                        pivot = new Vector2(0.5f, 0.5f),
                    });
                    pairs.Add(new SpriteNameFileIdPair(spriteName, id));
                }
            }

            provider.SetSpriteRects(rects.ToArray());
            provider.GetDataProvider<ISpriteNameFileIdDataProvider>()?.SetNameFileIdPairs(pairs);
            provider.Apply();
            AssetDatabase.ImportAsset(assetPath, ImportAssetOptions.ForceUpdate);
        }

        /// <summary>
        /// Carrega os sprites do tileset na ordem de grade (linha 0 primeiro, da esquerda
        /// para a direita), que é a ordem que o índice do mapa assume.
        /// </summary>
        private static Sprite[] LoadSpritesInGridOrder(string assetPath)
        {
            var loaded = new List<Sprite>();
            foreach (var asset in AssetDatabase.LoadAllAssetsAtPath(assetPath))
            {
                if (asset is Sprite sprite)
                {
                    loaded.Add(sprite);
                }
            }

            // LoadAllAssetsAtPath não garante ordem; o sufixo _{row}_{col} do slicing
            // é a fonte de verdade, então ordena por ele.
            loaded.Sort((a, b) => string.CompareOrdinal(a.name, b.name));
            return loaded.ToArray();
        }

        /// <summary>
        /// Cria (ou reusa) o asset de <see cref="Tile"/> de um sprite. Precisa ser asset
        /// em disco: um Tile só em memória não sobrevive ao reload da cena, e o Tilemap
        /// salvo apontaria para nada.
        /// </summary>
        private static Tile GetOrCreateTile(Sprite sprite, Dictionary<Sprite, Tile> cache)
        {
            if (cache.TryGetValue(sprite, out var cached))
            {
                return cached;
            }

            var sheetPath = AssetDatabase.GetAssetPath(sprite);
            var folder = Path.Combine(Path.GetDirectoryName(sheetPath) ?? "Assets", "Tiles")
                .Replace('\\', '/');
            if (!AssetDatabase.IsValidFolder(folder))
            {
                AssetDatabase.CreateFolder(Path.GetDirectoryName(sheetPath)?.Replace('\\', '/'), "Tiles");
            }

            var tilePath = $"{folder}/{sprite.name}.asset";
            var tile = AssetDatabase.LoadAssetAtPath<Tile>(tilePath);
            if (tile == null)
            {
                tile = ScriptableObject.CreateInstance<Tile>();
                tile.sprite = sprite;
                AssetDatabase.CreateAsset(tile, tilePath);
            }
            else if (tile.sprite != sprite)
            {
                tile.sprite = sprite;
                EditorUtility.SetDirty(tile);
            }

            cache[sprite] = tile;
            return tile;
        }

        private static Tilemap CreateTilemapObject(string rulesetName)
        {
            var root = new GameObject($"WFC_{rulesetName}");
            var grid = root.AddComponent<Grid>();
            // 32 PPU com tile de 32 px = 1 unidade Unity por célula (ADR-004).
            grid.cellSize = Vector3.one;

            var layer = new GameObject("Tilemap");
            layer.transform.SetParent(root.transform, false);
            var tilemap = layer.AddComponent<Tilemap>();
            layer.AddComponent<TilemapRenderer>();

            Undo.RegisterCreatedObjectUndo(root, "Importar Mapa WFC");
            return tilemap;
        }
    }
}
