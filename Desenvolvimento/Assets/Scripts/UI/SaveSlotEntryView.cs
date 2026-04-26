using System;
using UnityEngine;
using UnityEngine.UI;
using Braziliation.SaveSystem;

namespace Braziliation.UI
{
    /// <summary>
    /// Displays metadata for a single save slot: player name, formatted playtime, and last-saved date.
    /// Calls the selection callback when the slot button is clicked.
    /// Disables the button in <see cref="SaveSlotsView.Mode.Load"/> mode when the slot is empty.
    /// </summary>
    public sealed class SaveSlotEntryView : MonoBehaviour
    {
        [Header("Labels")]
        [SerializeField] private Text playerNameLabel;
        [SerializeField] private Text playtimeLabel;
        [SerializeField] private Text lastSavedLabel;

        [Header("State Indicators")]
        [SerializeField] private GameObject emptySlotIndicator;
        [SerializeField] private GameObject filledSlotIndicator;

        [Header("Action")]
        [SerializeField] private Button selectButton;

        private int            _slotIndex;
        private Action<int>    _onSelected;

        private void Awake()
        {
            if (selectButton != null) selectButton.onClick.AddListener(OnSelectClicked);
        }

        /// <summary>
        /// Binds this entry to a save slot.
        /// Pass <c>null</c> for <paramref name="slot"/> to render the empty-slot state.
        /// </summary>
        /// <param name="slotIndex">Slot index forwarded to the selection callback.</param>
        /// <param name="slot">Loaded <see cref="SaveSlot"/>, or <c>null</c> if the slot is unused.</param>
        /// <param name="mode">Controls whether empty slots can be selected.</param>
        /// <param name="onSelected">Callback raised with <paramref name="slotIndex"/> on click.</param>
        public void Bind(int slotIndex, SaveSlot slot, SaveSlotsView.Mode mode, Action<int> onSelected)
        {
            _slotIndex  = slotIndex;
            _onSelected = onSelected;

            bool hasData = slot != null;
            emptySlotIndicator.SetActive(!hasData);
            filledSlotIndicator.SetActive(hasData);

            if (hasData)
            {
                playerNameLabel.text = slot.PlayerName;
                playtimeLabel.text   = FormatPlaytime(slot.PlaytimeSeconds);
                lastSavedLabel.text  = slot.LastSaved.LocalDateTime.ToString("dd/MM/yyyy HH:mm");
            }
            else
            {
                playerNameLabel.text = string.Empty;
                playtimeLabel.text   = string.Empty;
                lastSavedLabel.text  = string.Empty;
            }

            // Empty slots are not selectable in Load mode.
            selectButton.interactable = mode == SaveSlotsView.Mode.New || hasData;
        }

        private void OnSelectClicked() => _onSelected?.Invoke(_slotIndex);

        private static string FormatPlaytime(double totalSeconds)
        {
            var span = TimeSpan.FromSeconds(totalSeconds);
            return $"{(int)span.TotalHours:D2}:{span.Minutes:D2}:{span.Seconds:D2}";
        }
    }
}
