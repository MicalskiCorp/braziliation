using Braziliation.Gameplay;
using UnityEngine;
using UnityEngine.UI;

namespace Braziliation.UI
{
    /// <summary>
    /// HUD de vida usando Canvas + Slider para a demo.
    /// </summary>
    public sealed class CanvasHealthHud : MonoBehaviour
    {
        [Header("Fonte de Vida")]
        [SerializeField] private HealthComponent _targetHealth;

        [Header("UI")]
        [SerializeField] private Slider _healthSlider;
        [SerializeField] private Text _healthLabel;

        public void Configure(HealthComponent targetHealth, Slider healthSlider, Text healthLabel)
        {
            _targetHealth = targetHealth;
            _healthSlider = healthSlider;
            _healthLabel = healthLabel;
            Refresh();
        }

        public void Bind(HealthComponent targetHealth)
        {
            _targetHealth = targetHealth;
            Refresh();
        }

        private void OnEnable()
        {
            if (_targetHealth != null)
                _targetHealth.OnHealthChanged.AddListener(OnHealthChanged);

            Refresh();
        }

        private void OnDisable()
        {
            if (_targetHealth != null)
                _targetHealth.OnHealthChanged.RemoveListener(OnHealthChanged);
        }

        private void Update()
        {
            if (_targetHealth != null)
                return;

            GameObject player = null;
            try
            {
                player = GameObject.FindWithTag("Player");
            }
            catch (UnityException)
            {
                // Tag pode não existir no projeto ainda.
            }

            if (player != null)
            {
                _targetHealth = player.GetComponent<HealthComponent>();
                if (_targetHealth != null)
                    _targetHealth.OnHealthChanged.AddListener(OnHealthChanged);

                Refresh();
            }
        }

        private void OnHealthChanged(float current, float max)
        {
            Refresh(current, max);
        }

        private void Refresh()
        {
            if (_targetHealth == null)
                return;

            Refresh(_targetHealth.CurrentHealth, _targetHealth.MaxHealth);
        }

        private void Refresh(float currentHealth, float maxHealth)
        {
            if (_healthSlider != null)
            {
                _healthSlider.minValue = 0f;
                _healthSlider.maxValue = Mathf.Max(1f, maxHealth);
                _healthSlider.value = Mathf.Clamp(currentHealth, 0f, _healthSlider.maxValue);
            }

            if (_healthLabel != null)
            {
                _healthLabel.text = $"HP {Mathf.CeilToInt(currentHealth)}/{Mathf.CeilToInt(maxHealth)}";
            }
        }
    }
}
