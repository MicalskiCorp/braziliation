using TMPro;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using Braziliation.Core;
using Braziliation.UI;

namespace Braziliation.Editor.Menu
{
    /// <summary>
    /// One-click setup for the Main Menu UI hierarchy.
    /// Run via Tools → Braziliation → Setup Main Menu UI.
    /// Idempotent: safe to run multiple times.
    /// </summary>
    public static class MainMenuUISetupEditor
    {
        // ── Layout constants ──────────────────────────────────────────────────
        private const float ButtonWidth    = 320f;
        private const float ButtonHeight   = 64f;
        private const float ButtonSpacing  = 16f;
        private const float PanelPaddingH  = 40f;
        private const float PanelPaddingV  = 32f;
        private const int   FontSize       = 28;

        private const string CanvasName    = "MainMenuCanvas";
        private const string EventSysName  = "EventSystem";
        private const string ServicesName  = "GameServices";

        // ── Entry point ───────────────────────────────────────────────────────
        [MenuItem("Tools/Braziliation/Setup Main Menu UI")]
        public static void SetupMainMenuUI()
        {
            EnsureEventSystem();
            EnsureGameServices();

            var canvas        = EnsureCanvas();
            var controllerGo  = EnsureChild(canvas, "MenuController");
            EnsureComponent<MenuController>(controllerGo);

            var mainPanel     = EnsureMainMenuPanel(canvas);
            var (s, l, o, e)  = EnsureButtons(mainPanel);

            var settingsPanel  = EnsurePlaceholderPanel<SettingsView>(canvas, "SettingsPanel");
            var saveSlotsPanel = EnsurePlaceholderPanel<SaveSlotsView>(canvas, "SaveSlotsPanel");

            WireMenuController(controllerGo, mainPanel, s, l, o, e, settingsPanel, saveSlotsPanel);
            SetupNavigation(s, l, o, e);

            EditorSceneManager.MarkSceneDirty(SceneManager.GetActiveScene());
            Debug.Log("[MainMenuUISetup] ✅ Main Menu UI configured successfully.");
        }

        // ── EventSystem ───────────────────────────────────────────────────────
        private static void EnsureEventSystem()
        {
            if (Object.FindAnyObjectByType<EventSystem>() != null)
                return;

            var go = new GameObject(EventSysName);
            Undo.RegisterCreatedObjectUndo(go, "Create EventSystem");
            go.AddComponent<EventSystem>();
            go.AddComponent<InputSystemUIInputModule>();
        }

        // ── GameServiceLocator ────────────────────────────────────────────────
        private static void EnsureGameServices()
        {
            if (Object.FindAnyObjectByType<GameServiceLocator>() != null)
                return;

            var go = new GameObject(ServicesName);
            Undo.RegisterCreatedObjectUndo(go, "Create GameServices");
            go.AddComponent<GameServiceLocator>();
        }

        // ── Canvas ────────────────────────────────────────────────────────────
        private static GameObject EnsureCanvas()
        {
            var existing = GameObject.Find(CanvasName);
            if (existing != null)
                return existing;

            var go     = new GameObject(CanvasName);
            Undo.RegisterCreatedObjectUndo(go, "Create MainMenuCanvas");
            go.layer   = LayerMask.NameToLayer("UI");

            var canvas = go.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 10;

            var scaler = go.AddComponent<CanvasScaler>();
            scaler.uiScaleMode        = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920f, 1080f);
            scaler.matchWidthOrHeight  = 0.5f;

            go.AddComponent<GraphicRaycaster>();
            return go;
        }

        // ── MainMenuPanel ─────────────────────────────────────────────────────
        private static GameObject EnsureMainMenuPanel(GameObject canvas)
        {
            var panel  = EnsureChild(canvas, "MainMenuPanel");
            var rt     = panel.GetComponent<RectTransform>();

            rt.anchorMin        = new Vector2(0.5f, 0.5f);
            rt.anchorMax        = new Vector2(0.5f, 0.5f);
            rt.pivot            = new Vector2(0.5f, 0.5f);
            rt.anchoredPosition = Vector2.zero;

            float totalH = 4f * ButtonHeight + 3f * ButtonSpacing + 2f * PanelPaddingV;
            rt.sizeDelta = new Vector2(ButtonWidth + 2f * PanelPaddingH, totalH);

            var vlg = EnsureComponent<VerticalLayoutGroup>(panel);
            vlg.childAlignment        = TextAnchor.MiddleCenter;
            vlg.spacing               = ButtonSpacing;
            vlg.padding               = new RectOffset(
                (int)PanelPaddingH, (int)PanelPaddingH,
                (int)PanelPaddingV, (int)PanelPaddingV);
            vlg.childForceExpandWidth  = true;
            vlg.childForceExpandHeight = false;
            vlg.childControlWidth      = true;
            vlg.childControlHeight     = false;

            return panel;
        }

        // ── Buttons ───────────────────────────────────────────────────────────
        private static (Button start, Button load, Button settings, Button exit)
            EnsureButtons(GameObject parent)
        {
            var start    = EnsureButton(parent, "StartGameButton",  "Start Game");
            var load     = EnsureButton(parent, "LoadGameButton",   "Load Game");
            var settings = EnsureButton(parent, "SettingsButton",   "Settings");
            var exit     = EnsureButton(parent, "ExitButton",       "Exit");
            return (start, load, settings, exit);
        }

        private static Button EnsureButton(GameObject parent, string name, string label)
        {
            var go  = EnsureChild(parent, name);
            go.layer = LayerMask.NameToLayer("UI");

            EnsureComponent<CanvasRenderer>(go);
            var img = EnsureComponent<Image>(go);
            img.color = new Color(0.12f, 0.12f, 0.14f, 0.95f);

            var le = EnsureComponent<LayoutElement>(go);
            le.preferredHeight = ButtonHeight;
            le.flexibleWidth   = 1f;

            var btn  = EnsureComponent<Button>(go);
            var cols = btn.colors;
            cols.normalColor      = new Color(0.12f, 0.12f, 0.14f, 0.95f);
            cols.highlightedColor = new Color(0.25f, 0.42f, 0.78f, 1f);
            cols.pressedColor     = new Color(0.18f, 0.30f, 0.55f, 1f);
            cols.selectedColor    = new Color(0.25f, 0.42f, 0.78f, 1f);
            btn.colors            = cols;
            btn.targetGraphic     = img;

            EnsureButtonLabel(go, label);
            return btn;
        }

        private static void EnsureButtonLabel(GameObject button, string text)
        {
            var labelGo = EnsureChild(button, "Label");
            labelGo.layer = LayerMask.NameToLayer("UI");
            EnsureComponent<CanvasRenderer>(labelGo);

            var rt = labelGo.GetComponent<RectTransform>();
            rt.anchorMin        = Vector2.zero;
            rt.anchorMax        = Vector2.one;
            rt.offsetMin        = new Vector2(8f, 4f);
            rt.offsetMax        = new Vector2(-8f, -4f);

            var tmp = EnsureComponent<TextMeshProUGUI>(labelGo);
            tmp.text                  = text;
            tmp.fontSize              = FontSize;
            tmp.fontStyle             = FontStyles.Bold;
            tmp.alignment             = TextAlignmentOptions.Center;
            tmp.color                 = Color.white;
            tmp.overflowMode          = TextOverflowModes.Ellipsis;
        }

        // ── Placeholder panels ────────────────────────────────────────────────
        private static GameObject EnsurePlaceholderPanel<T>(GameObject canvas, string name)
            where T : Component
        {
            var panel = EnsureChild(canvas, name);
            panel.layer = LayerMask.NameToLayer("UI");

            var rt = panel.GetComponent<RectTransform>();
            rt.anchorMin        = Vector2.zero;
            rt.anchorMax        = Vector2.one;
            rt.offsetMin        = Vector2.zero;
            rt.offsetMax        = Vector2.zero;

            EnsureComponent<T>(panel);
            panel.SetActive(false);
            return panel;
        }

        // ── Wiring ────────────────────────────────────────────────────────────
        private static void WireMenuController(
            GameObject controllerGo,
            GameObject mainPanel,
            Button btnStart, Button btnLoad, Button btnSettings, Button btnExit,
            GameObject settingsPanel, GameObject saveSlotsPanel)
        {
            var mc = controllerGo.GetComponent<MenuController>();
            if (mc == null) return;

            var so = new SerializedObject(mc);
            so.FindProperty("mainMenuPanel").objectReferenceValue = mainPanel;
            so.FindProperty("newGameButton").objectReferenceValue = btnStart;
            so.FindProperty("continueButton").objectReferenceValue = btnLoad;
            so.FindProperty("optionsButton").objectReferenceValue = btnSettings;
            so.FindProperty("exitButton").objectReferenceValue = btnExit;
            so.FindProperty("settingsView").objectReferenceValue =
                settingsPanel.GetComponent<SettingsView>();
            so.FindProperty("saveSlotsView").objectReferenceValue =
                saveSlotsPanel.GetComponent<SaveSlotsView>();
            so.FindProperty("firstSelected").objectReferenceValue = btnStart;
            so.ApplyModifiedProperties();
        }

        // ── Navigation ────────────────────────────────────────────────────────
        private static void SetupNavigation(
            Button start, Button load, Button settings, Button exit)
        {
            SetExplicitNav(start,    selectUp: exit,     selectDown: load);
            SetExplicitNav(load,     selectUp: start,    selectDown: settings);
            SetExplicitNav(settings, selectUp: load,     selectDown: exit);
            SetExplicitNav(exit,     selectUp: settings, selectDown: start);
        }

        private static void SetExplicitNav(Button btn, Selectable selectUp, Selectable selectDown)
        {
            var nav          = btn.navigation;
            nav.mode         = Navigation.Mode.Explicit;
            nav.selectOnUp   = selectUp;
            nav.selectOnDown = selectDown;
            btn.navigation   = nav;
        }

        // ── Helpers ───────────────────────────────────────────────────────────
        private static GameObject EnsureChild(GameObject parent, string name)
        {
            var rt = parent.GetComponent<RectTransform>();
            if (rt != null)
            {
                foreach (RectTransform child in rt)
                    if (child.name == name) return child.gameObject;
            }
            else
            {
                var t = parent.transform.Find(name);
                if (t != null) return t.gameObject;
            }

            var go = new GameObject(name, typeof(RectTransform));
            Undo.RegisterCreatedObjectUndo(go, $"Create {name}");
            go.transform.SetParent(parent.transform, false);
            return go;
        }

        private static T EnsureComponent<T>(GameObject go) where T : Component
        {
            var c = go.GetComponent<T>();
            return c != null ? c : Undo.AddComponent<T>(go);
        }
    }
}
