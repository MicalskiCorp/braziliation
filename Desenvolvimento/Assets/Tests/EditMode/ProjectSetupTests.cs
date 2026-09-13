using System.IO;
using System.Linq;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;
using UnityEngine.InputSystem;

namespace Braziliation.Tests.EditMode
{
    /// <summary>
    /// Configuração do projeto que só existe dentro do Unity: layers resolvidas, action map
    /// carregado, import settings aplicados, cenas do build presentes.
    ///
    /// Este assembly não referencia Assembly-CSharp de propósito (asmdef não pode
    /// referenciar o assembly padrão). Por isso os nomes abaixo repetem as constantes de
    /// GameLayers e GameInput — e os testes xUnit em UnityAssetConsistencyTests travam que
    /// essas constantes batem com os assets, dos dois lados.
    /// </summary>
    public sealed class ProjectSetupTests
    {
        [TestCase("Ground", 8)]
        [TestCase("Player", 9)]
        [TestCase("Enemy", 10)]
        public void Physics_Layer_Resolves_To_Expected_Index(string layerName, int expectedIndex)
        {
            Assert.AreEqual(expectedIndex, LayerMask.NameToLayer(layerName),
                $"A layer '{layerName}' deveria estar no índice {expectedIndex} (ProjectSettings/TagManager.asset).");
        }

        [TestCase("Move")]
        [TestCase("Jump")]
        [TestCase("Attack")]
        [TestCase("Interact")]
        public void Project_Wide_Actions_Expose_Player_Action(string actionName)
        {
            var asset = InputSystem.actions;
            Assert.IsNotNull(asset,
                "Nenhum action asset project-wide configurado (Project Settings > Input System Package).");
            Assert.IsNotNull(asset.FindAction($"Player/{actionName}", throwIfNotFound: false),
                $"GameInput lê 'Player/{actionName}', que não existe no action asset project-wide.");
        }

        /// <summary>
        /// SpriteImportPostprocessor força 32 PPU / Point / sem compressão em Assets/Art/.
        /// Um .meta antigo que nunca foi reimportado escapa do postprocessor — este teste pega.
        /// </summary>
        [Test]
        public void Own_Art_Is_Imported_Pixel_Perfect()
        {
            var problemas = AssetDatabase.FindAssets("t:Texture2D", new[] { "Assets/Art" })
                .Select(AssetDatabase.GUIDToAssetPath)
                .Where(path => !path.StartsWith("Assets/Art/ThirdParty/"))
                .Select(path => (path, importer: AssetImporter.GetAtPath(path) as TextureImporter))
                .Where(x => x.importer != null)
                .Where(x => !Mathf.Approximately(x.importer.spritePixelsPerUnit, 32f)
                            || x.importer.filterMode != FilterMode.Point
                            || x.importer.textureCompression != TextureImporterCompression.Uncompressed
                            || x.importer.mipmapEnabled)
                .Select(x => $"{x.path} (PPU {x.importer.spritePixelsPerUnit}, {x.importer.filterMode}, " +
                             $"{x.importer.textureCompression}, mipmap {x.importer.mipmapEnabled})")
                .ToList();

            Assert.IsEmpty(problemas,
                "Texturas fora do padrão pixel art (reimportar para o SpriteImportPostprocessor aplicar):\n" +
                string.Join("\n", problemas));
        }

        [Test]
        public void Every_Scene_In_Build_Settings_Exists()
        {
            var ausentes = EditorBuildSettings.scenes
                .Where(scene => !File.Exists(scene.path))
                .Select(scene => scene.path)
                .ToList();

            Assert.IsEmpty(ausentes, "Cenas na Build Settings que não existem: " + string.Join(", ", ausentes));
        }
    }
}
