using Braziliation.Gameplay;
using UnityEditor;
using UnityEditor.Events;
using UnityEngine;

namespace Braziliation.Editor.Interactables
{
    /// <summary>
    /// Cria/atualiza o prefab <c>Prop_FloodgateGate</c>: a comporta (bloqueio físico) com a
    /// alavanca <c>Prop_FloodgateLever</c> aninhada e já ligada ao <see cref="FloodgateController.Toggle"/>.
    /// Fila Unity de 2026-11-03 (Docs/TODO.md § Unity, "Integrar a alavanca ao sistema
    /// hídrico de Blumenau"). Depende de <c>Prop_FloodgateLever.prefab</c> já existir — roda
    /// <see cref="FloodgateLeverPrefabBuilder.CreateOrUpdatePrefab"/> primeiro se precisar.
    /// Idempotente: reconstrói o GameObject do zero e sobrescreve o prefab.
    /// </summary>
    public static class FloodgateGatePrefabBuilder
    {
        private const string PrefabFolder = "Assets/Prefabs/Interactables";
        private const string PrefabPath = PrefabFolder + "/Prop_FloodgateGate.prefab";
        private const string LeverPrefabPath = PrefabFolder + "/Prop_FloodgateLever.prefab";

        [MenuItem("Tools/Braziliation/Setup/Build Floodgate Gate Prefab")]
        public static void CreateOrUpdatePrefab()
        {
            var leverPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(LeverPrefabPath);
            if (leverPrefab == null)
            {
                Debug.LogError($"[FloodgateGatePrefabBuilder] {LeverPrefabPath} não encontrado. " +
                                "Rode Tools/Braziliation/Setup/Build Floodgate Lever Prefab primeiro.");
                return;
            }

            EnsureFolder();

            var root = new GameObject("Prop_FloodgateGate");
            GameObject leverInstance = null;
            try
            {
                // Comporta: colisor vertical fino que bloqueia a passagem quando fechada.
                // Dimensões pensadas para o grid de 48 PPU (ADR-011) — ajustar por instância.
                var gateCollider = root.AddComponent<BoxCollider2D>();
                gateCollider.size = new Vector2(0.2f, 3f);
                gateCollider.offset = new Vector2(0f, 1.5f);

                var controller = root.AddComponent<FloodgateController>();

                // Alavanca aninhada como prefab filho — fica como nested prefab instance,
                // então atualizações em Prop_FloodgateLever propagam para este prefab.
                leverInstance = (GameObject)PrefabUtility.InstantiatePrefab(leverPrefab);
                leverInstance.transform.SetParent(root.transform, worldPositionStays: false);
                leverInstance.transform.localPosition = new Vector3(0.6f, 0f, 0f);

                var leverInteractable = leverInstance.GetComponent<FloodgateLeverInteractable>();
                if (leverInteractable == null)
                {
                    Debug.LogError("[FloodgateGatePrefabBuilder] Prop_FloodgateLever sem FloodgateLeverInteractable.");
                    return;
                }

                UnityEventTools.AddPersistentListener(leverInteractable.OnActivated, controller.Toggle);

                PrefabUtility.SaveAsPrefabAsset(root, PrefabPath);
                Debug.Log($"[FloodgateGatePrefabBuilder] Prefab criado/atualizado em {PrefabPath}.");
            }
            finally
            {
                Object.DestroyImmediate(root);
            }
        }

        private static void EnsureFolder()
        {
            if (!AssetDatabase.IsValidFolder(PrefabFolder))
            {
                AssetDatabase.CreateFolder("Assets/Prefabs", "Interactables");
            }
        }
    }
}
