using System.Collections.Generic;
using Braziliation.Core;
using UnityEngine;
using UnityEngine.InputSystem;

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

        private void Awake()
        {
            _rigidbody = GetComponent<Rigidbody2D>();

            if (_groundCheck == null)
            {
                var groundCheckObj = new GameObject("GroundCheck");
                groundCheckObj.transform.SetParent(transform);
                groundCheckObj.transform.localPosition = new Vector3(0f, -0.55f, 0f);
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

        private void Update()
        {
            _moveInput = ReadMoveInput();

            if (WasJumpPressedThisFrame() && IsGrounded())
                Jump();

            if (WasInteractPressedThisFrame())
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

        private bool IsGrounded()
        {
            if (_groundCheck == null)
                return false;

            if (_groundMask.value == 0)
                return Physics2D.OverlapCircle(_groundCheck.position, _groundCheckRadius) != null;

            return Physics2D.OverlapCircle(_groundCheck.position, _groundCheckRadius, _groundMask) != null;
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

        private static float ReadMoveInput()
        {
            float move = 0f;

            var keyboard = Keyboard.current;
            if (keyboard != null)
            {
                if (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed)
                    move -= 1f;
                if (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed)
                    move += 1f;
            }

            var gamepad = Gamepad.current;
            if (gamepad != null)
            {
                var stick = gamepad.leftStick.ReadValue().x;
                if (Mathf.Abs(stick) > Mathf.Abs(move))
                    move = stick;
            }

            return Mathf.Clamp(move, -1f, 1f);
        }

        private static bool WasJumpPressedThisFrame()
        {
            var keyboard = Keyboard.current;
            if (keyboard != null &&
                (keyboard.spaceKey.wasPressedThisFrame || keyboard.wKey.wasPressedThisFrame || keyboard.upArrowKey.wasPressedThisFrame))
            {
                return true;
            }

            var gamepad = Gamepad.current;
            return gamepad != null && gamepad.buttonSouth.wasPressedThisFrame;
        }

        private static bool WasInteractPressedThisFrame()
        {
            var keyboard = Keyboard.current;
            if (keyboard != null && keyboard.eKey.wasPressedThisFrame)
                return true;

            var gamepad = Gamepad.current;
            return gamepad != null && gamepad.buttonWest.wasPressedThisFrame;
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
