using System.Collections.Generic;
using UnityEngine;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Animação de sprite por troca de quadro, alimentada direto pelos spritesheets
    /// fatiados em <c>Assets/Art/</c>.
    ///
    /// Por que não um Animator/AnimatorController: os clipes aqui são placeholder e
    /// mudam junto com a arte. Este componente monta tudo em runtime a partir do
    /// spritesheet, então trocar de sheet não exige reabrir o Editor nem regerar
    /// <c>.anim</c>/<c>.controller</c>. Quando a arte final entrar, o caminho é migrar
    /// para Animator via <c>Assets &gt; Braziliation &gt; Criar Animação do Spritesheet</c>.
    ///
    /// Os quadros vêm de <c>Resources.LoadAll</c>, ordenados pelo índice que o
    /// <c>SheetAutoSlicer</c> coloca no nome (<c>..._sheet_0</c>, <c>_1</c>, ...).
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public sealed class SpriteSheetAnimator : MonoBehaviour
    {
        [System.Serializable]
        public sealed class ClipDefinition
        {
            [Tooltip("Nome usado em Play(). Ex.: \"idle\", \"run\".")]
            public string Name = "idle";

            [Tooltip("Caminho do sheet dentro de uma pasta Resources, sem extensão.")]
            public string ResourcePath = "";

            [Min(1f)]
            public float FramesPerSecond = 8f;

            public bool Loop = true;
        }

        [SerializeField] private List<ClipDefinition> _clips = new List<ClipDefinition>();
        [SerializeField] private string _defaultClip = "idle";

        private readonly Dictionary<string, Sprite[]> _frames = new Dictionary<string, Sprite[]>();
        private readonly Dictionary<string, ClipDefinition> _definitions = new Dictionary<string, ClipDefinition>();

        private SpriteRenderer _renderer;
        private ClipDefinition _current;
        private Sprite[] _currentFrames;
        private float _time;
        private int _frameIndex;

        /// <summary>Nome do clipe em execução, ou string vazia.</summary>
        public string CurrentClip => _current != null ? _current.Name : string.Empty;

        private void Awake()
        {
            _renderer = GetComponent<SpriteRenderer>();
            foreach (var clip in _clips)
                Register(clip);

            if (!string.IsNullOrEmpty(_defaultClip))
                Play(_defaultClip);
        }

        private void Update()
        {
            if (_currentFrames == null || _currentFrames.Length <= 1 || _current == null)
                return;

            _time += Time.deltaTime;
            var frameDuration = 1f / Mathf.Max(1f, _current.FramesPerSecond);
            if (_time < frameDuration)
                return;

            var advanced = Mathf.FloorToInt(_time / frameDuration);
            _time -= advanced * frameDuration;
            _frameIndex += advanced;

            if (_frameIndex >= _currentFrames.Length)
            {
                _frameIndex = _current.Loop
                    ? _frameIndex % _currentFrames.Length
                    : _currentFrames.Length - 1;
            }

            _renderer.sprite = _currentFrames[_frameIndex];
        }

        /// <summary>Define um clipe por código. Útil para os builders da cena de demo.</summary>
        public void AddClip(string clipName, string resourcePath, float fps = 8f, bool loop = true)
        {
            var clip = new ClipDefinition
            {
                Name = clipName,
                ResourcePath = resourcePath,
                FramesPerSecond = fps,
                Loop = loop,
            };

            _clips.Add(clip);
            if (_renderer != null)
                Register(clip);
        }

        /// <summary>Troca o clipe. Repetir o clipe atual não reinicia a animação.</summary>
        public void Play(string clipName)
        {
            if (string.IsNullOrEmpty(clipName) || (_current != null && _current.Name == clipName))
                return;

            if (!_definitions.TryGetValue(clipName, out var clip))
                return;

            if (!_frames.TryGetValue(clipName, out var frames) || frames.Length == 0)
                return;

            _current = clip;
            _currentFrames = frames;
            _frameIndex = 0;
            _time = 0f;

            if (_renderer != null)
                _renderer.sprite = frames[0];
        }

        private void Register(ClipDefinition clip)
        {
            if (clip == null || string.IsNullOrEmpty(clip.Name) || _frames.ContainsKey(clip.Name))
                return;

            var frames = LoadFrames(clip.ResourcePath);
            if (frames.Length == 0)
                return;

            _definitions[clip.Name] = clip;
            _frames[clip.Name] = frames;
        }

        /// <summary>
        /// Carrega os quadros do sheet. Se o sheet ainda não foi fatiado, cai para o
        /// sprite único — a cena continua funcionando, só sem animação.
        /// </summary>
        private static Sprite[] LoadFrames(string resourcePath)
        {
            if (string.IsNullOrEmpty(resourcePath))
                return System.Array.Empty<Sprite>();

            var sprites = Resources.LoadAll<Sprite>(resourcePath);
            if (sprites == null || sprites.Length == 0)
            {
                var single = Resources.Load<Sprite>(resourcePath);
                return single != null ? new[] { single } : System.Array.Empty<Sprite>();
            }

            // Resources.LoadAll não garante ordem; o índice do slicer vai no fim do nome.
            System.Array.Sort(sprites, (a, b) => FrameIndexOf(a.name).CompareTo(FrameIndexOf(b.name)));
            return sprites;
        }

        private static int FrameIndexOf(string spriteName)
        {
            var separator = spriteName.LastIndexOf('_');
            if (separator < 0 || separator == spriteName.Length - 1)
                return 0;

            return int.TryParse(spriteName.Substring(separator + 1), out var index) ? index : 0;
        }
    }
}
