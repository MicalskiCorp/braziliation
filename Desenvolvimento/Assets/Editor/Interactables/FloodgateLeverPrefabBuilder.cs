using Braziliation.Gameplay;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

namespace Braziliation.Editor.Interactables
{
    /// <summary>
    /// Cria/atualiza o prefab <c>Prop_FloodgateLever</c> — fila Unity de 2026-11-03
    /// (Docs/TODO.md § Unity). Depende do Animator gerado por
    /// <see cref="Braziliation.Editor.Art.SheetAnimationTool.CreateAnimatorsForCurrentWave"/>;
    /// roda essa etapa primeiro se o controller ainda não existir.
    /// Idempotente: reconstrói o GameObject do zero e sobrescreve o prefab.
    /// </summary>
    public static class FloodgateLeverPrefabBuilder
    {
        private const string PrefabFolder = "Assets/Prefabs/Interactables";
        private const string PrefabPath = PrefabFolder + "/Prop_FloodgateLever.prefab";
        private const string RestingSpritePath = "Assets/Art/Environments/Blumenau/Props/prop_blumenau_floodgate_lever.png";
        private const string ControllerPath = "Assets/Animations/World/prop_blumenau_floodgate_lever_activate.controller";
        private const string ActivateStateName = "prop_blumenau_floodgate_lever_activate";

        [MenuItem("Tools/Braziliation/Setup/Build Floodgate Lever Prefab")]
        public static void CreateOrUpdatePrefab()
        {
            var controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath);
            if (controller == null)
            {
                Debug.LogError($"[FloodgateLeverPrefabBuilder] Controller não encontrado em {ControllerPath}. " +
                                "Rode Tools/Braziliation/Setup/Gerar Animators da Onda Atual primeiro.");
                return;
            }

            var restingSprite = AssetDatabase.LoadAssetAtPath<Sprite>(RestingSpritePath);
            if (restingSprite == null)
            {
                Debug.LogError($"[FloodgateLeverPrefabBuilder] Sprite de repouso não encontrado em {RestingSpritePath}.");
                return;
            }

            EnsureFolder();

            var root = new GameObject("Prop_FloodgateLever");
            try
            {
                var renderer = root.AddComponent<SpriteRenderer>();
                renderer.sprite = restingSprite;

                var collider = root.AddComponent<BoxCollider2D>();
                collider.size = new Vector2(1.2f, 2f);
                collider.offset = new Vector2(0f, 1f);

                var animator = root.AddComponent<Animator>();
                animator.runtimeAnimatorController = controller;

                var interactable = root.AddComponent<FloodgateLeverInteractable>();
                BindInteractable(interactable, restingSprite, animator);

                PrefabUtility.SaveAsPrefabAsset(root, PrefabPath);
                Debug.Log($"[FloodgateLeverPrefabBuilder] Prefab criado/atualizado em {PrefabPath}.");
            }
            finally
            {
                Object.DestroyImmediate(root);
            }
        }

        private static void BindInteractable(FloodgateLeverInteractable interactable, Sprite restingSprite, Animator animator)
        {
            var serialized = new SerializedObject(interactable);
            serialized.FindProperty("_restingSprite").objectReferenceValue = restingSprite;
            serialized.FindProperty("_activateAnimator").objectReferenceValue = animator;
            serialized.FindProperty("_activateStateName").stringValue = ActivateStateName;
            serialized.ApplyModifiedPropertiesWithoutUndo();
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
