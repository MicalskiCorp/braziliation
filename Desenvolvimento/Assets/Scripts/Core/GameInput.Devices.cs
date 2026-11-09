using System;
using Braziliation.Settings;
using UnityEngine.InputSystem;

namespace Braziliation.Core
{
    /// <summary>
    /// Família do dispositivo ativo e glifo a mostrar (ADR-017). O dispositivo vem do controle que
    /// disparou a última ação — de qualquer action map, inclusive o de UI —, não de polling de
    /// <c>Keyboard.current</c>/<c>Gamepad.current</c>. A regra de qual glifo mostrar é do core
    /// (<see cref="GlyphRules"/>); aqui só se detecta e se avisa a troca.
    /// </summary>
    public static partial class GameInput
    {
        private static ControllerFamily _activeFamily = ControllerFamily.KeyboardMouse;
        private static GlyphStyle _glyphStyle = GlyphStyle.Auto;
        private static bool _trackingDevices;

        /// <summary>Disparado quando a família de glifo a mostrar muda (dispositivo trocado ou preferência).</summary>
        public static event Action<ControllerFamily> GlyphFamilyChanged;

        /// <summary>Família do último dispositivo usado. Teclado/mouse até o primeiro input.</summary>
        public static ControllerFamily ActiveDeviceFamily
        {
            get
            {
                StartDeviceTracking();
                return _activeFamily;
            }
        }

        /// <summary>Preferência do jogador (<c>GameSettings.GlyphStyle</c>). Quem muda nas opções também grava.</summary>
        public static GlyphStyle GlyphStyle
        {
            get => _glyphStyle;
            set
            {
                if (_glyphStyle == value)
                    return;

                var before = GlyphFamily;
                _glyphStyle = value;
                NotifyIfGlyphChanged(before);
            }
        }

        /// <summary>Família de glifo que a UI deve desenhar agora.</summary>
        public static ControllerFamily GlyphFamily => GlyphRules.Resolve(ActiveDeviceFamily, _glyphStyle);

        /// <summary>
        /// Configuração do boot, antes da primeira leitura: overrides de binding e preferência de glifo do
        /// <c>GameSettings</c>, e começa a seguir o dispositivo ativo. Chamado pelo <c>GameServiceLocator</c>.
        /// </summary>
        public static void Configure(string bindingOverrides, GlyphStyle glyphStyle)
        {
            ApplyBindingOverrides(bindingOverrides);
            _glyphStyle = glyphStyle;
            StartDeviceTracking();
        }

        /// <summary>Classifica um dispositivo pela layout, sem tipos de plataforma (compila em qualquer alvo).</summary>
        public static ControllerFamily Classify(InputDevice device)
        {
            if (device is Gamepad)
            {
                if (InputSystem.IsFirstLayoutBasedOnSecond(device.layout, "DualShockGamepad"))
                    return ControllerFamily.PlayStation;
                if (InputSystem.IsFirstLayoutBasedOnSecond(device.layout, "SwitchProControllerHID"))
                    return ControllerFamily.Switch;
                return ControllerFamily.Xbox;
            }

            return ControllerFamily.KeyboardMouse;
        }

        private static void StartDeviceTracking()
        {
            if (_trackingDevices)
                return;

            _trackingDevices = true;
            InputSystem.onActionChange += OnActionChange;
        }

        private static void OnActionChange(object target, InputActionChange change)
        {
            if (change != InputActionChange.ActionPerformed)
                return;

            var device = (target as InputAction)?.activeControl?.device;
            if (device == null)
                return;

            var family = Classify(device);
            if (family == _activeFamily)
                return;

            var before = GlyphFamily;
            _activeFamily = family;
            NotifyIfGlyphChanged(before);
        }

        private static void NotifyIfGlyphChanged(ControllerFamily before)
        {
            var now = GlyphFamily;
            if (now != before)
                GlyphFamilyChanged?.Invoke(now);
        }

        private static void ResetDevices()
        {
            if (_trackingDevices)
                InputSystem.onActionChange -= OnActionChange;

            _trackingDevices = false;
            _activeFamily = ControllerFamily.KeyboardMouse;
            _glyphStyle = GlyphStyle.Auto;
            GlyphFamilyChanged = null;
        }
    }
}
