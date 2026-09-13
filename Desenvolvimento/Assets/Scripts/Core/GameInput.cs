using UnityEngine;
using UnityEngine.InputSystem;

namespace Braziliation.Core
{
    /// <summary>
    /// Ponto único de leitura de input do jogo, sobre o action map project-wide
    /// (<c>Assets/InputSystem_Actions.inputactions</c>, registrado em
    /// ProjectSettings/EditorBuildSettings.asset).
    ///
    /// Por que isso importa: antes, cada script lia <c>Keyboard.current</c>,
    /// <c>Mouse.current</c> e <c>Gamepad.current</c> direto. Isso amarra a mecânica ao
    /// dispositivo e mata quatro coisas que o alvo Steam exige — rebind pelo jogador,
    /// Steam Input, glifos de controle corretos e Steam Deck. Ler pelo action map
    /// devolve tudo isso de graça: quem quiser trocar a tecla, troca o binding.
    ///
    /// Convenção: só expõe as ações que o jogo usa hoje. Ação nova = binding no asset
    /// primeiro, propriedade aqui depois — nunca polling de dispositivo espalhado.
    /// </summary>
    public static class GameInput
    {
        private const string Map = "Player";

        private static InputAction _move;
        private static InputAction _jump;
        private static InputAction _attack;
        private static InputAction _interact;
        private static bool _warnedMissingAsset;

        // ── Ações ─────────────────────────────────────────────────────────────────

        public static InputAction Move     => Resolve(ref _move,     "Move");
        public static InputAction Jump     => Resolve(ref _jump,     "Jump");
        public static InputAction Attack   => Resolve(ref _attack,   "Attack");
        public static InputAction Interact => Resolve(ref _interact, "Interact");

        // ── Leitura de conveniência ───────────────────────────────────────────────

        /// <summary>Eixo horizontal de -1 a 1. Zero quando o input não está disponível.</summary>
        public static float MoveX
        {
            get
            {
                var action = Move;
                return action == null ? 0f : Mathf.Clamp(action.ReadValue<Vector2>().x, -1f, 1f);
            }
        }

        public static bool JumpPressedThisFrame     => WasPressed(Jump);
        public static bool AttackPressedThisFrame   => WasPressed(Attack);
        public static bool InteractPressedThisFrame => WasPressed(Interact);

        // ── Auxiliares ────────────────────────────────────────────────────────────

        private static bool WasPressed(InputAction action)
            => action != null && action.WasPressedThisFrame();

        /// <summary>
        /// Resolve a ação uma vez e mantém em cache. Devolve null — sem lançar — quando o
        /// asset project-wide não está configurado, para a cena continuar carregando.
        /// </summary>
        private static InputAction Resolve(ref InputAction cached, string actionName)
        {
            if (cached != null)
                return cached;

            var asset = InputSystem.actions;
            if (asset == null)
            {
                if (!_warnedMissingAsset)
                {
                    _warnedMissingAsset = true;
                    Debug.LogWarning(
                        "[GameInput] Nenhum action asset project-wide configurado. " +
                        "Project Settings > Input System Package > Project-wide Actions.");
                }
                return null;
            }

            cached = asset.FindAction($"{Map}/{actionName}", throwIfNotFound: false);
            if (cached == null)
            {
                Debug.LogWarning($"[GameInput] Ação '{Map}/{actionName}' não existe no action asset.");
                return null;
            }

            if (!cached.enabled)
                cached.Enable();

            return cached;
        }

        /// <summary>
        /// Limpa o cache entre entradas em Play Mode. Sem isso, com Domain Reload
        /// desativado, o segundo Play carrega referências de ações de uma sessão morta.
        /// </summary>
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetCache()
        {
            _move = null;
            _jump = null;
            _attack = null;
            _interact = null;
            _warnedMissingAsset = false;
        }
    }
}
