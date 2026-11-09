using System;
using System.Collections.Generic;
using Braziliation.Settings;
using UnityEngine;

namespace Braziliation.UI
{
    /// <summary>
    /// Sprites de glifo de controle por família (ADR-017): o seletor de glifo. Cada entrada liga uma
    /// família e um caminho de controle (o <c>controlPath</c> do <c>GetBindingDisplayString</c>, ex.:
    /// "buttonSouth", "space", "leftStick/up") a um sprite nosso. Os sprites são da pendência de glifos
    /// do <c>@SpriteArtist</c>; sem entrada, a UI cai no texto do binding.
    /// </summary>
    [CreateAssetMenu(menuName = "Braziliation/UI/Control Glyph Library", fileName = "ControlGlyphLibrary")]
    public sealed class ControlGlyphLibrary : ScriptableObject
    {
        [Serializable]
        private struct Entry
        {
            [SerializeField] private ControllerFamily _family;
            [Tooltip("Caminho do controle sem o dispositivo, ex.: buttonSouth, space, leftStick/up.")]
            [SerializeField] private string _controlPath;
            [SerializeField] private Sprite _sprite;

            public ControllerFamily Family => _family;
            public string ControlPath => _controlPath;
            public Sprite Sprite => _sprite;
        }

        [SerializeField] private List<Entry> _entries = new List<Entry>();

        /// <summary>Sprite do controle para a família, ou false quando ainda não há glifo desenhado.</summary>
        public bool TryGet(ControllerFamily family, string controlPath, out Sprite sprite)
        {
            sprite = null;
            if (string.IsNullOrEmpty(controlPath))
                return false;

            foreach (var entry in _entries)
            {
                if (entry.Family == family && entry.Sprite != null &&
                    string.Equals(entry.ControlPath, controlPath, StringComparison.OrdinalIgnoreCase))
                {
                    sprite = entry.Sprite;
                    return true;
                }
            }

            return false;
        }
    }
}
