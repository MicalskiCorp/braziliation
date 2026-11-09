using System.Collections.Generic;
using Braziliation.Core;
using Braziliation.Settings;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

namespace Braziliation.UI
{
    /// <summary>
    /// Tela de controles (ADR-017): lista os bindings do map Player para o dispositivo em uso (teclado e
    /// mouse, ou controle), troca e restaura cada um, e restaura tudo. Só chama o <see cref="GameInput"/>;
    /// quem grava os overrides no <c>GameSettings</c> é o <c>GameServiceLocator</c>. Navegável por controle:
    /// o foco vai para a primeira linha ao abrir.
    /// </summary>
    public sealed class RebindView : MonoBehaviour
    {
        [Header("Rows")]
        [Tooltip("Pai das linhas, com um LayoutGroup.")]
        [SerializeField] private Transform _rowContainer;
        [SerializeField] private RebindRowView _rowPrefab;
        [SerializeField] private ControlGlyphLibrary _glyphs;

        [Header("Buttons")]
        [SerializeField] private Button _resetAllButton;
        [SerializeField] private Button _backButton;

        [Header("Status")]
        [SerializeField] private TextMeshProUGUI _statusLabel;
        [SerializeField, TextArea] private string _waitingText  = "Aperte a nova tecla ou botão. Esc cancela.";
        [SerializeField, TextArea] private string _canceledText = "Troca cancelada.";
        [SerializeField, TextArea] private string _doneText     = "Controle trocado.";
        [Tooltip("{0} é o nome da outra ação.")]
        [SerializeField, TextArea] private string _conflictText = "Atenção: essa tecla também está em {0}.";

        private readonly List<RebindRowView> _rows = new List<RebindRowView>();
        private bool _showingGamepad;
        private MenuController _menuController;

        private void Awake()
        {
            if (_resetAllButton != null) _resetAllButton.onClick.AddListener(OnResetAllClicked);
            if (_backButton != null)     _backButton.onClick.AddListener(OnBackClicked);
        }

        private void OnEnable()  => GameInput.GlyphFamilyChanged += OnGlyphFamilyChanged;

        private void OnDisable()
        {
            GameInput.GlyphFamilyChanged -= OnGlyphFamilyChanged;
            GameInput.CancelRebind();
        }

        /// <summary>Abre a tela. <paramref name="menuController"/> é opcional (para o Voltar).</summary>
        public void Show(MenuController menuController = null)
        {
            _menuController = menuController;
            gameObject.SetActive(true);
            SetStatus(string.Empty);
            BuildRows(GameInput.GlyphFamily != ControllerFamily.KeyboardMouse);
        }

        public void Hide() => gameObject.SetActive(false);

        private void BuildRows(bool gamepad)
        {
            _showingGamepad = gamepad;
            foreach (var row in _rows)
                Destroy(row.gameObject);
            _rows.Clear();

            if (_rowPrefab == null || _rowContainer == null)
            {
                Debug.LogWarning("[RebindView] Prefab de linha ou container não vinculado.");
                return;
            }

            foreach (var slot in GameInput.GetRebindSlots(gamepad))
            {
                var row = Instantiate(_rowPrefab, _rowContainer);
                row.Bind(slot, OnRebindRequested, OnResetRequested);
                _rows.Add(row);
            }

            RefreshRows();
            if (_rows.Count > 0)
                MenuController.FocusForNavigation(_rows[0].FirstSelectable);
        }

        private void RefreshRows()
        {
            var family = GameInput.GlyphFamily;
            foreach (var row in _rows)
                row.Refresh(family, _glyphs);
        }

        private void OnRebindRequested(RebindRowView row)
        {
            if (!GameInput.StartRebind(row.Slot.Action, row.Slot.BindingIndex, result => OnRebindFinished(row, result)))
                return;

            SetRowsInteractable(false);
            SetStatus(_waitingText);
        }

        private void OnRebindFinished(RebindRowView row, GameInput.RebindResult result)
        {
            SetRowsInteractable(true);
            RefreshRows();

            if (!result.Completed)
                SetStatus(_canceledText);
            else if (!string.IsNullOrEmpty(result.ConflictWith))
                SetStatus(string.Format(_conflictText, result.ConflictWith));
            else
                SetStatus(_doneText);

            MenuController.FocusForNavigation(row.FirstSelectable);
        }

        private void OnResetRequested(RebindRowView row)
        {
            GameInput.ResetBinding(row.Slot.Action, row.Slot.BindingIndex);
            RefreshRows();
        }

        private void OnResetAllClicked()
        {
            GameInput.ResetAllBindings();
            RefreshRows();
        }

        private void OnGlyphFamilyChanged(ControllerFamily family)
        {
            bool gamepad = family != ControllerFamily.KeyboardMouse;
            if (GameInput.IsRebinding)
                return;

            if (gamepad != _showingGamepad)
                BuildRows(gamepad);
            else
                RefreshRows();
        }

        private void OnBackClicked()
        {
            if (_menuController != null)
                _menuController.ShowMainMenu();
            else
                Hide();
        }

        private void SetRowsInteractable(bool interactable)
        {
            foreach (var row in _rows)
                row.SetInteractable(interactable);
        }

        private void SetStatus(string text)
        {
            if (_statusLabel != null)
                _statusLabel.text = text;
        }
    }
}
