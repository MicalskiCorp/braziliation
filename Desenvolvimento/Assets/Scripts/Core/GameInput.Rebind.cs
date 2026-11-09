using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.InputSystem;

namespace Braziliation.Core
{
    /// <summary>
    /// Rebind de controles no jogo (ADR-017): overrides do action map, rebind interativo e restaurar
    /// padrão. Os overrides são um JSON opaco (<c>SaveBindingOverridesAsJson</c>) que o
    /// <c>GameServiceLocator</c> carrega do <c>GameSettings</c> no boot e grava a cada
    /// <see cref="BindingOverridesChanged"/>. A UI (<c>RebindView</c>) só chama estes métodos.
    /// </summary>
    public static partial class GameInput
    {
        private const string KeyboardGroup = "Keyboard&Mouse";
        private const string GamepadGroup = "Gamepad";
        private const string CancelPath = "<Keyboard>/escape";
        private const float RebindTimeoutSeconds = 8f;

        /// <summary>Ações que só aceitam teclado ou controle: o mouse não serve para andar.</summary>
        private static readonly HashSet<string> MovementActions = new HashSet<string> { "Move" };

        private static InputActionRebindingExtensions.RebindingOperation _rebind;

        /// <summary>Disparado com o JSON de todos os overrides depois de cada rebind ou restauração.</summary>
        public static event Action<string> BindingOverridesChanged;

        /// <summary>Há um rebind interativo esperando o jogador apertar algo.</summary>
        public static bool IsRebinding => _rebind != null;

        /// <summary>Um binding que o jogador pode trocar: a ação, o índice no action e o nome para a UI.</summary>
        public readonly struct RebindSlot
        {
            public RebindSlot(InputAction action, int bindingIndex, string label)
            {
                Action = action;
                BindingIndex = bindingIndex;
                Label = label;
            }

            public InputAction Action { get; }
            public int BindingIndex { get; }
            public string Label { get; }
        }

        /// <summary>Desfecho de um rebind interativo.</summary>
        public readonly struct RebindResult
        {
            public RebindResult(bool completed, string conflictWith)
            {
                Completed = completed;
                ConflictWith = conflictWith;
            }

            /// <summary>Falso quando o jogador cancelou (Esc) ou o tempo acabou.</summary>
            public bool Completed { get; }

            /// <summary>Nome da outra ação que já usava a tecla nova, ou null. O binding fica; a UI avisa.</summary>
            public string ConflictWith { get; }
        }

        // ── Overrides ─────────────────────────────────────────────────────────────

        /// <summary>
        /// Aplica os overrides gravados. Vazio volta aos bindings do asset. JSON ilegível também, com aviso:
        /// controle errado é pior que controle padrão.
        /// </summary>
        public static void ApplyBindingOverrides(string json)
        {
            var asset = InputSystem.actions;
            if (asset == null)
                return;

            asset.RemoveAllBindingOverrides();
            if (string.IsNullOrEmpty(json))
                return;

            try
            {
                asset.LoadBindingOverridesFromJson(json);
            }
            catch (Exception e)
            {
                asset.RemoveAllBindingOverrides();
                Debug.LogWarning($"[GameInput] Overrides de binding ilegíveis, voltando ao padrão: {e.Message}");
            }
        }

        /// <summary>Os overrides atuais em JSON (vazio quando não há nenhum).</summary>
        public static string SaveBindingOverrides()
        {
            var asset = InputSystem.actions;
            return asset == null ? string.Empty : asset.SaveBindingOverridesAsJson();
        }

        // ── O que listar ──────────────────────────────────────────────────────────

        /// <summary>
        /// Bindings trocáveis do map Player para teclado/mouse ou para controle. Composite (o "WASD" do
        /// Move) aparece por parte; a cabeça do composite, não.
        /// </summary>
        public static List<RebindSlot> GetRebindSlots(bool gamepad)
        {
            var slots = new List<RebindSlot>();
            var map = InputSystem.actions != null ? InputSystem.actions.FindActionMap(Map) : null;
            if (map == null)
                return slots;

            string group = gamepad ? GamepadGroup : KeyboardGroup;
            foreach (var action in map.actions)
            {
                var bindings = action.bindings;
                for (int i = 0; i < bindings.Count; i++)
                {
                    var binding = bindings[i];
                    if (binding.isComposite || !InGroup(binding, group))
                        continue;

                    string label = binding.isPartOfComposite ? $"{action.name} ({binding.name})" : action.name;
                    slots.Add(new RebindSlot(action, i, label));
                }
            }

            return slots;
        }

        /// <summary>Texto do binding atual e o caminho do controle (ex.: "buttonSouth"), para achar o glifo.</summary>
        public static string GetBindingDisplay(InputAction action, int bindingIndex, out string controlPath)
        {
            controlPath = null;
            if (action == null || bindingIndex < 0 || bindingIndex >= action.bindings.Count)
                return string.Empty;

            return action.GetBindingDisplayString(bindingIndex, out _, out controlPath);
        }

        // ── Rebind interativo ─────────────────────────────────────────────────────

        /// <summary>
        /// Espera o jogador apertar a nova tecla ou botão. Esc cancela, e 8 s sem input também (quem joga
        /// só de controle não tem Esc). O mouse fica fora das ações de movimento. Devolve false se não deu
        /// para começar (outro rebind em curso, índice inválido).
        /// </summary>
        public static bool StartRebind(InputAction action, int bindingIndex, Action<RebindResult> onFinished)
        {
            if (IsRebinding || action == null || bindingIndex < 0 || bindingIndex >= action.bindings.Count)
                return false;

            bool wasEnabled = action.enabled;
            action.Disable(); // o Input System exige a ação desligada durante o rebind

            var binding = action.bindings[bindingIndex];
            var op = action.PerformInteractiveRebinding(bindingIndex)
                .WithCancelingThrough(CancelPath)
                .WithTimeout(RebindTimeoutSeconds)
                .WithControlsExcluding("<Pointer>/position")
                .WithControlsExcluding("<Pointer>/delta")
                .OnMatchWaitForAnother(0.1f);

            if (InGroup(binding, GamepadGroup))
            {
                op.WithControlsHavingToMatchPath("<Gamepad>");
            }
            else
            {
                op.WithControlsHavingToMatchPath("<Keyboard>");
                if (!MovementActions.Contains(action.name))
                    op.WithControlsHavingToMatchPath("<Mouse>");
            }

            op.OnComplete(_ =>
            {
                string conflict = FindConflict(action, bindingIndex);
                EndRebind(action, wasEnabled);
                NotifyOverridesChanged();
                onFinished?.Invoke(new RebindResult(true, conflict));
            });
            op.OnCancel(_ =>
            {
                EndRebind(action, wasEnabled);
                onFinished?.Invoke(new RebindResult(false, null));
            });

            _rebind = op;
            op.Start();
            return true;
        }

        /// <summary>Cancela o rebind em curso (ex.: a tela fechou).</summary>
        public static void CancelRebind() => _rebind?.Cancel();

        // ── Restaurar padrão ──────────────────────────────────────────────────────

        public static void ResetBinding(InputAction action, int bindingIndex)
        {
            if (action == null || bindingIndex < 0 || bindingIndex >= action.bindings.Count)
                return;

            action.RemoveBindingOverride(bindingIndex);
            NotifyOverridesChanged();
        }

        public static void ResetAllBindings()
        {
            var asset = InputSystem.actions;
            if (asset == null)
                return;

            asset.RemoveAllBindingOverrides();
            NotifyOverridesChanged();
        }

        // ── Auxiliares ────────────────────────────────────────────────────────────

        private static bool InGroup(InputBinding binding, string group)
        {
            if (string.IsNullOrEmpty(binding.groups))
                return false;

            foreach (var g in binding.groups.Split(InputBinding.Separator))
            {
                if (g == group)
                    return true;
            }

            return false;
        }

        /// <summary>Outra ação do map Player, do mesmo grupo, que já usa o caminho do binding novo.</summary>
        private static string FindConflict(InputAction action, int bindingIndex)
        {
            var changed = action.bindings[bindingIndex];
            string path = changed.effectivePath;
            if (string.IsNullOrEmpty(path) || action.actionMap == null)
                return null;

            foreach (var other in action.actionMap.actions)
            {
                var bindings = other.bindings;
                for (int i = 0; i < bindings.Count; i++)
                {
                    if (other == action && i == bindingIndex)
                        continue;

                    var b = bindings[i];
                    if (b.isComposite || b.effectivePath != path)
                        continue;

                    if (SharesGroup(b, changed))
                        return other.name;
                }
            }

            return null;
        }

        private static bool SharesGroup(InputBinding a, InputBinding b)
        {
            if (string.IsNullOrEmpty(a.groups) || string.IsNullOrEmpty(b.groups))
                return false;

            foreach (var g in a.groups.Split(InputBinding.Separator))
            {
                if (!string.IsNullOrEmpty(g) && InGroup(b, g))
                    return true;
            }

            return false;
        }

        private static void EndRebind(InputAction action, bool wasEnabled)
        {
            _rebind?.Dispose();
            _rebind = null;
            if (wasEnabled)
                action.Enable();
        }

        private static void NotifyOverridesChanged() => BindingOverridesChanged?.Invoke(SaveBindingOverrides());

        private static void ResetRebind()
        {
            _rebind?.Dispose();
            _rebind = null;
            BindingOverridesChanged = null;
        }
    }
}
