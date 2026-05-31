using UnityEngine;
using UnityEngine.Events;
using Braziliation.Core;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Componente de vida e dano para player e inimigos.
    /// </summary>
    public sealed class HealthComponent : MonoBehaviour, IDamageable
    {
        [Header("Vida")]
        [SerializeField] private float _maxHealth = 100f;
        [SerializeField] private bool _destroyOnDeath = false;

        [Header("Eventos")]
        public UnityEvent<float, float> OnHealthChanged;
        public UnityEvent OnDamaged;
        public UnityEvent OnDied;

        public float CurrentHealth { get; private set; }
        public float MaxHealth => _maxHealth;
        public bool IsDead => CurrentHealth <= 0f;

        private void Awake()
        {
            _maxHealth = Mathf.Max(1f, _maxHealth);
            CurrentHealth = _maxHealth;
            OnHealthChanged?.Invoke(CurrentHealth, _maxHealth);
        }

        public void TakeDamage(float amount)
        {
            if (IsDead || amount <= 0f)
                return;

            CurrentHealth = Mathf.Max(0f, CurrentHealth - amount);
            OnDamaged?.Invoke();
            OnHealthChanged?.Invoke(CurrentHealth, _maxHealth);

            if (CurrentHealth <= 0f)
            {
                OnDied?.Invoke();
                if (_destroyOnDeath)
                    Destroy(gameObject);
            }
        }

        public void Heal(float amount)
        {
            if (IsDead || amount <= 0f)
                return;

            CurrentHealth = Mathf.Min(_maxHealth, CurrentHealth + amount);
            OnHealthChanged?.Invoke(CurrentHealth, _maxHealth);
        }

        public void SetMaxHealth(float newMaxHealth, bool healToFull)
        {
            _maxHealth = Mathf.Max(1f, newMaxHealth);
            CurrentHealth = healToFull ? _maxHealth : Mathf.Min(CurrentHealth, _maxHealth);
            OnHealthChanged?.Invoke(CurrentHealth, _maxHealth);
        }
    }
}
