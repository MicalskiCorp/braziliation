using UnityEngine;
using UnityEngine.Events;
using Braziliation.Crafting;
using Braziliation.Core;

namespace Braziliation.Build
{
    /// <summary>
    /// Totem de troca de itens nos slots da build.
    /// Permite substituir itens instalados sem custo algum, devolvendo o item antigo ao inventário.
    ///
    /// Conforme Build.md — Troca de Itens nos Slots:
    ///   "O jogador pode substituir itens nos slots livremente, sem custo,
    ///    dirigindo-se a um totem localizado em pontos específicos do mapa."
    ///
    /// TODO-DESIGN: localização de totens no mapa a definir (quantidade, cidades, áreas)
    /// </summary>
    public sealed class ItemSwapTotem : MonoBehaviour, IInteractable
    {
        [Header("Referências")]
        [SerializeField] private ReceptacleController _receptacleController;

        [Header("Eventos")]
        /// <summary>Disparado ao concluir uma troca. Parâmetro: o novo item instalado.</summary>
        public UnityEvent<ItemComponent> OnItemSwapped;

        /// <summary>
        /// Implementação de IInteractable — acionado quando o jogador interage com o totem.
        /// Abre a interface de seleção de slot e escolha de item para troca.
        /// TODO: integrar com sistema de UI de troca de slots.
        /// </summary>
        public void Interact()
        {
            // TODO: abrir painel de UI para seleção de receptáculo, slot e item a instalar
            Debug.Log("[ItemSwapTotem] Totem de troca ativado.");
        }

        /// <summary>
        /// Substitui o item instalado em um slot pelo novo item informado, sem custo.
        /// O item antigo é devolvido ao inventário — nenhum item é descartado.
        /// </summary>
        /// <param name="receptacle">Receptáculo alvo.</param>
        /// <param name="slotIndex">Índice do slot a ser substituído.</param>
        /// <param name="novoItem">Novo item a instalar no slot.</param>
        /// <param name="inventory">Inventário do jogador para receber o item removido.</param>
        public void SwapItem(ReceptacleType receptacle, int slotIndex, ItemComponent novoItem, PlayerInventory inventory)
        {
            if (_receptacleController == null)
            {
                Debug.LogWarning("[ItemSwapTotem] ReceptacleController não atribuído.");
                return;
            }

            var data = _receptacleController.GetReceptacle(receptacle);
            if (data == null)
            {
                Debug.LogWarning($"[ItemSwapTotem] Receptáculo '{receptacle}' não encontrado.");
                return;
            }

            if (slotIndex < 0 || slotIndex >= data.Slots.Count)
            {
                Debug.LogWarning($"[ItemSwapTotem] Índice de slot inválido: {slotIndex}");
                return;
            }

            var slot = data.Slots[slotIndex];
            var itemAntigo = slot.EquippedItem;

            // Instala o novo item — reutiliza a lógica centralizada do ReceptacleController
            _receptacleController.EquipItem(receptacle, slotIndex, novoItem);

            // Devolve o item antigo ao inventário, se o slot não estava vazio
            if (itemAntigo != null)
                inventory?.AddItem(itemAntigo);

            OnItemSwapped?.Invoke(novoItem);
        }
    }
}
