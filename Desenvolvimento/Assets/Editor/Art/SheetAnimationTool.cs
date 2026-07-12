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

            var clip = new AnimationClip { frameRate = FrameRate };
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

            var clipPath = $"{OutputFolder}/{baseName}.anim";
            AssetDatabase.CreateAsset(clip, clipPath);

            var controllerPath = $"{OutputFolder}/{baseName}.controller";
            if (AssetDatabase.LoadAssetAtPath<AnimatorController>(controllerPath) == null)
            {
                AnimatorController.CreateAnimatorControllerAtPathWithClip(controllerPath, clip);
            }

            AssetDatabase.SaveAssets();
            Debug.Log($"Criado: {clipPath} e {controllerPath} ({sprites.Length} frames @ {FrameRate} fps, sem loop).");
        }

        private static int ParseIndex(string spriteName)
        {
            var idx = spriteName.LastIndexOf('_');
            return idx >= 0 && int.TryParse(spriteName.Substring(idx + 1), out var n) ? n : 0;
        }
    }
}
