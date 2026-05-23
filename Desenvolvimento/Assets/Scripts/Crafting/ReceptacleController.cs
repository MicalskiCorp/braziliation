using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using Braziliation.Core;
using Braziliation.Crafting;

namespace Braziliation.Crafting
{
    /// <summary>
    /// Gerencia os três receptáculos da build do personagem no contexto Unity.
    /// Instala e remove itens dos slots, comunicando mudanças via UnityEvents para a UI e demais sistemas.
    ///
    /// Receptáculos conforme Build.md:
    ///   - Exoesqueleto dos Trilhos (Mecânico)
    ///   - Capa das Lendas do Mar (Místico)
    ///   - Espinha de Fungo (Biológico)
    /// </summary>
    public sealed class ReceptacleController : MonoBehaviour
    {
        [Header("Referências")]
        // TODO: conectar via GameServiceLocator
        [SerializeField] private PlayerInventory _playerInventory;

        [Header("Eventos")]
        /// <summary>Disparado ao instalar um item. Parâmetros: receptáculo, índice do slot, item instalado.</summary>
        public UnityEvent<ReceptacleType, int, ItemComponent> OnItemEquipped;

        /// <summary>Disparado ao remover um item. Parâmetros: receptáculo, índice do slot.</summary>
        public UnityEvent<ReceptacleType, int> OnItemUnequipped;

        // TODO: conectar via GameServiceLocator
        // private CraftingService _craftingService;

        // Dados de runtime dos três receptáculos — inicializados em Awake
        private readonly Dictionary<ReceptacleType, ReceptacleData> _receptaculos =
            new Dictionary<ReceptacleType, ReceptacleData>();

        private void Awake()
        {
            // Inicializa os receptáculos com configuração base conforme a spec (Build.md)
            _receptaculos[ReceptacleType.Exoskeleton] = new ReceptacleData
            {
                DisplayName = "Exoesqueleto dos Trilhos",
                Type        = ReceptacleType.Exoskeleton,
                Pillar      = PillarType.Mechanical
            };
            _receptaculos[ReceptacleType.Cape] = new ReceptacleData
            {
                DisplayName = "Capa das Lendas do Mar",
                Type        = ReceptacleType.Cape,
                Pillar      = PillarType.Mystical
            };
            _receptaculos[ReceptacleType.Spine] = new ReceptacleData
            {
                DisplayName = "Espinha de Fungo",
                Type        = ReceptacleType.Spine,
                Pillar      = PillarType.Biological
            };

            // TODO: conectar via GameServiceLocator
            // _craftingService = GameServiceLocator.Instance.CraftingService;
        }

        /// <summary>
        /// Instala um item no slot especificado do receptáculo informado.
        /// Valida índice de slot antes de instalar.
        /// </summary>
        /// <param name="receptacle">Receptáculo alvo.</param>
        /// <param name="slotIndex">Índice do slot onde o item será instalado.</param>
        /// <param name="item">Item a instalar.</param>
        public void EquipItem(ReceptacleType receptacle, int slotIndex, ItemComponent item)
        {
            var data = GetReceptacle(receptacle);
            if (data == null)
            {
                Debug.LogWarning($"[ReceptacleController] Receptáculo '{receptacle}' não encontrado.");
                return;
            }

            if (slotIndex < 0 || slotIndex >= data.Slots.Count)
            {
                Debug.LogWarning($"[ReceptacleController] Índice de slot inválido: {slotIndex}");
                return;
            }

            data.Slots[slotIndex].EquippedItem = item;
            OnItemEquipped?.Invoke(receptacle, slotIndex, item);
        }

        /// <summary>
        /// Remove o item do slot especificado e o devolve ao inventário do jogador.
        /// Nenhum item é perdido na remoção (conforme Build.md — Troca de Itens nos Slots).
        /// </summary>
        /// <param name="receptacle">Receptáculo alvo.</param>
        /// <param name="slotIndex">Índice do slot a ser esvaziado.</param>
        public void UnequipItem(ReceptacleType receptacle, int slotIndex)
        {
            var data = GetReceptacle(receptacle);
            if (data == null)
            {
                Debug.LogWarning($"[ReceptacleController] Receptáculo '{receptacle}' não encontrado.");
                return;
            }

            if (slotIndex < 0 || slotIndex >= data.Slots.Count)
            {
                Debug.LogWarning($"[ReceptacleController] Índice de slot inválido: {slotIndex}");
                return;
            }

            var slot = data.Slots[slotIndex];
            if (slot.IsEmpty) return;

            var itemRemovido = slot.EquippedItem;
            slot.EquippedItem = null;

            // Devolve ao inventário — nenhum item é descartado
            _playerInventory?.AddItem(itemRemovido);

            OnItemUnequipped?.Invoke(receptacle, slotIndex);
        }

        /// <summary>
        /// Retorna o ReceptacleData do receptáculo informado, ou null se não encontrado.
        /// </summary>
        public ReceptacleData GetReceptacle(ReceptacleType type)
        {
            _receptaculos.TryGetValue(type, out var data);
            return data;
        }
    }
}
