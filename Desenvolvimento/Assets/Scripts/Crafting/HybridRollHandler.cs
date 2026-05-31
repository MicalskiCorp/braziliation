using UnityEngine;
using UnityEngine.Events;
using Braziliation.Crafting;
using Braziliation.Core;

namespace Braziliation.Crafting
{
    /// <summary>
    /// Gerencia o sorteio 50/50 ao craftar um item híbrido com componente de terceiro tipo.
    ///
    /// Conforme Crafting.md — Regras da Mesa:
    ///   "Item híbrido (2 tipos) + componente de 3º tipo → Item de 2 tipos;
    ///    qual dos dois tipos do híbrido acompanha é definido por sorteio 50/50."
    /// </summary>
    public sealed class HybridRollHandler : MonoBehaviour
    {
        [Header("Eventos")]
        /// <summary>Disparado com o item resultante após o sorteio 50/50.</summary>
        public UnityEvent<ItemComponent> OnHybridRollComplete;

        // TODO-DESIGN: decidir se o sorteio usa seed fixa (determinismo/replay) ou aleatória (imprevisibilidade)
        [SerializeField] private bool _usarSeedFixa = false;
        // TODO-DESIGN: valor da seed fixa a definir pelo game design
        [SerializeField] private int _seedFixa = 0;

        private CraftingService _craftingService;

        private void Awake()
        {
            _craftingService = GameServiceLocator.Instance != null
                ? GameServiceLocator.Instance.Resolve<CraftingService>()
                : new CraftingService();
        }

        /// <summary>
        /// Tenta realizar um craft híbrido de terceiro tipo.
        /// Executa o sorteio 50/50 apenas se os inputs configurarem craft de pilares diferentes.
        /// Dispara <see cref="OnHybridRollComplete"/> com o item resultante.
        /// </summary>
        /// <param name="itemHibrido">Item híbrido (2 tipos) já na mesa de crafting.</param>
        /// <param name="componenteTerceiroTipo">Componente de terceiro tipo sendo adicionado.</param>
        public void TentarCraftHibrido(ItemComponent itemHibrido, ItemComponent componenteTerceiroTipo)
        {
            if (itemHibrido == null || componenteTerceiroTipo == null)
            {
                Debug.LogWarning("[HybridRollHandler] Inputs inválidos para craft híbrido.");
                return;
            }

            if (!_craftingService.IsHybridCraft(itemHibrido, componenteTerceiroTipo))
            {
                Debug.Log("[HybridRollHandler] Inputs não configuram craft híbrido de pilares diferentes.");
                return;
            }

            // Usa seed de UnityEngine.Random para garantir integração com o sistema de aleatoriedade Unity
            int seed = _usarSeedFixa
                ? _seedFixa
                : UnityEngine.Random.Range(int.MinValue, int.MaxValue);

            var rng = new System.Random(seed);
            var itemResultante = _craftingService.RollHybridResult(itemHibrido, componenteTerceiroTipo, rng);

            // TODO-DESIGN: efeito visual/sonoro do sorteio (animação de "roleta de pilar") a definir
            OnHybridRollComplete?.Invoke(itemResultante);
        }
    }
}
