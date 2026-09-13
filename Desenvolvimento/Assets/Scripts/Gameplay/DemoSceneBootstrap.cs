using Braziliation.Build;
using Braziliation.Core;
using Braziliation.UI;
using System;
using Object = UnityEngine.Object;
using UnityEngine;
using UnityEngine.UI;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Monta uma cena jogável mínima em runtime para a primeira demo:
    /// GameServiceLocator, BuildServiceBinder, chão, player, inimigo e HUD.
    /// </summary>
    public sealed class DemoSceneBootstrap : MonoBehaviour
    {
        [Header("Auto Setup")]
        [SerializeField] private bool _autoCreateIfMissing = true;

        [Header("Spawn")]
        [SerializeField] private Vector2 _playerSpawn = new Vector2(-3f, DemoSceneVisuals.GroundSurfaceY);
        [SerializeField] private Vector2 _enemySpawn = new Vector2(3f, DemoSceneVisuals.GroundSurfaceY);

        private void Start()
        {
            if (!_autoCreateIfMissing)
                return;

            EnsureCoreServices();
            EnsureBackground();
            EnsureGround();
            EnsureBounds();

            var player = EnsurePlayer();
            var enemy = EnsureEnemy(player.transform);

            EnsureCamera(player.transform);
            EnsureHud(player.GetComponent<HealthComponent>());

            if (enemy != null)
                enemy.name = "Enemy_Demo";
        }

        private static void EnsureCoreServices()
        {
            if (GameServiceLocator.Instance == null)
            {
                var locatorObj = new GameObject("GameServiceLocator");
                locatorObj.AddComponent<GameServiceLocator>();
            }

            var binderObj = GameObject.Find("BuildServiceBinder");
            if (binderObj == null)
            {
                binderObj = new GameObject("BuildServiceBinder");
                binderObj.AddComponent<BuildServiceBinder>();
            }
        }

        private static void EnsureBackground()
        {
            if (GameObject.Find("Background_Demo") != null)
                return;

            DemoSceneVisuals.CreateBackground(null, new Vector3(0f, 1f, 0f));
        }

        private static void EnsureGround()
        {
            if (GameObject.Find("Ground_Demo") != null)
                return;

            DemoSceneVisuals.ConfigureGround(new GameObject("Ground_Demo"));
        }

        private static void EnsureBounds()
        {
            if (GameObject.Find("Bound_Left") != null)
                return;

            DemoSceneVisuals.CreateBounds(null);
        }

        private GameObject EnsurePlayer()
        {
            GameObject existing = null;
            try
            {
                existing = GameObject.FindWithTag("Player");
            }
            catch (UnityException)
            {
                // Tag pode não existir no projeto ainda. Seguimos com criação normal.
            }

            if (existing != null)
                return existing;

            var player = new GameObject("Player_Demo");
            try
            {
                player.tag = "Player";
            }
            catch (UnityException)
            {
                Debug.LogWarning("[DemoSceneBootstrap] Tag 'Player' não existe no projeto. O HUD fará bind por referência direta.");
            }
            player.transform.position = new Vector3(_playerSpawn.x, _playerSpawn.y, 0f);
            GameLayers.Apply(player, GameLayers.PlayerName);

            DemoSceneVisuals.ApplyCharacterSprite(
                player,
                DemoSceneVisuals.PlayerSpritePath,
                DemoSceneVisuals.PlayerFallbackColor);
            DemoSceneVisuals.ConfigurePlayerAnimation(player);
            player.AddComponent<FallRespawn>();

            var body = player.AddComponent<Rigidbody2D>();
            body.freezeRotation = true;
            body.gravityScale = 3f;

            var playerCollider = player.AddComponent<BoxCollider2D>();
            playerCollider.size = DemoSceneVisuals.PlayerColliderSize;
            playerCollider.offset = DemoSceneVisuals.PlayerColliderOffset;

            var health = player.AddComponent<HealthComponent>();
            health.SetMaxHealth(100f, true);

            player.AddComponent<PlayerController>();
            var combat = player.AddComponent<PlayerCombat>();
            combat.SetAttackDamage(20f);

            var buildController = player.AddComponent<PlayerBuildController>();
            var synergy = player.AddComponent<HybridSynergyActivator>();
            var exploration = player.AddComponent<ExplorationFlagHandler>();

            buildController.ConfigureDependencies(
                player.GetComponent<PlayerController>(),
                synergy,
                exploration);

            var binder = Object.FindAnyObjectByType<BuildServiceBinder>();
            if (binder != null)
                binder.SetBuildController(buildController);

            return player;
        }

        private GameObject EnsureEnemy(Transform playerTarget)
        {
            var existing = GameObject.Find("Enemy_Demo");
            if (existing != null)
                return existing;

            var enemy = new GameObject("Enemy_Demo");
            enemy.transform.position = new Vector3(_enemySpawn.x, _enemySpawn.y, 0f);
            GameLayers.Apply(enemy, GameLayers.EnemyName);

            DemoSceneVisuals.ApplyCharacterSprite(
                enemy,
                DemoSceneVisuals.EnemySpritePath,
                DemoSceneVisuals.EnemyFallbackColor);
            DemoSceneVisuals.ConfigureEnemyAnimation(enemy);
            enemy.AddComponent<FallRespawn>();

            var body = enemy.AddComponent<Rigidbody2D>();
            body.freezeRotation = true;
            body.gravityScale = 3f;

            var enemyCollider = enemy.AddComponent<BoxCollider2D>();
            enemyCollider.size = DemoSceneVisuals.EnemyColliderSize;
            enemyCollider.offset = DemoSceneVisuals.EnemyColliderOffset;
            enemy.AddComponent<HealthComponent>();

            var controller = enemy.AddComponent<EnemyController>();
            controller.SetTarget(playerTarget);
            controller.SetSpriteFacesRight(DemoSceneVisuals.EnemySpriteFacesRight);

            // Os marcadores NÃO são filhos do inimigo: presos a ele, andavam junto e a
            // ponta da patrulha nunca era alcançada — o inimigo caminhava até cair do mapa.
            var left = new GameObject("EnemyPatrolLeft");
            left.transform.position = new Vector3(_enemySpawn.x - 2f, _enemySpawn.y, 0f);

            var right = new GameObject("EnemyPatrolRight");
            right.transform.position = new Vector3(_enemySpawn.x + 2f, _enemySpawn.y, 0f);

            controller.SetPatrolPoints(left.transform, right.transform);

            return enemy;
        }

        private static void EnsureCamera(Transform target)
        {
            var camera = Camera.main;
            if (camera == null)
            {
                var camObj = new GameObject("Main Camera");
                camObj.tag = "MainCamera";
                camera = camObj.AddComponent<Camera>();
                camera.orthographic = true;
                camera.orthographicSize = 5f;
            }

            EnsureUrpAdditionalCameraData(camera.gameObject);

            var follow = camera.GetComponent<SimpleCameraFollow>();
            if (follow == null)
                follow = camera.gameObject.AddComponent<SimpleCameraFollow>();

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

        private static void EnsureHud(HealthComponent playerHealth)
        {
            var hudObj = GameObject.Find("HUD_Demo");
            if (hudObj != null)
                return;

            hudObj = new GameObject("HUD_Demo");
            var canvas = hudObj.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            hudObj.AddComponent<CanvasScaler>();
            hudObj.AddComponent<GraphicRaycaster>();

            var panelObj = new GameObject("HealthPanel");
            panelObj.transform.SetParent(hudObj.transform, false);
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

            var hud = hudObj.AddComponent<CanvasHealthHud>();
            hud.Configure(playerHealth, slider, label);
        }
    }
}
