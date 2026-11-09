using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;
using Braziliation.SaveSystem;

namespace Braziliation.UI
{
    /// <summary>
    /// Save Slots panel supporting two modes:
    /// <list type="bullet">
    ///   <item><see cref="Mode.Load"/> — Continue flow: only usable slots (<see cref="SaveLoadResult.IsUsable"/>) are selectable.</item>
    ///   <item><see cref="Mode.New"/> — New Game flow: only overwritable slots (<see cref="SaveLoadResult.CanOverwrite"/>) are selectable.</item>
    /// </list>
    /// Loads each slot with <see cref="SaveGameService.LoadDetailed"/> so a corrupt save or one from a
    /// newer build is never shown as empty (ADR-007; contract in Sistemas/UI.md › Estado do slot).
    /// Raises Unity events for gameplay integration. No scene transitions or game state changes happen here.
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
            {
                SaveLoadResult result = _saveGameService.LoadDetailed(i);
                LogBlockedStatus(i, result);
                slotEntries[i].Bind(i, result, _mode, OnSlotSelected);
            }
        }

        // O jogador vê só o aviso do slot; o log guarda o que ajuda a diagnosticar.
        private static void LogBlockedStatus(int slotIndex, SaveLoadResult result)
        {
            switch (result.Status)
            {
                case SaveLoadStatus.Corrupt:
                    Debug.LogWarning($"[SaveSlotsView] Slot {slotIndex}: save corrompido (versão lida {result.FoundVersion}).");
                    break;
                case SaveLoadStatus.FromNewerBuild:
                    Debug.LogWarning($"[SaveSlotsView] Slot {slotIndex}: save de build mais nova (versão {result.FoundVersion}, esta lê até {SaveSlot.CurrentSchemaVersion}). Bloqueado, nunca sobrescrito.");
                    break;
                case SaveLoadStatus.NoMigrationPath:
                    Debug.LogError($"[SaveSlotsView] Slot {slotIndex}: versão {result.FoundVersion} sem degrau de migração até {SaveSlot.CurrentSchemaVersion}. Falta registrar um ISaveMigration.");
                    break;
            }
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
