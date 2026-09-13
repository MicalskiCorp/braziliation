using Braziliation.Core;
using UnityEngine;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Rede de segurança para queda fora do mapa: abaixo de <see cref="_killY"/> o objeto
    /// volta ao ponto de origem em vez de cair para sempre.
    ///
    /// As paredes nas pontas do chão já impedem sair andando; isto cobre o resto
    /// (pulo mal calculado, buraco de level design, empurrão de inimigo).
    /// </summary>
    public sealed class FallRespawn : MonoBehaviour
    {
        [Tooltip("Altura abaixo da qual o objeto é considerado perdido.")]
        [SerializeField] private float _killY = -12f;

        [Tooltip("Para onde voltar. Se vazio, usa a posição inicial do objeto.")]
        [SerializeField] private Transform _respawnPoint;

        [Tooltip("Dano aplicado ao cair. 0 desliga.")]
        [SerializeField] private float _fallDamage = 10f;

        private Vector3 _origin;
        private Rigidbody2D _rigidbody;
        private HealthComponent _health;

        private void Awake()
        {
            _origin = transform.position;
            _rigidbody = GetComponent<Rigidbody2D>();
            _health = GetComponent<HealthComponent>();
        }

        public void SetRespawnPoint(Vector3 position)
        {
            _origin = position;
            _respawnPoint = null;
        }

        private void FixedUpdate()
        {
            if (transform.position.y > _killY)
                return;

            Respawn();
        }

        private void Respawn()
        {
            var destination = _respawnPoint != null ? _respawnPoint.position : _origin;

            if (_rigidbody != null)
            {
                _rigidbody.linearVelocity = Vector2.zero;
                _rigidbody.angularVelocity = 0f;
                _rigidbody.position = destination;
            }

            transform.position = destination;

            if (_fallDamage > 0f && _health != null && !_health.IsDead)
                ((IDamageable)_health).TakeDamage(_fallDamage);
        }
    }
}
