using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;
using Braziliation.SaveSystem;

namespace Braziliation.UI
{
    /// <summary>
    /// Save Slots panel supporting two modes:
    /// <list type="bullet">
    ///   <item><see cref="Mode.Load"/> — Continue flow: empty slots are disabled.</item>
    ///   <item><see cref="Mode.New"/> — New Game flow: all slots are selectable.</item>
    /// </list>
    /// Reads slot metadata from <see cref="SaveGameService"/> and raises Unity events for
    /// gameplay integration. No scene transitions or game state changes happen here.
    /// </summary>
    public sealed class SaveSlotsView : MonoBehaviour
    {
        public enum Mode { Load, New }

        [Header("Slot Entries")]
        [Tooltip("Assign one SaveSlotEntryView per available save slot (e.g. 3 entries).")]
        [SerializeField] private SaveSlotEntryView[] slotEntries;

        [Header("Buttons")]
        [SerializeField] private Button backButton;

        [Header("Navigation – Steam Input")]
        [Tooltip("First element focused when the Save Slots panel opens.")]
        [SerializeField] private Selectable firstSelected;

        [Header("Game Events")]
        [Tooltip("Raised with the slot index when the player loads an existing save. Wire to the Gameplay Engineer's scene loader.")]
        [SerializeField] private UnityEvent<int> onLoadGame;

        [Tooltip("Raised with the slot index when the player starts a new game. Wire to the Gameplay Engineer's scene loader.")]
        [SerializeField] private UnityEvent<int> onNewGame;

        private SaveGameService _saveGameService;
        private MenuController  _menuController;
        private Mode            _mode;

        private void Awake()
        {
            if (backButton != null) backButton.onClick.AddListener(OnBackClicked);
        }

        /// <summary>Opens the panel in Continue (Load) mode.</summary>
        public void ShowForLoad(SaveGameService saveGameService, MenuController menuController)
        {
            _mode = Mode.Load;
            ShowInternal(saveGameService, menuController);
        }

        /// <summary>Opens the panel in New Game mode.</summary>
        public void ShowForNewGame(SaveGameService saveGameService, MenuController menuController)
        {
            _mode = Mode.New;
            ShowInternal(saveGameService, menuController);
        }

        /// <summary>Hides the Save Slots panel.</summary>
        public void Hide() => gameObject.SetActive(false);

        private void ShowInternal(SaveGameService saveGameService, MenuController menuController)
        {
            _saveGameService = saveGameService;
            _menuController  = menuController;

            RefreshSlots();
            gameObject.SetActive(true);
            MenuController.FocusForNavigation(firstSelected);
        }

        private void RefreshSlots()
        {
            for (int i = 0; i < slotEntries.Length; i++)
                slotEntries[i].Bind(i, _saveGameService.Load(i), _mode, OnSlotSelected);
        }

        private void OnSlotSelected(int slotIndex)
        {
            if (_mode == Mode.Load)
                onLoadGame.Invoke(slotIndex);
            else
                onNewGame.Invoke(slotIndex);
        }

        private void OnBackClicked() => _menuController.ShowMainMenu();
    }
}
