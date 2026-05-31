using Braziliation.Core;
using UnityEngine;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Inimigo básico com patrulha horizontal, perseguição curta e dano por contato.
    /// </summary>
    [RequireComponent(typeof(Rigidbody2D))]
    public sealed class EnemyController : MonoBehaviour
    {
        [Header("Patrulha")]
        [SerializeField] private Transform _leftPoint;
        [SerializeField] private Transform _rightPoint;
        [SerializeField] private float _patrolSpeed = 2f;

        [Header("Perseguição")]
        [SerializeField] private Transform _target;
        [SerializeField] private float _detectRadius = 4f;
        [SerializeField] private float _chaseSpeed = 3f;

        [Header("Dano por contato")]
        [SerializeField] private float _contactDamage = 10f;
        [SerializeField] private float _damageInterval = 0.5f;

        private Rigidbody2D _rigidbody;
        private int _direction = 1;
        private float _nextDamageTime;

        private void Awake()
        {
            _rigidbody = GetComponent<Rigidbody2D>();
        }

        public void SetTarget(Transform target)
        {
            _target = target;
        }

        public void SetPatrolPoints(Transform leftPoint, Transform rightPoint)
        {
            _leftPoint = leftPoint;
            _rightPoint = rightPoint;
        }

        private void FixedUpdate()
        {
            var speed = _patrolSpeed;
            var targetX = PatrolTargetX();

            if (_target != null && Vector2.Distance(transform.position, _target.position) <= _detectRadius)
            {
                speed = _chaseSpeed;
                targetX = _target.position.x;
            }

            var moveDir = Mathf.Sign(targetX - transform.position.x);
            if (Mathf.Abs(targetX - transform.position.x) > 0.05f)
                _direction = moveDir >= 0f ? 1 : -1;

            var velocity = _rigidbody.linearVelocity;
            velocity.x = _direction * speed;
            _rigidbody.linearVelocity = velocity;

            UpdatePatrolDirection();
        }

        private float PatrolTargetX()
        {
            if (_leftPoint == null || _rightPoint == null)
                return transform.position.x + _direction;

            return _direction > 0 ? _rightPoint.position.x : _leftPoint.position.x;
        }

        private void UpdatePatrolDirection()
        {
            if (_leftPoint == null || _rightPoint == null)
                return;

            if (_direction < 0 && transform.position.x <= _leftPoint.position.x)
                _direction = 1;
            else if (_direction > 0 && transform.position.x >= _rightPoint.position.x)
                _direction = -1;
        }

        private void OnCollisionStay2D(Collision2D collision)
        {
            if (Time.time < _nextDamageTime)
                return;

            var damageable = collision.collider.GetComponent<IDamageable>();
            if (damageable == null)
                damageable = collision.collider.GetComponentInParent<IDamageable>();

            if (damageable != null)
            {
                damageable.TakeDamage(_contactDamage);
                _nextDamageTime = Time.time + _damageInterval;
            }
        }

#if UNITY_EDITOR
        private void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(transform.position, _detectRadius);

            if (_leftPoint != null && _rightPoint != null)
            {
                Gizmos.color = Color.magenta;
                Gizmos.DrawLine(_leftPoint.position, _rightPoint.position);
            }
        }
#endif
    }
}
