using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using Braziliation.Crafting;
using Braziliation.Core;

namespace Braziliation.UI
{
    /// <summary>
    /// Controla o painel de crafting da interface do jogador.
    /// Exibe os três receptáculos com seus slots e itens equipados.
    /// Responde a eventos do ReceptacleController para manter a view sincronizada.
    ///
    /// Contém zero lógica de negócio — toda operação é delegada ao ReceptacleController.
    /// TODO: criar Prefab do painel e vincular no Inspector
    /// </summary>
    public sealed class CraftingPanelController : MonoBehaviour
    {
        [Header("Painel")]
        [Tooltip("Objeto raiz do painel de crafting — ativado/desativado em ShowPanel/HidePanel.")]
        [SerializeField] private GameObject _painelRaiz;

        [Header("Referências")]
        [Tooltip("ReceptacleController da cena — fonte dos dados dos receptáculos.")]
        [SerializeField] private ReceptacleController _receptacleController;

        [Header("Slots de UI — Exoesqueleto")]
        [Tooltip("Botões de slot do receptáculo Exoesqueleto, na ordem dos índices.")]
        [SerializeField] private List<Button> _slotsExoesqueleto;

        [Header("Slots de UI — Capa")]
        [Tooltip("Botões de slot do receptáculo Capa, na ordem dos índices.")]
        [SerializeField] private List<Button> _slotsCapa;

        [Header("Slots de UI — Espinha")]
        [Tooltip("Botões de slot do receptáculo Espinha, na ordem dos índices.")]
        [SerializeField] private List<Button> _slotsEspinha;

        [Header("Navegação — Steam Input")]
        [Tooltip("Primeiro elemento selecionado ao abrir o painel (navegação por controle/teclado).")]
        [SerializeField] private Selectable _primeiroSelecionado;

        private void Awake()
        {
            // Vincula callbacks dos botões de slot a OnSlotClicked
            VincularSlots(_slotsExoesqueleto, ReceptacleType.Exoskeleton);
            VincularSlots(_slotsCapa, ReceptacleType.Cape);
            VincularSlots(_slotsEspinha, ReceptacleType.Spine);
        }

        private void OnEnable()
        {
            if (_receptacleController == null) return;

            // Subscreve nos eventos do ReceptacleController para auto-refresh da view
            _receptacleController.OnItemEquipped.AddListener(OnItemEquipado);
            _receptacleController.OnItemUnequipped.AddListener(OnItemDesequipado);
        }

        private void OnDisable()
        {
            if (_receptacleController == null) return;

            _receptacleController.OnItemEquipped.RemoveListener(OnItemEquipado);
            _receptacleController.OnItemUnequipped.RemoveListener(OnItemDesequipado);
        }

        // ── Visibilidade ────────────────────────────────────────────────────────

        /// <summary>Exibe o painel de crafting e define o foco inicial para navegação por controle.</summary>
        public void ShowPanel()
        {
            if (_painelRaiz != null)
                _painelRaiz.SetActive(true);

            // Garante navegação por controle/teclado ao abrir o painel
            if (_primeiroSelecionado != null)
                EventSystem.current.SetSelectedGameObject(_primeiroSelecionado.gameObject);

            RefreshAll();
        }

        /// <summary>Esconde o painel de crafting.</summary>
        public void HidePanel()
        {
            if (_painelRaiz != null)
                _painelRaiz.SetActive(false);
        }

        // ── Atualização de view ─────────────────────────────────────────────────

        /// <summary>
        /// Atualiza a visualização de todos os slots com base nos dados dos receptáculos informados.
        /// </summary>
        /// <param name="receptacles">Array com os dados dos três receptáculos.</param>
        public void RefreshView(ReceptacleData[] receptacles)
        {
            if (receptacles == null) return;

            foreach (var data in receptacles)
            {
                var botoes = ObterBotoesDoReceptaculo(data.Type);
                AtualizarSlotsDaUI(botoes, data);
            }
        }

        /// <summary>Callback de clique em um slot do painel.</summary>
        /// <param name="receptacle">Receptáculo ao qual o slot pertence.</param>
        /// <param name="slotIndex">Índice do slot clicado.</param>
        public void OnSlotClicked(ReceptacleType receptacle, int slotIndex)
        {
            Debug.Log($"[CraftingPanelController] Slot clicado — receptáculo: {receptacle}, índice: {slotIndex}");
            // Delegar operação de equip/unequip ao ReceptacleController conforme fluxo de UX
        }

        // ── Handlers internos ───────────────────────────────────────────────────

        private void OnItemEquipado(ReceptacleType receptacle, int slotIndex, ItemComponent item)
        {
            RefreshReceptaculo(receptacle);
        }

        private void OnItemDesequipado(ReceptacleType receptacle, int slotIndex)
        {
            RefreshReceptaculo(receptacle);
        }

        // ── Helpers ─────────────────────────────────────────────────────────────

        private void RefreshAll()
        {
            if (_receptacleController == null) return;

            AtualizarReceptaculoNaUI(ReceptacleType.Exoskeleton, _slotsExoesqueleto);
            AtualizarReceptaculoNaUI(ReceptacleType.Cape, _slotsCapa);
            AtualizarReceptaculoNaUI(ReceptacleType.Spine, _slotsEspinha);
        }

        private void RefreshReceptaculo(ReceptacleType tipo)
        {
            if (_receptacleController == null) return;

            var data = _receptacleController.GetReceptacle(tipo);
            if (data == null) return;

            var botoes = ObterBotoesDoReceptaculo(tipo);
            AtualizarSlotsDaUI(botoes, data);
        }

        private void AtualizarReceptaculoNaUI(ReceptacleType tipo, List<Button> botoes)
        {
            var data = _receptacleController.GetReceptacle(tipo);
            if (data == null) return;
            AtualizarSlotsDaUI(botoes, data);
        }

        private static void AtualizarSlotsDaUI(List<Button> botoes, ReceptacleData data)
        {
            for (int i = 0; i < botoes.Count; i++)
            {
                if (botoes[i] == null) continue;
                bool temItem = i < data.Slots.Count && !data.Slots[i].IsEmpty;
                // Feedback visual mínimo — arte completa a ser integrada no pipeline de arte
                botoes[i].interactable = true;
                var texto = botoes[i].GetComponentInChildren<UnityEngine.UI.Text>();
                if (texto != null)
                    texto.text = temItem ? data.Slots[i].EquippedItem.Id : "—";
            }
        }

        private List<Button> ObterBotoesDoReceptaculo(ReceptacleType tipo)
        {
            return tipo switch
            {
                ReceptacleType.Exoskeleton => _slotsExoesqueleto,
                ReceptacleType.Cape        => _slotsCapa,
                ReceptacleType.Spine       => _slotsEspinha,
                _                          => new List<Button>()
            };
        }

        private void VincularSlots(List<Button> botoes, ReceptacleType tipo)
        {
            for (int i = 0; i < botoes.Count; i++)
            {
                if (botoes[i] == null) continue;
                int indice = i; // captura por valor para o lambda
                botoes[i].onClick.AddListener(() => OnSlotClicked(tipo, indice));
            }
        }
    }
}
