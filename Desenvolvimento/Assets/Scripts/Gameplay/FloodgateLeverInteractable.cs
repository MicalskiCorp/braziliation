using Braziliation.Core;
using UnityEngine;
using UnityEngine.Events;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Casca visual da alavanca da comporta (Prop_FloodgateLever): toca a animação de
    /// ativação e avisa quem estiver ouvindo via <see cref="OnActivated"/>. Nenhuma regra
    /// do sistema hídrico de Blumenau vive aqui — quem decide o que a interação significa
    /// no mundo é a <see cref="FloodgateController"/> ligada no Inspector (ou já pronta no
    /// prefab <c>Prop_FloodgateGate</c>).
    ///
    /// Convenção: o Animator fica desligado em repouso para não tocar a animação de
    /// ativação sozinho ao carregar a cena — o <see cref="SpriteRenderer"/> mostra o
    /// quadro de repouso até o primeiro <see cref="Interact"/>.
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public sealed class FloodgateLeverInteractable : MonoBehaviour, IInteractable
    {
        [Header("Visual")]
        [Tooltip("Quadro mostrado antes de qualquer interação.")]
        [SerializeField] private Sprite _restingSprite;
        [Tooltip("Controller gerado por SheetAnimationTool a partir do *_activate_sheet.")]
        [SerializeField] private Animator _activateAnimator;
        [Tooltip("Nome do estado/clipe de ativação (baseName do sheet, sem '_sheet').")]
        [SerializeField] private string _activateStateName = "prop_blumenau_floodgate_lever_activate";

        [Header("Eventos")]
        [Tooltip("Disparado a cada interação, independente do estado ligado/desligado.")]
        [SerializeField] private UnityEvent _onActivated;

        private SpriteRenderer _renderer;
        private bool _isOn;

        /// <summary>Estado atual da alavanca — ligada ou desligada.</summary>
        public bool IsOn => _isOn;

        /// <summary>
        /// Evento disparado a cada interação — exposto para wiring programático (ex.:
        /// <c>FloodgateGatePrefabBuilder</c>) além do Inspector.
        /// </summary>
        public UnityEvent OnActivated => _onActivated;

        private void Awake()
        {
            _renderer = GetComponent<SpriteRenderer>();
            if (_restingSprite != null)
                _renderer.sprite = _restingSprite;

            if (_activateAnimator != null)
                _activateAnimator.enabled = false;
        }

        /// <summary>Acionado pelo jogador via <see cref="PlayerController"/>.</summary>
        public void Interact()
        {
            _isOn = !_isOn;
            PlayActivateAnimation();
            _onActivated?.Invoke();
        }

        private void PlayActivateAnimation()
        {
            if (_activateAnimator == null || string.IsNullOrEmpty(_activateStateName))
                return;

            _activateAnimator.enabled = true;
            _activateAnimator.Play(_activateStateName, 0, 0f);
        }
    }
}
