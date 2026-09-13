using Braziliation.Core;
using UnityEngine;

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
            if (GameInput.AttackPressedThisFrame)
                TryAttack();
        }

        private void TryAttack()
        {
            if (Time.time < _nextAttackTime)
                return;

            _nextAttackTime = Time.time + _attackCooldown;

            var origin = _attackOrigin != null ? _attackOrigin.position : transform.position;
            var mask = _enemyMask.value != 0 ? _enemyMask : GameLayers.EnemyMask;

            var hits = mask.value != 0
                ? Physics2D.OverlapCircleAll(origin, _attackRadius, mask)
                : Physics2D.OverlapCircleAll(origin, _attackRadius);

            foreach (var hit in hits)
            {
                // Sem esse filtro o golpe pega o próprio colisor do jogador e ele
                // se machuca a cada ataque.
                if (hit == null || hit.transform.IsChildOf(transform))
                    continue;

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
