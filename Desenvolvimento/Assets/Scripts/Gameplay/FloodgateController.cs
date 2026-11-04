using Braziliation.Core;
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
    /// Hoje a comporta só conhece aberta/fechada/travada por ação local (a alavanca). O
    /// sistema global de 4 estados do rio
    /// (<c>Docs/GDD/Features/Blumenau-SistemaHidrico.md</c>) ainda não existe
    /// (<c>@SystemsDeveloper</c>, <c>HydricStateManager</c>) — quando existir, ele trava a
    /// comporta via <see cref="SetLocked"/> nos estados de Cheia/Saturação em vez de
    /// alterar esta classe. Ver <c>Docs/Tech/tech_debt.md</c>.
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

        /// <summary>Comporta aberta (sem bloqueio) ou fechada (bloqueando a passagem).</summary>
        public bool IsOpen => _isOpen;

        /// <summary>
        /// Travada ignora <see cref="Toggle"/>, <see cref="Open"/> e <see cref="Close"/> —
        /// reservado para o futuro <c>HydricStateManager</c> (ex.: trava fechada em Saturação).
        /// </summary>
        public bool IsLocked => _locked;

        private void Awake()
        {
            _collider = GetComponent<Collider2D>();

            if (_blocksAsGround)
                GameLayers.Apply(gameObject, GameLayers.GroundName);

            ApplyState(_startsOpen, force: true);
        }

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
        /// Trava a comporta no estado atual, ignorando novas interações da alavanca. Ponto
        /// de integração do futuro <c>HydricStateManager</c> (ex.: travar fechada em Saturação).
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
