using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Animations;
using UnityEngine;

namespace Braziliation.Editor.Art
{
    /// <summary>
    /// Gera AnimationClip + AnimatorController a partir de um spritesheet
    /// já fatiado (pelo SheetAutoSlicer ou manualmente).
    /// Uso: selecionar o sheet no Project e rodar
    /// Assets > Braziliation > Criar Animação do Spritesheet.
    /// Saída em Assets/Animations/World/ (padrão AssetsStructure.md).
    /// </summary>
    public static class SheetAnimationTool
    {
        private const string MenuPath = "Assets/Braziliation/Criar Animação do Spritesheet";
        private const string OutputFolder = "Assets/Animations/World";
        private const float FrameRate = 8f;

        /// <summary>
        /// Sheets da fila Unity de 2026-11-03 (item "Conferir o slicing do
        /// SheetAutoSlicer e gerar Animators"): alavanca e sino tocam uma vez
        /// (ativação/toque), o idle do Autômato é contínuo.
        /// </summary>
        private static readonly (string TexturePath, bool Loop)[] CurrentWaveSheets =
        {
            ("Assets/Art/Environments/Blumenau/Props/prop_blumenau_floodgate_lever_activate_sheet.png", false),
            ("Assets/Art/Environments/Blumenau/Props/prop_blumenau_sino_alerta_ring_sheet.png", false),
            ("Assets/Art/Enemies/Resources/enm_automato_idle_sheet.png", true),
        };

        [MenuItem(MenuPath, true)]
        private static bool Validate()
        {
            return Selection.activeObject is Texture2D;
        }

        [MenuItem(MenuPath)]
        private static void Create()
        {
            var texture = (Texture2D)Selection.activeObject;
            var texturePath = AssetDatabase.GetAssetPath(texture);
            CreateFromTexturePath(texturePath, loop: false);
        }

        /// <summary>
        /// Gera (ou regenera) os Animators da alavanca, do sino e do Autômato.
        /// Força o reimport antes: os dois primeiros sheets foram redesenhados
        /// (32→48/64→96 px) sem trocar a contagem de frames, e a guarda antiga do
        /// <see cref="SheetAutoSlicer"/> só olhava a contagem — ver o fix lá.
        /// Rodar via Tools/Braziliation/Setup ou em batch (-executeMethod).
        /// </summary>
        [MenuItem("Tools/Braziliation/Setup/Gerar Animators da Onda Atual (Alavanca, Sino, Autômato)")]
        public static void CreateAnimatorsForCurrentWave()
        {
            foreach (var (texturePath, loop) in CurrentWaveSheets)
            {
                AssetDatabase.ImportAsset(texturePath, ImportAssetOptions.ForceUpdate);
                CreateFromTexturePath(texturePath, loop);
            }

            AssetDatabase.SaveAssets();
            Debug.Log("[SheetAnimationTool] Onda atual: Animators de alavanca, sino e Autômato gerados/atualizados.");
        }

        /// <summary>Ponto de entrada sem depender de Selection — usado pelo menu e pelo batch.</summary>
        public static void CreateFromTexturePath(string texturePath, bool loop)
        {
            var sprites = AssetDatabase.LoadAllAssetRepresentationsAtPath(texturePath)
                .OfType<Sprite>()
                .OrderBy(s => ParseIndex(s.name))
                .ToArray();

            if (sprites.Length < 2)
            {
                Debug.LogError($"'{texturePath}' não tem múltiplos sprites. Confirme Sprite Mode Multiple e o slicing (sufixo _sheet fatia automático).");
                return;
            }

            var baseName = Path.GetFileNameWithoutExtension(texturePath);
            if (baseName.EndsWith("_sheet"))
            {
                baseName = baseName.Substring(0, baseName.Length - "_sheet".Length);
            }

            Directory.CreateDirectory(OutputFolder);

            var clip = new AnimationClip { frameRate = FrameRate, name = baseName };
            var binding = new EditorCurveBinding
            {
                type = typeof(SpriteRenderer),
                path = string.Empty,
                propertyName = "m_Sprite",
            };
            var keys = new ObjectReferenceKeyframe[sprites.Length];
            for (int i = 0; i < sprites.Length; i++)
            {
                keys[i] = new ObjectReferenceKeyframe { time = i / FrameRate, value = sprites[i] };
            }

            AnimationUtility.SetObjectReferenceCurve(clip, binding, keys);

            var settings = AnimationUtility.GetAnimationClipSettings(clip);
            settings.loopTime = loop;
            AnimationUtility.SetAnimationClipSettings(clip, settings);

            var clipPath = $"{OutputFolder}/{baseName}.anim";
            var existingClip = AssetDatabase.LoadAssetAtPath<AnimationClip>(clipPath);
            if (existingClip != null)
            {
                EditorUtility.CopySerialized(clip, existingClip);
                AssetDatabase.SaveAssets();
            }
            else
            {
                AssetDatabase.CreateAsset(clip, clipPath);
            }

            var controllerPath = $"{OutputFolder}/{baseName}.controller";
            if (AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath) == null)
            {
                var savedClip = AssetDatabase.LoadAssetAtPath<AnimationClip>(clipPath);
                AnimatorController.CreateAnimatorControllerAtPathWithClip(controllerPath, savedClip);
            }

            AssetDatabase.SaveAssets();
            Debug.Log($"Criado/atualizado: {clipPath} e {controllerPath} ({sprites.Length} frames @ {FrameRate} fps, loop={loop}).");
        }

        private static int ParseIndex(string spriteName)
        {
            var idx = spriteName.LastIndexOf('_');
            return idx >= 0 && int.TryParse(spriteName.Substring(idx + 1), out var n) ? n : 0;
        }
    }
}
