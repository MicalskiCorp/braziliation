using Braziliation.Enemies;
using UnityEngine;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Traduz o estado da IA (<see cref="EnemyState"/>) em clipes do
    /// <see cref="SpriteSheetAnimator"/>. O espelhamento do sprite é feito pelo
    /// <see cref="EnemyController"/>, que já conhece a direção decidida pelo cérebro.
    /// </summary>
    [RequireComponent(typeof(EnemyController))]
    public sealed class EnemySpriteAnimation : MonoBehaviour
    {
        [SerializeField] private SpriteSheetAnimator _animator;

        [Header("Clipes")]
        [SerializeField] private string _idleClip = "idle";
        [SerializeField] private string _walkClip = "walk";
        [Tooltip("Deixe vazio para reaproveitar o clipe de caminhada na perseguição.")]
        [SerializeField] private string _chaseClip = "";
        [Tooltip("Deixe vazio para reaproveitar o clipe parado no ataque.")]
        [SerializeField] private string _attackClip = "";

        private EnemyController _controller;

        private void Awake()
        {
            _controller = GetComponent<EnemyController>();

            if (_animator == null)
                _animator = GetComponentInChildren<SpriteSheetAnimator>();
        }

        private void Update()
        {
            if (_animator == null)
                return;

            _animator.Play(ClipFor(_controller.State));
        }

        private string ClipFor(EnemyState state)
        {
            switch (state)
            {
                case EnemyState.Patrol:
                case EnemyState.Returning:
                case EnemyState.Reposition:
                case EnemyState.Flee:
                    return _walkClip;

                case EnemyState.Chase:
                    return string.IsNullOrEmpty(_chaseClip) ? _walkClip : _chaseClip;

                case EnemyState.Attack:
                    return string.IsNullOrEmpty(_attackClip) ? _idleClip : _attackClip;

                default:
                    return _idleClip;
            }
        }
    }
}
