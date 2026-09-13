using Braziliation.Core;
using Braziliation.Enemies;
using Braziliation.Gameplay.Enemies;
using UnityEngine;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Adaptador Unity do motor de IA de inimigos.
    ///
    /// Este componente **não decide nada**: ele lê o mundo (chão, parede, precipício,
    /// alvo), entrega isso ao <see cref="EnemyBrain"/> — C# puro, testado sem engine
    /// em Tests/Braziliation.Game.Tests/EnemyBrainTests.cs — e aplica a decisão no
    /// Rigidbody2D. Trocar o comportamento de um inimigo é trocar o perfil, não o código.
    ///
    /// Convenção de pivot: o sprite tem pivot no centro-inferior, então
    /// <c>transform.position</c> é o pé do inimigo. Os sensores partem dali.
    /// </summary>
    [RequireComponent(typeof(Rigidbody2D))]
    public sealed class EnemyController : MonoBehaviour
    {
        [Header("Perfil de comportamento")]
        [Tooltip("Se preenchido, substitui todos os valores abaixo.")]
        [SerializeField] private EnemyProfileAsset _profileAsset;

        [SerializeField] private EnemyAggressionStyle _style = EnemyAggressionStyle.Patroller;

        [Header("Patrulha")]
        [Tooltip("Opcionais: se preenchidos, definem a faixa de patrulha. A posição é lida " +
                 "uma única vez no Start — depois disso mover os pontos não afeta nada.")]
        [SerializeField] private Transform _leftPoint;
        [SerializeField] private Transform _rightPoint;
        [SerializeField] private float _patrolSpeed = 1.6f;
        [Tooltip("Usado quando não há pontos de patrulha: meia-largura ao redor do spawn.")]
        [SerializeField] private float _patrolRange = 2f;
        [SerializeField] private float _patrolPauseSeconds = 0.6f;

        [Header("Perseguição")]
        [SerializeField] private Transform _target;
        [SerializeField] private float _detectRadius = 5f;
        [SerializeField] private float _loseTargetRadius = 7.5f;
        [SerializeField] private float _leashRadius = 8f;
        [SerializeField] private float _chaseSpeed = 3.2f;
        [SerializeField] private float _reactionSeconds = 0.25f;

        [Header("Ataque")]
        [SerializeField] private float _attackRange = 1.4f;
        [SerializeField] private float _attackDamage = 12f;
        [SerializeField] private float _attackWindupSeconds = 0.2f;
        [SerializeField] private float _attackCooldownSeconds = 1.1f;

        [Header("Dano por contato")]
        [SerializeField] private float _contactDamage = 10f;
        [SerializeField] private float _damageInterval = 0.5f;

        [Header("Terreno")]
        [SerializeField] private bool _turnsAtLedges = true;
        [SerializeField] private bool _turnsAtWalls = true;
        [SerializeField] private bool _canJump;
        [SerializeField] private float _jumpForce = 9f;

        [Header("Sensores")]
        [SerializeField] private LayerMask _groundMask;
        [SerializeField] private LayerMask _targetMask;
        [Tooltip("Quanto à frente dos pés o sensor procura chão.")]
        [SerializeField] private float _ledgeProbeDistance = 0.5f;
        [Tooltip("Profundidade da busca por chão à frente. Menor que isso conta como precipício.")]
        [SerializeField] private float _ledgeProbeDepth = 0.6f;

        [Header("Sprite")]
        [Tooltip("Desmarque quando a arte original olha para a esquerda (caso do cão).")]
        [SerializeField] private bool _spriteFacesRight = true;

        private Rigidbody2D _rigidbody;
        private Collider2D _collider;
        private SpriteRenderer _renderer;
        private HealthComponent _health;
        private EnemyBrain _brain;

        private float _anchorX;
        private float _nextContactDamageTime;
        private EnemyIntent _intent;

        /// <summary>Estado atual da IA. Usado pela animação e por depuração.</summary>
        public EnemyState State => _brain?.State ?? EnemyState.Idle;

        /// <summary>Direção que o inimigo encara: -1 esquerda, 1 direita.</summary>
        public int Facing => _brain?.Facing ?? 1;

        private void Awake()
        {
            _rigidbody = GetComponent<Rigidbody2D>();
            _collider = GetComponent<Collider2D>();
            _renderer = GetComponentInChildren<SpriteRenderer>();
            _health = GetComponent<HealthComponent>();
        }

        private void Start()
        {
            _anchorX = transform.position.x;
            _brain = new EnemyBrain(BuildProfile(), _spriteFacesRight ? 1 : -1);
        }

        public void SetTarget(Transform target) => _target = target;

        /// <summary>
        /// Define a faixa de patrulha por dois marcadores. A posição deles é lida no
        /// Start e convertida em uma faixa fixa em coordenadas de mundo — antes, com os
        /// marcadores presos ao próprio inimigo, eles andavam junto e a ponta nunca era
        /// alcançada, então o inimigo caminhava para sempre até cair do mapa.
        /// </summary>
        public void SetPatrolPoints(Transform leftPoint, Transform rightPoint)
        {
            _leftPoint = leftPoint;
            _rightPoint = rightPoint;
        }

        /// <summary>Informa se a arte original olha para a direita, para o espelhamento sair certo.</summary>
        public void SetSpriteFacesRight(bool facesRight) => _spriteFacesRight = facesRight;

        public void SetProfile(EnemyProfileAsset profileAsset)
        {
            _profileAsset = profileAsset;
            if (_brain != null)
                _brain = new EnemyBrain(BuildProfile(), _brain.Facing);
        }

        private EnemyBehaviorProfile BuildProfile()
        {
            if (_profileAsset != null)
                return _profileAsset.ToProfile();

            var range = _patrolRange;
            if (_leftPoint != null && _rightPoint != null)
            {
                var left = Mathf.Min(_leftPoint.position.x, _rightPoint.position.x);
                var right = Mathf.Max(_leftPoint.position.x, _rightPoint.position.x);
                _anchorX = (left + right) * 0.5f;
                range = (right - left) * 0.5f;
            }

            return new EnemyBehaviorProfile
            {
                Id = name,
                Style = _style,
                PatrolSpeed = _patrolSpeed,
                PatrolRange = range,
                PatrolPauseSeconds = _patrolPauseSeconds,
                ChaseSpeed = _chaseSpeed,
                DetectRadius = _detectRadius,
                LoseTargetRadius = _loseTargetRadius,
                LeashRadius = _leashRadius,
                ReactionSeconds = _reactionSeconds,
                AttackRange = _attackRange,
                AttackWindupSeconds = _attackWindupSeconds,
                AttackCooldownSeconds = _attackCooldownSeconds,
                TurnsAtLedges = _turnsAtLedges,
                TurnsAtWalls = _turnsAtWalls,
                CanJump = _canJump,
            };
        }

        private void FixedUpdate()
        {
            if (_brain == null)
                return;

            _intent = _brain.Tick(ReadSenses(), Time.fixedDeltaTime);
            Apply(_intent);
        }

        // ----------------------------------------------------------------- sensores
        private EnemySenses ReadSenses()
        {
            var position = transform.position;
            var facing = _brain.Facing;

            var hasTarget = _target != null;
            var targetX = hasTarget ? _target.position.x : position.x;
            var targetDistance = hasTarget
                ? Vector2.Distance(position, _target.position)
                : float.MaxValue;

            return new EnemySenses(
                position.x,
                _anchorX,
                hasTarget,
                targetX,
                targetDistance,
                IsGrounded(),
                HasWallAhead(facing),
                HasLedgeAhead(facing),
                HealthFraction(),
                facing);
        }

        private LayerMask GroundMask => _groundMask.value != 0 ? _groundMask : GameLayers.GroundMask;

        private float BodyHeight => _collider != null ? _collider.bounds.size.y : 1f;

        private float BodyHalfWidth => _collider != null ? _collider.bounds.extents.x : 0.5f;

        private bool IsGrounded()
        {
            var origin = (Vector2)transform.position + Vector2.up * 0.05f;
            var hit = Physics2D.Raycast(origin, Vector2.down, 0.25f, GroundMask);
            return hit.collider != null;
        }

        private bool HasWallAhead(int facing)
        {
            var origin = (Vector2)transform.position + Vector2.up * (BodyHeight * 0.5f);
            var hit = Physics2D.Raycast(origin, Vector2.right * facing,
                                        BodyHalfWidth + 0.15f, GroundMask);
            return hit.collider != null;
        }

        /// <summary>Falta chão logo à frente? É isto que impede o inimigo de andar para fora do mapa.</summary>
        private bool HasLedgeAhead(int facing)
        {
            var origin = (Vector2)transform.position
                         + Vector2.right * (facing * (BodyHalfWidth + _ledgeProbeDistance))
                         + Vector2.up * 0.1f;
            var hit = Physics2D.Raycast(origin, Vector2.down, _ledgeProbeDepth, GroundMask);
            return hit.collider == null;
        }

        private float HealthFraction()
        {
            if (_health == null)
                return 1f;

            return _health.MaxHealth <= 0f ? 0f : _health.CurrentHealth / _health.MaxHealth;
        }

        // -------------------------------------------------------------- aplicação
        private void Apply(in EnemyIntent intent)
        {
            var velocity = _rigidbody.linearVelocity;
            velocity.x = intent.VelocityX;

            if (intent.Jump && IsGrounded())
                velocity.y = _jumpForce;

            _rigidbody.linearVelocity = velocity;

            if (_renderer != null)
                _renderer.flipX = _spriteFacesRight ? intent.Facing < 0 : intent.Facing > 0;

            if (intent.Attack)
                PerformAttack(intent.Facing);
        }

        private void PerformAttack(int facing)
        {
            var origin = (Vector2)transform.position
                         + Vector2.up * (BodyHeight * 0.5f)
                         + Vector2.right * (facing * _attackRange * 0.5f);

            var mask = _targetMask.value != 0 ? _targetMask : GameLayers.PlayerMask;
            var hits = mask.value != 0
                ? Physics2D.OverlapCircleAll(origin, _attackRange * 0.6f, mask)
                : Physics2D.OverlapCircleAll(origin, _attackRange * 0.6f);

            foreach (var hit in hits)
            {
                if (hit == null || hit.transform.IsChildOf(transform))
                    continue;

                var damageable = hit.GetComponent<IDamageable>() ?? hit.GetComponentInParent<IDamageable>();
                damageable?.TakeDamage(_attackDamage);
            }
        }

        private void OnCollisionStay2D(Collision2D collision)
        {
            if (_contactDamage <= 0f || Time.time < _nextContactDamageTime)
                return;

            if (collision.collider == null || collision.collider.transform.IsChildOf(transform))
                return;

            var damageable = collision.collider.GetComponent<IDamageable>()
                             ?? collision.collider.GetComponentInParent<IDamageable>();

            if (damageable == null)
                return;

            damageable.TakeDamage(_contactDamage);
            _nextContactDamageTime = Time.time + _damageInterval;
        }

#if UNITY_EDITOR
        private void OnDrawGizmosSelected()
        {
            var position = transform.position;
            var anchorX = Application.isPlaying ? _anchorX : position.x;

            Gizmos.color = Color.yellow;
            Gizmos.DrawWireSphere(position, _detectRadius);

            Gizmos.color = new Color(1f, 0.6f, 0f, 0.6f);
            Gizmos.DrawWireSphere(position, _loseTargetRadius);

            var range = _patrolRange;
            if (_leftPoint != null && _rightPoint != null)
            {
                var left = Mathf.Min(_leftPoint.position.x, _rightPoint.position.x);
                var right = Mathf.Max(_leftPoint.position.x, _rightPoint.position.x);
                anchorX = (left + right) * 0.5f;
                range = (right - left) * 0.5f;
            }

            Gizmos.color = Color.magenta;
            Gizmos.DrawLine(new Vector3(anchorX - range, position.y, 0f),
                            new Vector3(anchorX + range, position.y, 0f));

            var facing = Application.isPlaying ? Facing : 1;
            Gizmos.color = Color.cyan;
            var ledgeOrigin = new Vector3(position.x + facing * (BodyHalfWidth + _ledgeProbeDistance),
                                          position.y + 0.1f, 0f);
            Gizmos.DrawLine(ledgeOrigin, ledgeOrigin + Vector3.down * _ledgeProbeDepth);
        }
#endif
    }
}
