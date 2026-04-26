using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using Braziliation.Core;

namespace Braziliation.UI
{
    /// <summary>
    /// Root controller for the Main Menu scene.
    /// Owns panel visibility and routes button clicks to the correct view.
    /// Contains no business logic — all data operations are delegated to services via views.
    /// </summary>
    public sealed class MenuController : MonoBehaviour
    {
        [Header("Panels")]
        [SerializeField] private GameObject mainMenuPanel;

        [Header("Main Menu Buttons")]
        [SerializeField] private Button newGameButton;
        [SerializeField] private Button continueButton;
        [SerializeField] private Button optionsButton;
        [SerializeField] private Button exitButton;

        [Header("Views")]
        [SerializeField] private SettingsView settingsView;
        [SerializeField] private SaveSlotsView saveSlotsView;

        [Header("Navigation – Steam Input")]
        [Tooltip("First button focused when the Main Menu panel is shown.")]
        [SerializeField] private Selectable firstSelected;

        private Braziliation.SaveSystem.SaveGameService _saveGameService;
        private Braziliation.Settings.SettingsService _settingsService;

        private void Awake()
        {
            var locator = GameServiceLocator.Instance;
            if (locator == null)
            {
                Debug.LogError("[MenuController] GameServiceLocator not found. Add it to the scene before MenuController.");
                return;
            }

            _saveGameService = locator.SaveGameService;
            _settingsService = locator.SettingsService;
        }

        private void Start()
        {
            newGameButton.onClick.AddListener(OnNewGameClicked);
            continueButton.onClick.AddListener(OnContinueClicked);
            optionsButton.onClick.AddListener(OnOptionsClicked);
            exitButton.onClick.AddListener(OnExitClicked);

            ShowMainMenu();
        }

        /// <summary>
        /// Returns to the Main Menu panel, hiding all other views.
        /// Called by child views (SettingsView, SaveSlotsView) when Back is pressed.
        /// </summary>
        public void ShowMainMenu()
        {
            mainMenuPanel.SetActive(true);
            settingsView.Hide();
            saveSlotsView.Hide();
            FocusForNavigation(firstSelected);
        }

        private void OnNewGameClicked() =>
            saveSlotsView.ShowForNewGame(_saveGameService, this);

        private void OnContinueClicked() =>
            saveSlotsView.ShowForLoad(_saveGameService, this);

        private void OnOptionsClicked() =>
            settingsView.Show(_settingsService, this);

        private void OnExitClicked() => Application.Quit();

        /// <summary>
        /// Sets the EventSystem focus to <paramref name="target"/> for controller/keyboard navigation.
        /// Call this whenever a panel becomes active. Compatible with future Steam Input.
        /// </summary>
        internal static void FocusForNavigation(Selectable target)
        {
            if (target == null) return;
            EventSystem.current?.SetSelectedGameObject(target.gameObject);
        }
    }
}
