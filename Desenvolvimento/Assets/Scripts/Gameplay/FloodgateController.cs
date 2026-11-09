using Braziliation.Core;
using Braziliation.Hydric;
using UnityEngine;
using UnityEngine.Events;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Comporta hídrica de Blumenau: bloqueia ou libera uma passagem. É o lado "regra"
    /// da integração pedida em <c>Docs/TODO.md</c> § Unity ("Integrar a alavanca ao
    /// sistema hídrico de Blumenau") — a <see cref="FloodgateLeverInteractable"/> é só a
    /// casca visual da alavanca; esta classe decide o que a interação significa no mundo.
    /// Ligar as duas: no Inspector da alavanca, em "Eventos → On Activated", apontar para
    /// o método <see cref="Toggle"/> desta comporta (ou usar o prefab
    /// <c>Prop_FloodgateGate</c>, que já nasce com essa ligação pronta).
    ///
    /// O estado global do rio (<see cref="HydricStateManager"/>, no <c>GameServiceLocator</c>;
    /// <c>Docs/GDD/Features/Blumenau-SistemaHidrico.md</c>) trava a comporta em Cheia e Saturação
    /// (<see cref="HydricStateRules.LocksFloodgates"/>) e a destrava nos outros estados. Sem locator
    /// na cena, a comporta responde só à alavanca.
    /// </summary>
    [RequireComponent(typeof(Collider2D))]
    public sealed class FloodgateController : MonoBehaviour
    {
        [Header("Estado Inicial")]
        [Tooltip("Comporta começa aberta (passagem livre) ou fechada (bloqueando)?")]
        [SerializeField] private bool _startsOpen;

        [Header("Física")]
        [Tooltip("Aplica a layer Ground à comporta, para ela bloquear o jogador como piso/parede " +
                 "enquanto fechada. Desligue para uma comporta que só dispara eventos (áudio/VFX) sem bloquear.")]
        [SerializeField] private bool _blocksAsGround = true;

        [Header("Visual (opcional — aguarda asset de comporta, ver tech_debt.md)")]
        [SerializeField] private SpriteRenderer _gateRenderer;
        [SerializeField] private Sprite _openSprite;
        [SerializeField] private Sprite _closedSprite;

        [Header("Eventos")]
        [Tooltip("Disparado ao terminar de abrir.")]
        [SerializeField] private UnityEvent _onOpened;
        [Tooltip("Disparado ao terminar de fechar.")]
        [SerializeField] private UnityEvent _onClosed;

        private Collider2D _collider;
        private bool _isOpen;
        private bool _locked;
        private HydricStateManager _hydric;

        /// <summary>Comporta aberta (sem bloqueio) ou fechada (bloqueando a passagem).</summary>
        public bool IsOpen => _isOpen;

        /// <summary>
        /// Travada ignora <see cref="Toggle"/>, <see cref="Open"/> e <see cref="Close"/> —
        /// hoje quem trava é o estado do rio (Cheia e Saturação).
        /// </summary>
        public bool IsLocked => _locked;

        private void Awake()
        {
            _collider = GetComponent<Collider2D>();

            if (_blocksAsGround)
                GameLayers.Apply(gameObject, GameLayers.GroundName);

            ApplyState(_startsOpen, force: true);
        }

        // No Start, não no Awake: o GameServiceLocator registra o rio no Awake dele.
        private void Start()
        {
            var locator = GameServiceLocator.Instance;
            if (locator == null)
                return;

            _hydric = locator.Resolve<HydricStateManager>();
            if (_hydric == null)
                return;

            _hydric.StateChanged += OnHydricStateChanged;
            SetLocked(_hydric.Current.LocksFloodgates());
        }

        private void OnDestroy()
        {
            if (_hydric != null)
                _hydric.StateChanged -= OnHydricStateChanged;
        }

        private void OnHydricStateChanged(HydricState previous, HydricState current) =>
            SetLocked(current.LocksFloodgates());

        /// <summary>Alterna aberta/fechada. Pensado para o <c>UnityEvent</c> da alavanca.</summary>
        public void Toggle()
        {
            if (_locked)
                return;

            ApplyState(!_isOpen);
        }

        /// <summary>Abre a comporta (libera a passagem). Ignorado se travada.</summary>
        public void Open()
        {
            if (_locked)
                return;

            ApplyState(true);
        }

        /// <summary>Fecha a comporta (bloqueia a passagem). Ignorado se travada.</summary>
        public void Close()
        {
            if (_locked)
                return;

            ApplyState(false);
        }

        /// <summary>
        /// Trava a comporta no estado atual, ignorando novas interações da alavanca. Chamado pelo
        /// estado do rio a cada mudança: uma trava posta por outro sistema é desfeita quando o rio
        /// volta a Rotina ou Alerta.
        /// </summary>
        public void SetLocked(bool locked) => _locked = locked;

        private void ApplyState(bool open, bool force = false)
        {
            if (!force && _isOpen == open)
                return;

            _isOpen = open;

            if (_collider != null)
                _collider.enabled = !open;

            UpdateVisual();

            if (force)
                return;

            if (open)
                _onOpened?.Invoke();
            else
                _onClosed?.Invoke();
        }

        private void UpdateVisual()
        {
            if (_gateRenderer == null)
                return;

            var sprite = _isOpen ? _openSprite : _closedSprite;
            if (sprite != null)
                _gateRenderer.sprite = sprite;
        }
    }
}
