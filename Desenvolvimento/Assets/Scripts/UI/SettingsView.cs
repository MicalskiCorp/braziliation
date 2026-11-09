using UnityEngine;
using UnityEngine.UI;
using Braziliation.Settings;

namespace Braziliation.UI
{
    /// <summary>
    /// Options panel: exposes Master, Music, and SFX volume sliders.
    /// Populates slider values from <see cref="SettingsService"/> on <see cref="Show"/>;
    /// persists settings on Apply. All clamping is handled by <see cref="GameSettings"/>.
    /// No business logic — this is a pure view.
    /// </summary>
    public sealed class SettingsView : MonoBehaviour
    {
        [Header("Sliders")]
        [SerializeField] private Slider masterVolumeSlider;
        [SerializeField] private Slider musicVolumeSlider;
        [SerializeField] private Slider sfxVolumeSlider;

        [Header("Buttons")]
        [SerializeField] private Button applyButton;
        [SerializeField] private Button backButton;

        [Header("Navigation – Steam Input")]
        [Tooltip("First element focused when the Options panel opens.")]
        [SerializeField] private Selectable firstSelected;

        private SettingsService _settingsService;
        private MenuController _menuController;

        private void Awake()
        {
            if (applyButton != null) applyButton.onClick.AddListener(OnApplyClicked);
            if (backButton  != null) backButton.onClick.AddListener(OnBackClicked);
        }

        /// <summary>
        /// Opens the Options panel, loads current settings, and sets navigation focus.
        /// </summary>
        public void Show(SettingsService settingsService, MenuController menuController)
        {
            _settingsService = settingsService;
            _menuController  = menuController;

            var settings = _settingsService.Load();
            masterVolumeSlider.SetValueWithoutNotify(settings.MasterVolume);
            musicVolumeSlider.SetValueWithoutNotify(settings.MusicVolume);
            sfxVolumeSlider.SetValueWithoutNotify(settings.SfxVolume);

            gameObject.SetActive(true);
            MenuController.FocusForNavigation(firstSelected);
        }

        /// <summary>Hides the Options panel without saving.</summary>
        public void Hide() => gameObject.SetActive(false);

        private void OnApplyClicked()
        {
            // Relê e muda só o áudio: um GameSettings novo apagaria os controles (overrides e glifo).
            var settings = _settingsService.Load();
            settings.MasterVolume = masterVolumeSlider.value;
            settings.MusicVolume  = musicVolumeSlider.value;
            settings.SfxVolume    = sfxVolumeSlider.value;
            _settingsService.Save(settings);
        }

        private void OnBackClicked() => _menuController.ShowMainMenu();
    }
}
