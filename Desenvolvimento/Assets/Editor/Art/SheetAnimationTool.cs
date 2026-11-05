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
    /// Com o JSON lateral do pxfx (<see cref="SheetMetadata"/>, ADR-016), usa a duração de cada
    /// quadro e o loop de lá; sem ele, 8 fps constantes.
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

            // Com o JSON lateral do pxfx (ADR-016), cada quadro dura o que o JSON diz — é o que segura a
            // antecipação e o impacto — e o loop vem de lá. Sem JSON, 8 fps constantes como antes.
            var temMeta = SheetMetadata.TryLoadFor(texturePath, out var meta)
                && meta.duracoes_ms != null
                && meta.duracoes_ms.Length == sprites.Length;
            if (temMeta)
            {
                loop = meta.loop;
            }

            var clip = new AnimationClip { frameRate = temMeta ? 60f : FrameRate, name = baseName };
            var binding = new EditorCurveBinding
            {
                type = typeof(SpriteRenderer),
                path = string.Empty,
                propertyName = "m_Sprite",
            };
            ObjectReferenceKeyframe[] keys;
            if (temMeta)
            {
                // uma chave por quadro no início dele, e uma chave final que segura o último quadro pelo tempo dele
                keys = new ObjectReferenceKeyframe[sprites.Length + 1];
                float t = 0f;
                for (int i = 0; i < sprites.Length; i++)
                {
                    keys[i] = new ObjectReferenceKeyframe { time = t, value = sprites[i] };
                    t += meta.duracoes_ms[i] / 1000f;
                }

                keys[sprites.Length] = new ObjectReferenceKeyframe { time = t, value = sprites[sprites.Length - 1] };
            }
            else
            {
                keys = new ObjectReferenceKeyframe[sprites.Length];
                for (int i = 0; i < sprites.Length; i++)
                {
                    keys[i] = new ObjectReferenceKeyframe { time = i / FrameRate, value = sprites[i] };
                }
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
            var ritmo = temMeta ? "durações do JSON lateral" : $"{FrameRate} fps";
            Debug.Log($"Criado/atualizado: {clipPath} e {controllerPath} ({sprites.Length} frames, {ritmo}, loop={loop}).");
        }

        private static int ParseIndex(string spriteName)
        {
            var idx = spriteName.LastIndexOf('_');
            return idx >= 0 && int.TryParse(spriteName.Substring(idx + 1), out var n) ? n : 0;
        }
    }
}
