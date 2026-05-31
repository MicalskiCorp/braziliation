using Braziliation.Core;
using UnityEngine;
using UnityEngine.InputSystem;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Combate básico do jogador com ataque corpo a corpo em área curta.
    /// </summary>
    public sealed class PlayerCombat : MonoBehaviour
    {
        [Header("Ataque")]
        [SerializeField] private Transform _attackOrigin;
        [SerializeField] private float _attackRadius = 0.8f;
        [SerializeField] private float _attackDamage = 10f;
        [SerializeField] private float _attackCooldown = 0.25f;
        [SerializeField] private LayerMask _enemyMask;

        private float _nextAttackTime;

        private void Update()
        {
            if (WasAttackPressedThisFrame())
                TryAttack();
        }

        private void TryAttack()
        {
            if (Time.time < _nextAttackTime)
                return;

            _nextAttackTime = Time.time + _attackCooldown;

            var origin = _attackOrigin != null ? _attackOrigin.position : transform.position;
            var hits = _enemyMask.value == 0
                ? Physics2D.OverlapCircleAll(origin, _attackRadius)
                : Physics2D.OverlapCircleAll(origin, _attackRadius, _enemyMask);
            foreach (var hit in hits)
            {
                var damageable = hit.GetComponent<IDamageable>();
                if (damageable == null)
                    damageable = hit.GetComponentInParent<IDamageable>();

                damageable?.TakeDamage(_attackDamage);
            }
        }

        public void SetAttackDamage(float damage)
        {
            _attackDamage = Mathf.Max(0f, damage);
        }

        private static bool WasAttackPressedThisFrame()
        {
            var mouse = Mouse.current;
            if (mouse != null && mouse.leftButton.wasPressedThisFrame)
                return true;

            var keyboard = Keyboard.current;
            if (keyboard != null && keyboard.fKey.wasPressedThisFrame)
                return true;

            var gamepad = Gamepad.current;
            return gamepad != null && gamepad.rightShoulder.wasPressedThisFrame;
        }

#if UNITY_EDITOR
        private void OnDrawGizmosSelected()
        {
            var origin = _attackOrigin != null ? _attackOrigin.position : transform.position;
            Gizmos.color = Color.red;
            Gizmos.DrawWireSphere(origin, _attackRadius);
        }
#endif
    }
}
