using UnityEngine;
using UnityEngine.Events;
using Braziliation.Crafting;
using Braziliation.Core;

namespace Braziliation.Build
{
    /// <summary>
    /// Tipo de NPC responsável pela expansão de slots de um receptáculo específico.
    /// Cada NPC expande apenas o receptáculo correspondente ao seu pilar (conforme Build.md).
    /// </summary>
    public enum NPCType
    {
        /// <summary>Artesão de Blumenau — expande o Exoesqueleto dos Trilhos (pilar Mecânico).</summary>
        Craftsman,

        /// <summary>Costureira ritualística / Bruxa da Ilha da Magia — expande a Capa das Lendas do Mar (pilar Místico).</summary>
        Seamstress,

        /// <summary>Alquimista biológico / Pesquisador da mata — expande a Espinha de Fungo (pilar Biológico).</summary>
        Alchemist
    }

    /// <summary>
    /// Gerencia a expansão de slots via entrega de materiais especiais a NPCs.
    ///
    /// Conforme Build.md — Expansão de Slots:
    ///   O jogador encontra materiais especiais no mapa e os entrega ao NPC correto
    ///   para desbloquear novos slots no receptáculo correspondente.
    /// </summary>
    public sealed class SlotExpansionHandler : MonoBehaviour
    {
        [Header("Configuração do NPC")]
        [SerializeField] private NPCType _tipoNPC;

        // TODO-DESIGN: ID do material especial exigido por este NPC
        //   Artesão      → ex: "metal_plate_old"   (Placas metálicas antigas — Build.md)
        //   Costureira   → ex: "spool_old"          (Carretéis antigos — Build.md)
        //   Alquimista   → ex: "crystal_fungus"     (Fungos cristalizados — Build.md)
        [SerializeField] private string _idMaterialEspecial = ""; // TODO-DESIGN

        [Header("Referências")]
        [SerializeField] private ReceptacleController _receptacleController;

        [Header("Eventos")]
        /// <summary>Disparado ao expandir um slot com sucesso. Parâmetro: receptáculo expandido.</summary>
        public UnityEvent<ReceptacleType> OnSlotExpanded;

        /// <summary>
        /// Verifica se o inventário contém o material especial exigido, remove-o
        /// e adiciona um novo slot ao receptáculo correspondente a este NPC.
        ///
        /// Cada NPC expande apenas o receptáculo do seu pilar — o parâmetro receptacle
        /// deve corresponder ao mapeamento deste NPCType.
        /// </summary>
        /// <param name="receptacle">Receptáculo alvo (deve ser o receptáculo deste NPC).</param>
        /// <param name="inventory">Inventário do jogador a ser verificado e consumido.</param>
        public void ExpandSlot(ReceptacleType receptacle, PlayerInventory inventory)
        {
            var receptaculoDoNPC = ObterReceptaculoDoNPC(_tipoNPC);

            if (receptacle != receptaculoDoNPC)
            {
                Debug.LogWarning(
                    $"[SlotExpansionHandler] NPC '{_tipoNPC}' não expande o receptáculo '{receptacle}'. " +
                    $"Este NPC expande apenas '{receptaculoDoNPC}'.");
                return;
            }

            if (string.IsNullOrEmpty(_idMaterialEspecial))
            {
                Debug.LogWarning("[SlotExpansionHandler] ID do material especial não configurado. TODO-DESIGN.");
                return;
            }

            if (!inventory.HasItem(_idMaterialEspecial))
            {
                Debug.Log($"[SlotExpansionHandler] Jogador não possui o material '{_idMaterialEspecial}'.");
                return;
            }

            // Consome o material especial do inventário
            inventory.RemoveItem(_idMaterialEspecial);

            // Adiciona novo slot ao receptáculo
            var data = _receptacleController.GetReceptacle(receptacle);
            if (data == null)
            {
                Debug.LogWarning($"[SlotExpansionHandler] Receptáculo '{receptacle}' não encontrado no controller.");
                return;
            }

            data.Slots.Add(new SlotData
            {
                AcceptedType  = data.Pillar,
                EquippedItem  = null
            });

            data.ExpansionLevel++;
            OnSlotExpanded?.Invoke(receptacle);
        }

        /// <summary>
        /// Mapeia o tipo de NPC para o receptáculo que ele expande.
        /// Conforme Build.md — tabela de Expansão de Slots.
        /// </summary>
        private static ReceptacleType ObterReceptaculoDoNPC(NPCType npc)
        {
            return npc switch
            {
                NPCType.Craftsman  => ReceptacleType.Exoskeleton,
                NPCType.Seamstress => ReceptacleType.Cape,
                NPCType.Alchemist  => ReceptacleType.Spine,
                _                  => ReceptacleType.Exoskeleton
            };
        }
    }
}
