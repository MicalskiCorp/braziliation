using Braziliation.Core;
using Braziliation.Gameplay;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

namespace Braziliation.Editor.Enemies
{
    /// <summary>
    /// Cria/atualiza o prefab <c>Enemy_Automato</c> — fila Unity de 2026-11-03
    /// (Docs/TODO.md § Unity, redesenho 96×96 aprovado em 2026-10-05). Usa o Animator
    /// (loop) gerado por
    /// <see cref="Braziliation.Editor.Art.SheetAnimationTool.CreateAnimatorsForCurrentWave"/>
    /// em vez do <see cref="SpriteSheetAnimator"/> de placeholder — essa é exatamente a
    /// migração que o comentário do SpriteSheetAnimator descreve para quando a arte
    /// final entra.
    ///
    /// Sem <see cref="EnemyProfileAsset"/>: o perfil do arquétipo ainda depende da
    /// decisão de design "Inimigo básico da demo" (Docs/TODO.md § Decisões). O
    /// <see cref="EnemyController"/> usa os defaults inline (Patroller), como o
    /// inimigo da demo já faz.
    /// </summary>
    public static class AutomatoPrefabBuilder
    {
        private const string PrefabFolder = "Assets/Prefabs/Enemies";
        private const string PrefabPath = PrefabFolder + "/Enemy_Automato.prefab";
        private const string BaseSpritePath = "Assets/Art/Enemies/Resources/enm_automato_lanca.png";
        private const string ControllerPath = "Assets/Animations/World/enm_automato_idle.controller";

        [MenuItem("Tools/Braziliation/Setup/Build Automato Enemy Prefab")]
        public static void CreateOrUpdatePrefab()
        {
            var controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath);
            if (controller == null)
            {
                Debug.LogError($"[AutomatoPrefabBuilder] Controller não encontrado em {ControllerPath}. " +
                                "Rode Tools/Braziliation/Setup/Gerar Animators da Onda Atual primeiro.");
                return;
            }

            var baseSprite = AssetDatabase.LoadAssetAtPath<Sprite>(BaseSpritePath);
            if (baseSprite == null)
            {
                Debug.LogError($"[AutomatoPrefabBuilder] Sprite base não encontrado em {BaseSpritePath}.");
                return;
            }

            EnsureFolder();

            var root = new GameObject("Enemy_Automato");
            try
            {
                GameLayers.Apply(root, GameLayers.EnemyName);

                var renderer = root.AddComponent<SpriteRenderer>();
                renderer.sprite = baseSprite;
                renderer.sortingOrder = DemoSceneVisuals.CharacterSortingOrder;

                var animator = root.AddComponent<Animator>();
                animator.runtimeAnimatorController = controller;

                var body = root.AddComponent<Rigidbody2D>();
                body.freezeRotation = true;
                body.gravityScale = 3f;

                var collider = root.AddComponent<BoxCollider2D>();
                collider.size = DemoSceneVisuals.EnemyColliderSize;
                collider.offset = DemoSceneVisuals.EnemyColliderOffset;

                root.AddComponent<HealthComponent>();

                var controllerComponent = root.AddComponent<EnemyController>();
                controllerComponent.SetSpriteFacesRight(DemoSceneVisuals.EnemySpriteFacesRight);

                PrefabUtility.SaveAsPrefabAsset(root, PrefabPath);
                Debug.Log($"[AutomatoPrefabBuilder] Prefab criado/atualizado em {PrefabPath}.");
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
                AssetDatabase.CreateFolder("Assets/Prefabs", "Enemies");
            }
        }
    }
}
