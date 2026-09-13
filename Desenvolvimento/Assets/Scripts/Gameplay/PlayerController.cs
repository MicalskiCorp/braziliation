using System.Collections.Generic;
using Braziliation.Core;
using UnityEngine;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Movimento básico do jogador (andar, pular) e interação com objetos próximos.
    /// </summary>
    [RequireComponent(typeof(Rigidbody2D))]
    public sealed class PlayerController : MonoBehaviour, IStatReceiver
    {
        [Header("Movimento")]
        [SerializeField] private float _moveSpeed = 5f;
        [SerializeField] private float _jumpForce = 12f;

        [Header("Detecção de chão")]
        [SerializeField] private Transform _groundCheck;
        [SerializeField] private float _groundCheckRadius = 0.2f;
        [SerializeField] private LayerMask _groundMask;

        [Header("Interação")]
        [SerializeField] private Transform _interactionOrigin;
        [SerializeField] private float _interactionRadius = 0.8f;
        [SerializeField] private LayerMask _interactableMask;

        private Rigidbody2D _rigidbody;
        private float _moveInput;
        private bool _grounded;
        private int _facing = 1;

        /// <summary>Entrada horizontal do frame, de -1 a 1.</summary>
        public float MoveInput => _moveInput;

        /// <summary>Resultado do último teste de chão. Evita repetir a consulta de física.</summary>
        public bool Grounded => _grounded;

        /// <summary>Direção que o jogador encara: -1 esquerda, 1 direita.</summary>
        public int Facing => _facing;

        /// <summary>Velocidade vertical atual, para a animação distinguir subida de queda.</summary>
        public float VerticalVelocity => _rigidbody != null ? _rigidbody.linearVelocity.y : 0f;

        private void Awake()
        {
            _rigidbody = GetComponent<Rigidbody2D>();

            if (_groundCheck == null)
            {
                var groundCheckObj = new GameObject("GroundCheck");
                groundCheckObj.transform.SetParent(transform);
                groundCheckObj.transform.localPosition = new Vector3(0f, GetColliderBottomLocalY() - 0.05f, 0f);
                _groundCheck = groundCheckObj.transform;
            }

            if (_interactionOrigin == null)
            {
                var interactionObj = new GameObject("InteractionOrigin");
                interactionObj.transform.SetParent(transform);
                interactionObj.transform.localPosition = new Vector3(0f, 0f, 0f);
                _interactionOrigin = interactionObj.transform;
            }
        }

        /// <summary>
        /// Base do collider em espaço local, para posicionar o GroundCheck logo abaixo
        /// dos pés. Sem isso o ponto de checagem fica preso a um offset fixo e deixa de
        /// tocar o chão sempre que o sprite (e portanto o collider) muda de tamanho.
        /// </summary>
        private float GetColliderBottomLocalY()
        {
            const float legacyOffsetY = -0.55f;

            var boxCollider = GetComponent<BoxCollider2D>();
            if (boxCollider != null)
                return boxCollider.offset.y - (boxCollider.size.y * 0.5f);

            var anyCollider = GetComponent<Collider2D>();
            if (anyCollider == null)
                return legacyOffsetY;

            var scaleY = transform.lossyScale.y;
            if (Mathf.Approximately(scaleY, 0f))
                return legacyOffsetY;

            return (anyCollider.bounds.min.y - transform.position.y) / scaleY;
        }

        private void Update()
        {
            _moveInput = GameInput.MoveX;
            _grounded = IsGrounded();

            if (!Mathf.Approximately(_moveInput, 0f))
                _facing = _moveInput > 0f ? 1 : -1;

            if (GameInput.JumpPressedThisFrame && _grounded)
                Jump();

            if (GameInput.InteractPressedThisFrame)
                Interact();
        }

        private void FixedUpdate()
        {
            var velocity = _rigidbody.linearVelocity;
            velocity.x = _moveInput * _moveSpeed;
            _rigidbody.linearVelocity = velocity;
        }

        public void ApplyStats(Dictionary<string, float> stats)
        {
            if (stats == null)
                return;

            if (stats.TryGetValue("speed", out var speedBonus))
                _moveSpeed = Mathf.Max(1f, 5f + speedBonus);

            if (stats.TryGetValue("jump", out var jumpBonus))
                _jumpForce = Mathf.Max(1f, 12f + jumpBonus);
        }

        private void Jump()
        {
            var velocity = _rigidbody.linearVelocity;
            velocity.y = _jumpForce;
            _rigidbody.linearVelocity = velocity;
        }

        /// <summary>
        /// Só é "no chão" se o círculo de checagem tocar um colisor que **não seja do
        /// próprio jogador**. Sem esse filtro o teste encosta no corpo do player e o
        /// pulo pode ser repetido no ar indefinidamente.
        /// </summary>
        private bool IsGrounded()
        {
            if (_groundCheck == null)
                return false;

            var mask = _groundMask.value != 0 ? _groundMask : GameLayers.GroundMask;

            var hits = mask.value != 0
                ? Physics2D.OverlapCircleAll(_groundCheck.position, _groundCheckRadius, mask)
                : Physics2D.OverlapCircleAll(_groundCheck.position, _groundCheckRadius);

            foreach (var hit in hits)
            {
                if (hit == null || hit.isTrigger)
                    continue;

                if (hit.transform.IsChildOf(transform))
                    continue;

                return true;
            }

            return false;
        }

        private void Interact()
        {
            var origin = _interactionOrigin != null ? _interactionOrigin.position : transform.position;
            var hits = _interactableMask.value == 0
                ? Physics2D.OverlapCircleAll(origin, _interactionRadius)
                : Physics2D.OverlapCircleAll(origin, _interactionRadius, _interactableMask);

            foreach (var hit in hits)
            {
                var interactable = hit.GetComponent<IInteractable>();
                if (interactable == null)
                    interactable = hit.GetComponentInParent<IInteractable>();

                if (interactable != null)
                {
                    interactable.Interact();
                    break;
                }
            }
        }

#if UNITY_EDITOR
        private void OnDrawGizmosSelected()
        {
            if (_groundCheck != null)
            {
                Gizmos.color = Color.green;
                Gizmos.DrawWireSphere(_groundCheck.position, _groundCheckRadius);
            }

            var origin = _interactionOrigin != null ? _interactionOrigin.position : transform.position;
            Gizmos.color = Color.cyan;
            Gizmos.DrawWireSphere(origin, _interactionRadius);
        }
#endif
    }
}
