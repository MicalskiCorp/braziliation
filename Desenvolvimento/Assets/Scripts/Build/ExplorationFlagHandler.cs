using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using Braziliation.Build;

namespace Braziliation.Build
{
    /// <summary>
    /// Lê as flags de exploração desbloqueadas no BuildState e ativa os comportamentos correspondentes.
    /// Cada flag mapeia para um conjunto de GameObjects que são ativados/desativados conforme a build muda.
    ///
    /// Conforme Build.md — Utilidade na Exploração por Pilar:
    ///   Mecânico  — NightVision:         visão noturna, interação com máquinas.
    ///   Místico   — HiddenPaths:         passagens ocultas, detecção de relíquias.
    ///   Biológico — UnderwaterBreathing: respiração submersa, sobrevivência em áreas tóxicas.
    ///
    /// Como usar: vincule no Inspector os GameObjects de efeito de cada flag. Eles serão
    /// ativados quando a flag estiver ativa na build e desativados quando removida.
    /// </summary>
    public sealed class ExplorationFlagHandler : MonoBehaviour
    {
        [Header("Efeitos — NightVision (Mecânico)")]
        [Tooltip("GameObjects ativados ao desbloquear visão noturna (ex: PostProcessVolume, câmera noturna).")]
        [SerializeField] private List<GameObject> _nightVisionObjects = new();

        [Header("Efeitos — HiddenPaths (Místico)")]
        [Tooltip("GameObjects ativados ao desbloquear caminhos ocultos (ex: reveladores de passagem, detectores de relíquia).")]
        [SerializeField] private List<GameObject> _hiddenPathsObjects = new();

        [Header("Efeitos — UnderwaterBreathing (Biológico)")]
        [Tooltip("GameObjects ativados ao desbloquear respiração submersa (ex: zona de água sem sufocamento, overlay de bolhas).")]
        [SerializeField] private List<GameObject> _underwaterBreathingObjects = new();

        [Header("Eventos")]
        /// <summary>Disparado ao ativar uma flag. Parâmetro: identificador da flag ativada.</summary>
        public UnityEvent<string> OnFlagActivated;

        /// <summary>Disparado ao desativar uma flag. Parâmetro: identificador da flag desativada.</summary>
        public UnityEvent<string> OnFlagDeactivated;

        // Flags atualmente ativas — usadas para detectar mudanças entre chamadas
        private readonly HashSet<string> _flagsAtivas = new HashSet<string>();

        /// <summary>
        /// Sincroniza os efeitos de exploração com o estado atual da build.
        /// Ativa as flags novas e desativa as que foram removidas.
        /// Deve ser chamado sempre que a build mudar (ex: pelo PlayerBuildController.OnBuildChanged).
        /// </summary>
        /// <param name="state">Estado atual da build do jogador.</param>
        public void SyncFlags(BuildState state)
        {
            if (state == null)
            {
                Debug.LogWarning("[ExplorationFlagHandler] BuildState nulo.");
                return;
            }

            // Desativa flags que não estão mais na build
            var flagsParaRemover = new List<string>();
            foreach (var flag in _flagsAtivas)
            {
                if (!state.UnlockedExplorationFlags.Contains(flag))
                    flagsParaRemover.Add(flag);
            }
            foreach (var flag in flagsParaRemover)
                DesativarFlag(flag);

            // Ativa flags novas na build
            foreach (var flag in state.UnlockedExplorationFlags)
            {
                if (!_flagsAtivas.Contains(flag))
                    AtivarFlag(flag);
            }
        }

        /// <summary>
        /// Desativa todos os efeitos de exploração e limpa o estado interno.
        /// Útil ao carregar um save ou reiniciar a build.
        /// </summary>
        public void ClearAllFlags()
        {
            var flags = new List<string>(_flagsAtivas);
            foreach (var flag in flags)
                DesativarFlag(flag);
        }


        /// <summary>
        /// Despacha a ativação para o método de efeito correspondente à flag.
        /// </summary>
        private void AtivarFlag(string flag)
        {
            switch (flag)
            {
                case "NightVision":
                    SetActive(_nightVisionObjects, true);
                    break;

                case "HiddenPaths":
                    SetActive(_hiddenPathsObjects, true);
                    break;

                case "UnderwaterBreathing":
                    SetActive(_underwaterBreathingObjects, true);
                    break;

                default:
                    Debug.LogWarning($"[ExplorationFlagHandler] Flag de exploração desconhecida: '{flag}'");
                    return;
            }

            _flagsAtivas.Add(flag);
            OnFlagActivated?.Invoke(flag);
        }

        /// <summary>
        /// Desativa os efeitos correspondentes à flag e remove do conjunto ativo.
        /// </summary>
        private void DesativarFlag(string flag)
        {
            switch (flag)
            {
                case "NightVision":
                    SetActive(_nightVisionObjects, false);
                    break;

                case "HiddenPaths":
                    SetActive(_hiddenPathsObjects, false);
                    break;

                case "UnderwaterBreathing":
                    SetActive(_underwaterBreathingObjects, false);
                    break;

                default:
                    Debug.LogWarning($"[ExplorationFlagHandler] Flag desconhecida ao desativar: '{flag}'");
                    return;
            }

            _flagsAtivas.Remove(flag);
            OnFlagDeactivated?.Invoke(flag);
        }

        /// <summary>Ativa ou desativa todos os GameObjects da lista.</summary>
        private static void SetActive(List<GameObject> objects, bool active)
        {
            foreach (var obj in objects)
            {
                if (obj != null)
                    obj.SetActive(active);
            }
        }
    }
}
