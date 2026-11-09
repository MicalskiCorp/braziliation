using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using Braziliation.Build;
using Braziliation.Core;
using Braziliation.Crafting;

namespace Braziliation.Crafting
{
    /// <summary>
    /// Gerencia os três receptáculos da build do personagem no contexto Unity.
    /// Instala e remove itens dos slots, comunicando mudanças via UnityEvents para a UI e demais sistemas.
    /// Os receptáculos vivem no <see cref="BuildState"/> registrado no <see cref="GameServiceLocator"/>
    /// (fonte única); este componente só os altera.
    ///
    /// Receptáculos conforme Build.md:
    ///   - Exoesqueleto dos Trilhos (Mecânico)
    ///   - Capa das Lendas do Mar (Místico)
    ///   - Espinha de Fungo (Biológico)
    /// </summary>
    public sealed class ReceptacleController : MonoBehaviour
    {
        [Header("Referências")]
        [SerializeField] private PlayerInventory _playerInventory;

        [Header("Eventos")]
        /// <summary>Disparado ao instalar um item. Parâmetros: receptáculo, índice do slot, item instalado.</summary>
        public UnityEvent<ReceptacleType, int, ItemComponent> OnItemEquipped;

        /// <summary>Disparado ao remover um item. Parâmetros: receptáculo, índice do slot.</summary>
        public UnityEvent<ReceptacleType, int> OnItemUnequipped;

        private CraftingService _craftingService;

        // Fonte única dos receptáculos. Resolvido na primeira leitura, não no Awake, porque o
        // BuildServiceBinder registra o BuildState no Awake dele e a ordem entre objetos não é garantida.
        private BuildState _buildState;

        private BuildState State
        {
            get
            {
                if (_buildState != null)
                    return _buildState;

                if (GameServiceLocator.Instance != null)
                    _buildState = GameServiceLocator.Instance.Resolve<BuildState>();

                if (_buildState == null)
                {
                    Debug.LogWarning("[ReceptacleController] BuildState não registrado — usando uma build local, " +
                                     "que o PlayerBuildController e a UI não enxergam. Falta um BuildServiceBinder na cena.");
                    _buildState = BuildState.CreateDefault();
                }

                return _buildState;
            }
        }

        private void Awake()
        {
            _craftingService = GameServiceLocator.Instance != null
                ? GameServiceLocator.Instance.Resolve<CraftingService>()
                : new CraftingService();
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
        public ReceptacleData GetReceptacle(ReceptacleType type) => State.GetReceptacle(type);
    }
}
