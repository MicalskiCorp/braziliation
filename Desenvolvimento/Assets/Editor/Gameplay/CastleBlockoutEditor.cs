using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Braziliation.Editor.Art;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Tilemaps;

namespace Braziliation.Editor.Gameplay
{
    /// <summary>
    /// Cria/atualiza uma cena de blockout em Assets/Scenes/Sandbox/CastleBlockout.unity,
    /// fatiando (via <see cref="TilesetAutoSlicer"/>) e usando o tileset placeholder CC0
    /// `env_placeholder_castelo_tileset.png` para montar um corredor fechado com
    /// Tilemap + TilemapCollider2D. Objetivo: validar o fluxo de blockout de nível por
    /// Tilemap — não é arte final (placeholder de terceiros Gothicvania, ver CREDITS.md).
    /// </summary>
    public static class CastleBlockoutEditor
    {
        private const string ScenePath = "Assets/Scenes/Sandbox/CastleBlockout.unity";
        private const string TilesetPath = "Assets/Art/ThirdParty/Gothicvania/Environments/env_placeholder_castelo_tileset.png";
        private const string TilesFolder = "Assets/Art/ThirdParty/Gothicvania/Environments/Tiles";

        // Células escolhidas visualmente no tileset (col_row, origem no canto superior
        // esquerdo, fatiado por TilesetAutoSlicer): bloco escuro do fundo (arco/janela)
        // como parede; topo musgoso + fuste do pilar como piso em duas camadas.
        private const string WallSpriteName = "env_placeholder_castelo_tileset_22_4";
        private const string FloorCapSpriteName = "env_placeholder_castelo_tileset_21_9";
        private const string FloorShaftSpriteName = "env_placeholder_castelo_tileset_21_10";

        private const int RoomWidth = 20;
        private const int RoomHeight = 8;

        [MenuItem("Braziliation/Demo/Create or Update Castle Blockout Scene")]
        public static void CreateOrUpdateBlockoutScene()
        {
            AssetDatabase.ImportAsset(TilesetPath, ImportAssetOptions.ForceUpdate);

            // Os Tiles são carregados/criados DEPOIS do NewScene(..., Single) — carregá-los
            // antes invalida a referência em memória (o objeto fica "fake null", sem o
            // GC ainda ter rodado: NewScene descarrega a cena anterior e libera assets sem
            // outro holder). Custou um ciclo de depuração via `unity run_script` (sessão
            // 2026-11-04) — perder esse passo faz o Tilemap sair vazio sem nenhum erro.
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var sprites = AssetDatabase.LoadAllAssetsAtPath(TilesetPath)
                .OfType<Sprite>()
                .ToDictionary(s => s.name, s => s);

            var wallTile = GetOrCreateTile("CasteloBlockoutWall", sprites, WallSpriteName);
            var floorCapTile = GetOrCreateTile("CasteloBlockoutFloorCap", sprites, FloorCapSpriteName);
            var floorShaftTile = GetOrCreateTile("CasteloBlockoutFloorShaft", sprites, FloorShaftSpriteName);

            if (wallTile == null || floorCapTile == null || floorShaftTile == null)
            {
                Debug.LogError("[CastleBlockoutEditor] Abortado — tile(s) ausente(s). Confira o fatiamento do tileset.");
                return;
            }

            var gridObj = new GameObject("CastleBlockoutGrid");
            var grid = gridObj.AddComponent<Grid>();
            grid.cellSize = new Vector3(1f, 1f, 0f);

            var tilemapObj = new GameObject("Tilemap_Blockout");
            tilemapObj.transform.SetParent(gridObj.transform);
            var tilemap = tilemapObj.AddComponent<Tilemap>();
            tilemapObj.AddComponent<TilemapRenderer>();
            tilemapObj.AddComponent<TilemapCollider2D>();

            BuildRoom(tilemap, wallTile, floorCapTile, floorShaftTile);
            CreateCamera(gridObj.transform);

            EnsureFolder(Path.GetDirectoryName(ScenePath).Replace('\\', '/'));
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("[CastleBlockoutEditor] Blockout criado/atualizado em " + ScenePath);
        }

        private static void BuildRoom(Tilemap tilemap, TileBase wall, TileBase floorCap, TileBase floorShaft)
        {
            for (int x = 0; x < RoomWidth; x++)
            {
                tilemap.SetTile(new Vector3Int(x, 0, 0), floorShaft);
                tilemap.SetTile(new Vector3Int(x, 1, 0), floorCap);
            }

            for (int y = 1; y <= RoomHeight; y++)
            {
                tilemap.SetTile(new Vector3Int(-1, y, 0), wall);
                tilemap.SetTile(new Vector3Int(RoomWidth, y, 0), wall);
            }

            for (int x = -1; x <= RoomWidth; x++)
            {
                tilemap.SetTile(new Vector3Int(x, RoomHeight + 1, 0), wall);
            }
        }

        private static TileBase GetOrCreateTile(string tileName, Dictionary<string, Sprite> sprites, string spriteName)
        {
            var path = $"{TilesFolder}/{tileName}.asset";
            var existing = AssetDatabase.LoadAssetAtPath<Tile>(path);
            if (existing != null)
            {
                return existing;
            }

            if (!sprites.TryGetValue(spriteName, out var sprite))
            {
                Debug.LogError($"[CastleBlockoutEditor] Sprite '{spriteName}' não encontrado em {TilesetPath}.");
                return null;
            }

            EnsureFolder(TilesFolder);

            var tile = ScriptableObject.CreateInstance<Tile>();
            tile.sprite = sprite;
            tile.colliderType = Tile.ColliderType.Grid;
            AssetDatabase.CreateAsset(tile, path);
            return tile;
        }

        private static void EnsureFolder(string path)
        {
            if (string.IsNullOrEmpty(path) || AssetDatabase.IsValidFolder(path))
            {
                return;
            }

            var parent = Path.GetDirectoryName(path)?.Replace('\\', '/');
            var folderName = Path.GetFileName(path);
            if (!string.IsNullOrEmpty(parent))
            {
                EnsureFolder(parent);
            }

            AssetDatabase.CreateFolder(parent, folderName);
        }

        private static void CreateCamera(Transform parent)
        {
            var cameraObj = new GameObject("Main Camera");
            cameraObj.transform.SetParent(parent);
            cameraObj.tag = "MainCamera";
            cameraObj.transform.position = new Vector3(RoomWidth / 2f, RoomHeight / 2f, -10f);

            var camera = cameraObj.AddComponent<Camera>();
            camera.orthographic = true;
            camera.orthographicSize = 6f;

            var urpCameraDataType = Type.GetType(
                "UnityEngine.Rendering.Universal.UniversalAdditionalCameraData, Unity.RenderPipelines.Universal.Runtime");
            if (urpCameraDataType != null && cameraObj.GetComponent(urpCameraDataType) == null)
            {
                cameraObj.AddComponent(urpCameraDataType);
            }
        }
    }
}
