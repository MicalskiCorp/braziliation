using Braziliation.Build;
using Braziliation.Core;
using Braziliation.Gameplay;
using Braziliation.UI;
using System;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace Braziliation.Editor.Gameplay
{
    /// <summary>
    /// Cria/atualiza uma cena fixa de demo em Assets/Scenes/DemoGameplay.unity.
    /// Use para substituir o bootstrap automático quando quiser uma cena persistida no projeto.
    /// </summary>
    public static class DemoSceneBuilderEditor
    {
        private const string ScenePath = "Assets/Scenes/DemoGameplay.unity";

        [MenuItem("Braziliation/Demo/Create or Update Fixed Demo Scene")]
        public static void CreateOrUpdateFixedDemoScene()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var root = new GameObject("DemoFixedSceneRoot");

            var locatorObj = new GameObject("GameServiceLocator");
            locatorObj.transform.SetParent(root.transform);
            locatorObj.AddComponent<GameServiceLocator>();

            var binderObj = new GameObject("BuildServiceBinder");
            binderObj.transform.SetParent(root.transform);
            var binder = binderObj.AddComponent<BuildServiceBinder>();

            CreateGround(root.transform);
            var player = CreatePlayer(root.transform, binder);
            CreateEnemy(root.transform, player.transform);
            CreateCamera(root.transform, player.transform);
            CreateHud(root.transform, player.GetComponent<HealthComponent>());

            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.Refresh();

            Debug.Log("[DemoSceneBuilderEditor] Cena fixa criada/atualizada em " + ScenePath);
        }

        private static void CreateGround(Transform parent)
        {
            var ground = new GameObject("Ground_Demo");
            ground.transform.SetParent(parent);
            ground.transform.position = new Vector3(0f, -1.5f, 0f);
            ground.transform.localScale = new Vector3(24f, 1f, 1f);

            var collider = ground.AddComponent<BoxCollider2D>();
            collider.size = new Vector2(24f, 1f);

            var renderer = ground.AddComponent<SpriteRenderer>();
            renderer.sprite = CreateSquareSprite();
            renderer.color = new Color(0.18f, 0.22f, 0.28f, 1f);
        }

        private static GameObject CreatePlayer(Transform parent, BuildServiceBinder binder)
        {
            var player = new GameObject("Player_Demo");
            player.transform.SetParent(parent);
            player.transform.position = new Vector3(-3f, 1f, 0f);
            player.transform.localScale = new Vector3(0.8f, 1.2f, 1f);

            try
            {
                player.tag = "Player";
            }
            catch (UnityException)
            {
                Debug.LogWarning("[DemoSceneBuilderEditor] Tag 'Player' não encontrada. A cena ainda funciona sem ela.");
            }

            var sprite = player.AddComponent<SpriteRenderer>();
            sprite.sprite = CreateSquareSprite();
            sprite.color = new Color(0.15f, 0.75f, 0.95f, 1f);

            var body = player.AddComponent<Rigidbody2D>();
            body.freezeRotation = true;
            body.gravityScale = 3f;

            player.AddComponent<BoxCollider2D>();

            var health = player.AddComponent<HealthComponent>();
            health.SetMaxHealth(100f, true);

            var controller = player.AddComponent<PlayerController>();
            var combat = player.AddComponent<PlayerCombat>();
            combat.SetAttackDamage(20f);

            var buildController = player.AddComponent<PlayerBuildController>();
            var synergy = player.AddComponent<HybridSynergyActivator>();
            var exploration = player.AddComponent<ExplorationFlagHandler>();

            buildController.ConfigureDependencies(controller, synergy, exploration);
            binder.SetBuildController(buildController);

            return player;
        }

        private static void CreateEnemy(Transform parent, Transform playerTarget)
        {
            var enemy = new GameObject("Enemy_Demo");
            enemy.transform.SetParent(parent);
            enemy.transform.position = new Vector3(3f, 1f, 0f);
            enemy.transform.localScale = new Vector3(0.8f, 1.2f, 1f);

            var sprite = enemy.AddComponent<SpriteRenderer>();
            sprite.sprite = CreateSquareSprite();
            sprite.color = new Color(0.95f, 0.3f, 0.25f, 1f);

            var body = enemy.AddComponent<Rigidbody2D>();
            body.freezeRotation = true;
            body.gravityScale = 3f;

            enemy.AddComponent<BoxCollider2D>();
            enemy.AddComponent<HealthComponent>();

            var enemyController = enemy.AddComponent<EnemyController>();
            enemyController.SetTarget(playerTarget);

            var left = new GameObject("EnemyPatrolLeft");
            left.transform.SetParent(enemy.transform);
            left.transform.position = new Vector3(1f, 1f, 0f);

            var right = new GameObject("EnemyPatrolRight");
            right.transform.SetParent(enemy.transform);
            right.transform.position = new Vector3(5f, 1f, 0f);

            enemyController.SetPatrolPoints(left.transform, right.transform);
        }

        private static void CreateCamera(Transform parent, Transform target)
        {
            var cameraObj = new GameObject("Main Camera");
            cameraObj.transform.SetParent(parent);
            cameraObj.tag = "MainCamera";
            cameraObj.transform.position = new Vector3(0f, 1f, -10f);

            var camera = cameraObj.AddComponent<Camera>();
            camera.orthographic = true;
            camera.orthographicSize = 5f;

            EnsureUrpAdditionalCameraData(cameraObj);

            var follow = cameraObj.AddComponent<SimpleCameraFollow>();
            follow.SetTarget(target);
        }

        private static void EnsureUrpAdditionalCameraData(GameObject cameraObject)
        {
            var urpCameraDataType = Type.GetType("UnityEngine.Rendering.Universal.UniversalAdditionalCameraData, Unity.RenderPipelines.Universal.Runtime");
            if (urpCameraDataType == null)
                return;

            if (cameraObject.GetComponent(urpCameraDataType) == null)
                cameraObject.AddComponent(urpCameraDataType);
        }

        private static void CreateHud(Transform parent, HealthComponent playerHealth)
        {
            var canvasObj = new GameObject("HUD_Demo");
            canvasObj.transform.SetParent(parent);

            var canvas = canvasObj.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasObj.AddComponent<CanvasScaler>();
            canvasObj.AddComponent<GraphicRaycaster>();

            var panelObj = new GameObject("HealthPanel");
            panelObj.transform.SetParent(canvasObj.transform, false);
            var panelRect = panelObj.AddComponent<RectTransform>();
            panelRect.anchorMin = new Vector2(0f, 1f);
            panelRect.anchorMax = new Vector2(0f, 1f);
            panelRect.pivot = new Vector2(0f, 1f);
            panelRect.anchoredPosition = new Vector2(20f, -20f);
            panelRect.sizeDelta = new Vector2(320f, 48f);

            var panelImage = panelObj.AddComponent<Image>();
            panelImage.color = new Color(0f, 0f, 0f, 0.45f);

            var sliderObj = new GameObject("HealthSlider");
            sliderObj.transform.SetParent(panelObj.transform, false);
            var sliderRect = sliderObj.AddComponent<RectTransform>();
            sliderRect.anchorMin = new Vector2(0f, 0f);
            sliderRect.anchorMax = new Vector2(1f, 1f);
            sliderRect.offsetMin = new Vector2(12f, 10f);
            sliderRect.offsetMax = new Vector2(-12f, -10f);

            var slider = sliderObj.AddComponent<Slider>();
            slider.minValue = 0f;
            slider.maxValue = 100f;
            slider.value = 100f;
            slider.interactable = false;

            var backgroundObj = new GameObject("Background");
            backgroundObj.transform.SetParent(sliderObj.transform, false);
            var bgImage = backgroundObj.AddComponent<Image>();
            bgImage.color = new Color(0.15f, 0.15f, 0.15f, 0.9f);
            var bgRect = backgroundObj.GetComponent<RectTransform>();
            bgRect.anchorMin = Vector2.zero;
            bgRect.anchorMax = Vector2.one;
            bgRect.offsetMin = Vector2.zero;
            bgRect.offsetMax = Vector2.zero;
            slider.targetGraphic = bgImage;

            var fillAreaObj = new GameObject("Fill Area");
            fillAreaObj.transform.SetParent(sliderObj.transform, false);
            var fillAreaRect = fillAreaObj.AddComponent<RectTransform>();
            fillAreaRect.anchorMin = Vector2.zero;
            fillAreaRect.anchorMax = Vector2.one;
            fillAreaRect.offsetMin = new Vector2(5f, 5f);
            fillAreaRect.offsetMax = new Vector2(-5f, -5f);

            var fillObj = new GameObject("Fill");
            fillObj.transform.SetParent(fillAreaObj.transform, false);
            var fillImage = fillObj.AddComponent<Image>();
            fillImage.color = new Color(0.2f, 0.9f, 0.35f, 0.95f);
            var fillRect = fillObj.GetComponent<RectTransform>();
            fillRect.anchorMin = Vector2.zero;
            fillRect.anchorMax = Vector2.one;
            fillRect.offsetMin = Vector2.zero;
            fillRect.offsetMax = Vector2.zero;

            var handleAreaObj = new GameObject("Handle Slide Area");
            handleAreaObj.transform.SetParent(sliderObj.transform, false);
            var handleAreaRect = handleAreaObj.AddComponent<RectTransform>();
            handleAreaRect.anchorMin = Vector2.zero;
            handleAreaRect.anchorMax = Vector2.one;
            handleAreaRect.offsetMin = Vector2.zero;
            handleAreaRect.offsetMax = Vector2.zero;

            slider.fillRect = fillRect;

            var labelObj = new GameObject("HealthLabel");
            labelObj.transform.SetParent(panelObj.transform, false);
            var labelRect = labelObj.AddComponent<RectTransform>();
            labelRect.anchorMin = new Vector2(0f, 0f);
            labelRect.anchorMax = new Vector2(1f, 1f);
            labelRect.offsetMin = new Vector2(12f, 8f);
            labelRect.offsetMax = new Vector2(-12f, -8f);

            var label = labelObj.AddComponent<Text>();
            label.text = "HP 100/100";
            label.alignment = TextAnchor.MiddleCenter;
            label.color = Color.white;
            label.fontSize = 16;
            label.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");

            var hud = canvasObj.AddComponent<CanvasHealthHud>();
            hud.Configure(playerHealth, slider, label);
        }

        private static Sprite CreateSquareSprite()
        {
            var texture = Texture2D.whiteTexture;
            return Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f), 100f);
        }
    }
}
