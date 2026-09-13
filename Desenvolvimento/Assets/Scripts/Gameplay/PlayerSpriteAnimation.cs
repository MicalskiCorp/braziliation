using UnityEngine;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Liga o estado do <see cref="PlayerController"/> ao <see cref="SpriteSheetAnimator"/>
    /// e cuida do espelhamento do sprite. Fica separado do controller para que a lógica
    /// de movimento não dependa de nada visual.
    /// </summary>
    [RequireComponent(typeof(PlayerController))]
    public sealed class PlayerSpriteAnimation : MonoBehaviour
    {
        [SerializeField] private SpriteSheetAnimator _animator;
        [SerializeField] private SpriteRenderer _renderer;

        [Header("Clipes")]
        [SerializeField] private string _idleClip = "idle";
        [SerializeField] private string _runClip = "run";

        [Header("Sprite")]
        [Tooltip("Desmarque quando a arte original olha para a esquerda.")]
        [SerializeField] private bool _spriteFacesRight = true;

        private PlayerController _controller;

        private void Awake()
        {
            _controller = GetComponent<PlayerController>();

            if (_animator == null)
                _animator = GetComponentInChildren<SpriteSheetAnimator>();

            if (_renderer == null)
                _renderer = GetComponentInChildren<SpriteRenderer>();
        }

        private void Update()
        {
            if (_renderer != null)
            {
                _renderer.flipX = _spriteFacesRight
                    ? _controller.Facing < 0
                    : _controller.Facing > 0;
            }

            if (_animator == null)
                return;

            var moving = Mathf.Abs(_controller.MoveInput) > 0.01f;
            _animator.Play(moving ? _runClip : _idleClip);
        }
    }
}
