using System;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using Braziliation.SaveSystem;

namespace Braziliation.UI
{
    /// <summary>
    /// Displays a single save slot by its <see cref="SaveLoadStatus"/>: player name, formatted playtime
    /// and last-saved date when the save is usable; an "unavailable" state with an explanation when it is
    /// corrupt, from a newer build or without a migration path. Whether the button is selectable comes
    /// from the core rule (<see cref="SaveLoadResult.IsUsable"/> for Continue,
    /// <see cref="SaveLoadResult.CanOverwrite"/> for New Game) — contract in Sistemas/UI.md › Estado do slot.
    /// </summary>
    public sealed class SaveSlotEntryView : MonoBehaviour
    {
        [Header("Labels")]
        [SerializeField] private TextMeshProUGUI playerNameLabel;
        [SerializeField] private TextMeshProUGUI playtimeLabel;
        [SerializeField] private TextMeshProUGUI lastSavedLabel;
        [Tooltip("Explains why the slot cannot be used (corrupt, newer build, no migration path).")]
        [SerializeField] private TextMeshProUGUI statusLabel;

        [Header("State Indicators")]
        [SerializeField] private GameObject emptySlotIndicator;
        [SerializeField] private GameObject filledSlotIndicator;
        [Tooltip("Shown for Corrupt, FromNewerBuild and NoMigrationPath.")]
        [SerializeField] private GameObject unavailableSlotIndicator;

        [Header("Status Texts (PT-BR until localization)")]
        [SerializeField, TextArea] private string corruptText = "Save danificado.";
        [SerializeField, TextArea] private string fromNewerBuildText = "Salvo numa versão mais nova do jogo. Atualize para continuar.";
        [SerializeField, TextArea] private string noMigrationPathText = "Save de uma versão antiga que esta versão não converte.";

        [Header("Action")]
        [SerializeField] private Button selectButton;

        private int            _slotIndex;
        private Action<int>    _onSelected;

        private void Awake()
        {
            if (selectButton != null) selectButton.onClick.AddListener(OnSelectClicked);
        }

        /// <summary>Binds this entry to the outcome of loading a save slot.</summary>
        /// <param name="slotIndex">Slot index forwarded to the selection callback.</param>
        /// <param name="result">Result of <see cref="SaveGameService.LoadDetailed"/> for this slot.</param>
        /// <param name="mode">Continue reads <see cref="SaveLoadResult.IsUsable"/>; New Game reads <see cref="SaveLoadResult.CanOverwrite"/>.</param>
        /// <param name="onSelected">Callback raised with <paramref name="slotIndex"/> on click.</param>
        public void Bind(int slotIndex, SaveLoadResult result, SaveSlotsView.Mode mode, Action<int> onSelected)
        {
            _slotIndex  = slotIndex;
            _onSelected = onSelected;

            SaveSlot slot     = result.IsUsable ? result.Slot : null;
            bool hasData      = slot != null;
            bool isEmpty      = result.Status == SaveLoadStatus.Empty;
            bool isUnavailable = !hasData && !isEmpty;

            SetActive(emptySlotIndicator, isEmpty);
            SetActive(filledSlotIndicator, hasData);
            SetActive(unavailableSlotIndicator, isUnavailable);

            playerNameLabel.text = hasData ? slot.PlayerName : string.Empty;
            playtimeLabel.text   = hasData ? FormatPlaytime(slot.PlaytimeSeconds) : string.Empty;
            lastSavedLabel.text  = hasData ? slot.LastSaved.LocalDateTime.ToString("dd/MM/yyyy HH:mm") : string.Empty;
            if (statusLabel != null)
                statusLabel.text = StatusText(result.Status);

            selectButton.interactable = mode == SaveSlotsView.Mode.Load ? result.IsUsable : result.CanOverwrite;
        }

        private string StatusText(SaveLoadStatus status)
        {
            switch (status)
            {
                case SaveLoadStatus.Corrupt:         return corruptText;
                case SaveLoadStatus.FromNewerBuild:  return fromNewerBuildText;
                case SaveLoadStatus.NoMigrationPath: return noMigrationPathText;
                default:                             return string.Empty;
            }
        }

        private static void SetActive(GameObject target, bool active)
        {
            if (target != null) target.SetActive(active);
        }

        private void OnSelectClicked() => _onSelected?.Invoke(_slotIndex);

        private static string FormatPlaytime(double totalSeconds)
        {
            var span = TimeSpan.FromSeconds(totalSeconds);
            return $"{(int)span.TotalHours:D2}:{span.Minutes:D2}:{span.Seconds:D2}";
        }
    }
}
