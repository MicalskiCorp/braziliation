using Braziliation.Gameplay;
using UnityEngine;

namespace Braziliation.UI
{
    /// <summary>
    /// HUD mínimo de vida desenhado com OnGUI para prototipação rápida.
    /// </summary>
    public sealed class SimpleHealthHud : MonoBehaviour
    {
        [Header("Fonte de Vida")]
        [SerializeField] private HealthComponent _targetHealth;

        [Header("Layout")]
        [SerializeField] private Vector2 _position = new Vector2(20f, 20f);
        [SerializeField] private Vector2 _size = new Vector2(280f, 26f);

        [Header("Cores")]
        [SerializeField] private Color _backgroundColor = new Color(0f, 0f, 0f, 0.6f);
        [SerializeField] private Color _fillColor = new Color(0.2f, 0.9f, 0.35f, 0.95f);

        public void Bind(HealthComponent health)
        {
            _targetHealth = health;
        }

        private void Update()
        {
            if (_targetHealth == null)
            {
                var player = GameObject.FindWithTag("Player");
                if (player != null)
                    _targetHealth = player.GetComponent<HealthComponent>();
            }
        }

        private void OnGUI()
        {
            if (_targetHealth == null)
                return;

            var percent = Mathf.Clamp01(_targetHealth.CurrentHealth / _targetHealth.MaxHealth);
            var bgRect = new Rect(_position.x, _position.y, _size.x, _size.y);
            var fillRect = new Rect(_position.x + 2f, _position.y + 2f, (_size.x - 4f) * percent, _size.y - 4f);

            var oldColor = GUI.color;
            GUI.color = _backgroundColor;
            GUI.DrawTexture(bgRect, Texture2D.whiteTexture);

            GUI.color = _fillColor;
            GUI.DrawTexture(fillRect, Texture2D.whiteTexture);

            GUI.color = Color.white;
            GUI.Label(new Rect(_position.x + 8f, _position.y + 4f, _size.x, _size.y),
                $"HP: {Mathf.CeilToInt(_targetHealth.CurrentHealth)}/{Mathf.CeilToInt(_targetHealth.MaxHealth)}");
            GUI.color = oldColor;
        }
    }
}
