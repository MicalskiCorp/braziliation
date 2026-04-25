using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

namespace Braziliation.Editor.Menu
{
    /// <summary>
    /// One-click setup for the animated menu background.
    /// Run via Tools → Braziliation → Setup Menu Background.
    /// Idempotent: safe to run multiple times.
    /// </summary>
    public static class MenuBackgroundSetupEditor
    {
        private const string FramesFolder   = "Assets/Art/Menu/Background/Frames";
        private const string AnimFolder     = "Assets/Animations/Menu";
        private const string ClipName       = "MenuBackgroundLoop";
        private const string ControllerName = "MenuBackgroundAnimator";
        private const string GoName         = "MenuBackground";
        private const int    FrameRate      = 6;
        private const int    PixelsPerUnit  = 16;

        [MenuItem("Tools/Braziliation/Setup Menu Background")]
        public static void SetupMenuBackground()
        {
            EnsureDirectories();

            var sprites = LoadAndConfigureSprites();
            if (sprites == null || sprites.Length == 0)
            {
                Debug.LogError($"[MenuBackgroundSetup] No sprites found in {FramesFolder}. " +
                               "Add frame_001.png … frame_006.png and run again.");
                return;
            }

            var clip       = CreateOrUpdateAnimationClip(sprites);
            var controller = CreateOrUpdateAnimatorController(clip);

            SetupSceneGameObject(controller, sprites[0]);

            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log("[MenuBackgroundSetup] ✅ Menu background configured successfully.");
        }

        // ── Sprites ─────────────────────────────────────────────────────────

        private static Sprite[] LoadAndConfigureSprites()
        {
            var pngs = Directory.GetFiles(FramesFolder, "*.png")
                                .OrderBy(p => p)
                                .ToArray();

            if (pngs.Length == 0)
                return null;

            foreach (var png in pngs)
                ApplySpriteImportSettings(png);

            AssetDatabase.Refresh();

            return pngs.Select(p =>
                       {
                           var allAssets = AssetDatabase.LoadAllAssetsAtPath(p);
                           return allAssets.OfType<Sprite>().FirstOrDefault()
                                  ?? AssetDatabase.LoadAssetAtPath<Sprite>(p);
                       })
                       .Where(s => s != null)
                       .ToArray();
        }

        private static void ApplySpriteImportSettings(string assetPath)
        {
            var importer = AssetImporter.GetAtPath(assetPath) as TextureImporter;
            if (importer == null) return;

            bool dirty = false;

            if (importer.textureType != TextureImporterType.Sprite)
            { importer.textureType = TextureImporterType.Sprite; dirty = true; }

            if (importer.spriteImportMode != SpriteImportMode.Single)
            { importer.spriteImportMode = SpriteImportMode.Single; dirty = true; }

            if ((int)importer.spritePixelsPerUnit != PixelsPerUnit)
            { importer.spritePixelsPerUnit = PixelsPerUnit; dirty = true; }

            if (importer.filterMode != FilterMode.Point)
            { importer.filterMode = FilterMode.Point; dirty = true; }

            if (importer.textureCompression != TextureImporterCompression.Uncompressed)
            { importer.textureCompression = TextureImporterCompression.Uncompressed; dirty = true; }

            if (dirty)
                importer.SaveAndReimport();
        }

        // ── Animation Clip ───────────────────────────────────────────────────

        private static AnimationClip CreateOrUpdateAnimationClip(Sprite[] sprites)
        {
            EnsureDirectories();
            var clipPath = $"{AnimFolder}/{ClipName}.anim";
            var clip     = AssetDatabase.LoadAssetAtPath<AnimationClip>(clipPath);

            if (clip == null)
            {
                clip = new AnimationClip();
                AssetDatabase.CreateAsset(clip, clipPath);
            }

            clip.name      = ClipName;
            clip.frameRate = FrameRate;

            var settings = AnimationUtility.GetAnimationClipSettings(clip);
            settings.loopTime = true;
            AnimationUtility.SetAnimationClipSettings(clip, settings);

            var binding = new EditorCurveBinding
            {
                type         = typeof(SpriteRenderer),
                path         = string.Empty,
                propertyName = "m_Sprite"
            };

            var keyframes = new ObjectReferenceKeyframe[sprites.Length];
            for (int i = 0; i < sprites.Length; i++)
            {
                keyframes[i] = new ObjectReferenceKeyframe
                {
                    time  = i / (float)FrameRate,
                    value = sprites[i]
                };
            }

            AnimationUtility.SetObjectReferenceCurve(clip, binding, keyframes);
            EditorUtility.SetDirty(clip);

            return clip;
        }

        // ── Animator Controller ──────────────────────────────────────────────

        private static AnimatorController CreateOrUpdateAnimatorController(AnimationClip clip)
        {
            var controllerPath = $"{AnimFolder}/{ControllerName}.controller";
            var controller     = AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath);

            if (controller == null)
            {
                controller = AnimatorController.CreateAnimatorControllerAtPath(controllerPath);
            }

            var stateMachine = controller.layers[0].stateMachine;

            // Remove any existing state with the same name to avoid duplicates
            foreach (var existing in stateMachine.states)
            {
                if (existing.state.name == ClipName)
                {
                    stateMachine.RemoveState(existing.state);
                    break;
                }
            }

            var state = stateMachine.AddState(ClipName, new Vector3(300f, 120f, 0f));
            state.motion         = clip;
            state.writeDefaultValues = true;
            stateMachine.defaultState = state;

            EditorUtility.SetDirty(controller);
            return controller;
        }

        // ── Scene GameObject ─────────────────────────────────────────────────

        private static void SetupSceneGameObject(RuntimeAnimatorController controller, Sprite defaultSprite)
        {
            var existing = GameObject.Find(GoName);
            if (existing == null)
            {
                existing = new GameObject(GoName);
            }

            // SpriteRenderer
            var sr = existing.GetComponent<SpriteRenderer>();
            if (sr == null)
                sr = existing.AddComponent<SpriteRenderer>();

            sr.sprite       = defaultSprite;
            sr.sortingOrder = -100;

            // Animator
            var anim = existing.GetComponent<Animator>();
            if (anim == null)
                anim = existing.AddComponent<Animator>();

            anim.runtimeAnimatorController = controller;

            // Position at world origin, in front of camera z
            existing.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
            existing.transform.localScale = Vector3.one;

            // Mark scene dirty so Unity prompts to save
            UnityEditor.SceneManagement.EditorSceneManager.MarkSceneDirty(
                UnityEngine.SceneManagement.SceneManager.GetActiveScene());
        }

        // ── Helpers ──────────────────────────────────────────────────────────

        private static void EnsureDirectories()
        {
            CreateFolderIfMissing("Assets",            "Art");
            CreateFolderIfMissing("Assets/Art",        "Menu");
            CreateFolderIfMissing("Assets/Art/Menu",   "Background");
            CreateFolderIfMissing("Assets/Art/Menu/Background", "Frames");
            CreateFolderIfMissing("Assets",            "Animations");
            CreateFolderIfMissing("Assets/Animations", "Menu");
        }

        private static void CreateFolderIfMissing(string parent, string name)
        {
            var full = $"{parent}/{name}";
            if (!AssetDatabase.IsValidFolder(full))
                AssetDatabase.CreateFolder(parent, name);
        }
    }
}
