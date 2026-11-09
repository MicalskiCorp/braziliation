using System;
using Braziliation.Core;
using Braziliation.Settings;
using TMPro;
using UnityEngine;
using UnityEngine.UI;

namespace Braziliation.UI
{
    /// <summary>
    /// Uma linha da tela de controles: nome da ação, binding atual (glifo, ou o texto do binding enquanto
    /// não houver glifo desenhado), botão de trocar e botão de restaurar. Não decide nada: avisa a
    /// <see cref="RebindView"/>, que chama o <see cref="GameInput"/>.
    /// </summary>
    public sealed class RebindRowView : MonoBehaviour
    {
        [Header("Labels")]
        [SerializeField] private TextMeshProUGUI _actionLabel;
        [Tooltip("Texto do binding — só aparece quando não há glifo para ele.")]
        [SerializeField] private TextMeshProUGUI _bindingLabel;
        [SerializeField] private Image _glyphImage;

        [Header("Buttons")]
        [SerializeField] private Button _rebindButton;
        [SerializeField] private Button _resetButton;

        private Action<RebindRowView> _onRebind;
        private Action<RebindRowView> _onReset;

        public GameInput.RebindSlot Slot { get; private set; }

        /// <summary>Primeiro elemento focável da linha, para navegação por controle.</summary>
        public Selectable FirstSelectable => _rebindButton;

        private void Awake()
        {
            if (_rebindButton != null) _rebindButton.onClick.AddListener(() => _onRebind?.Invoke(this));
            if (_resetButton != null)  _resetButton.onClick.AddListener(() => _onReset?.Invoke(this));
        }

        public void Bind(GameInput.RebindSlot slot, Action<RebindRowView> onRebind, Action<RebindRowView> onReset)
        {
            Slot      = slot;
            _onRebind = onRebind;
            _onReset  = onReset;
            if (_actionLabel != null)
                _actionLabel.text = slot.Label;
        }

        /// <summary>Redesenha o binding atual na família de glifo pedida.</summary>
        public void Refresh(ControllerFamily family, ControlGlyphLibrary glyphs)
        {
            string text = GameInput.GetBindingDisplay(Slot.Action, Slot.BindingIndex, out string controlPath);
            bool hasGlyph = glyphs != null && glyphs.TryGet(family, controlPath, out Sprite sprite) && Show(sprite);

            if (_glyphImage != null)
                _glyphImage.enabled = hasGlyph;
            if (_bindingLabel != null)
                _bindingLabel.text = hasGlyph ? string.Empty : text;
        }

        /// <summary>Liga ou desliga os botões, enquanto outra linha espera o jogador apertar algo.</summary>
        public void SetInteractable(bool interactable)
        {
            if (_rebindButton != null) _rebindButton.interactable = interactable;
            if (_resetButton != null)  _resetButton.interactable  = interactable;
        }

        private bool Show(Sprite sprite)
        {
            if (_glyphImage == null)
                return false;

            _glyphImage.sprite = sprite;
            return true;
        }
    }
}
