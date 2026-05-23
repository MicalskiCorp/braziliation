using System.Collections.Generic;
using TMPro;
using UnityEngine;
using Braziliation.Build;

namespace Braziliation.UI
{
    /// <summary>
    /// Exibe feedback visual quando sinergias híbridas são desbloqueadas ou removidas.
    /// Subscreve em HybridSynergyActivator.OnSynergiesChanged para reação automática.
    ///
    /// TODO: implementar efeitos visuais (partículas, animações) no pipeline de arte
    /// </summary>
    public sealed class HybridSynergyFeedbackView : MonoBehaviour
    {
        [Header("Referências")]
        [Tooltip("HybridSynergyActivator da cena — fonte dos eventos de sinergia.")]
        [SerializeField] private HybridSynergyActivator _synergyActivator;

        [Header("UI de Feedback")]
        [Tooltip("Objeto raiz do painel de feedback de sinergias — ativado ao exibir notificação.")]
        [SerializeField] private GameObject _painelFeedback;

        [Tooltip("Texto que exibe a lista de sinergias ativas.")]
        [SerializeField] private TextMeshProUGUI _textoSinergias;

        [Header("Efeitos Visuais")]
        [Tooltip("Sistema de partículas disparado ao ativar uma sinergia híbrida.")]
        [SerializeField] private ParticleSystem _particulasSinergia;

        [Header("Tempo de exibição (segundos)")]
        [Tooltip("Duração do feedback visual antes de ser ocultado automaticamente.")]
        [SerializeField] private float _duracaoExibicao = 3f;

        private Coroutine _corotinaOcultacao;

        private void OnEnable()
        {
            if (_synergyActivator == null) return;

            // Subscreve para receber notificações de mudança nas sinergias ativas
            _synergyActivator.OnSynergiesChanged.AddListener(OnSinergiasAlteradas);
        }

        private void OnDisable()
        {
            if (_synergyActivator == null) return;

            _synergyActivator.OnSynergiesChanged.RemoveListener(OnSinergiasAlteradas);
        }

        /// <summary>
        /// Exibe notificação visual com a lista de sinergias híbridas ativas.
        /// </summary>
        /// <param name="activeSynergies">Lista de IDs das sinergias ativas.</param>
        public void ShowSynergyFeedback(List<string> activeSynergies)
        {
            if (activeSynergies == null || activeSynergies.Count == 0)
            {
                HideSynergyFeedback();
                return;
            }

            if (_painelFeedback != null)
                _painelFeedback.SetActive(true);

            if (_textoSinergias != null)
                _textoSinergias.text = string.Join("\n", activeSynergies);

            // Dispara partículas se disponíveis — efeito visual de sinergia ativada
            if (_particulasSinergia != null)
                _particulasSinergia.Play();

            // Agenda ocultação automática após a duração configurada
            if (_corotinaOcultacao != null)
                StopCoroutine(_corotinaOcultacao);

            _corotinaOcultacao = StartCoroutine(OcultarAposDelay());
        }

        /// <summary>
        /// Limpa o feedback visual de sinergias imediatamente.
        /// </summary>
        public void HideSynergyFeedback()
        {
            if (_corotinaOcultacao != null)
            {
                StopCoroutine(_corotinaOcultacao);
                _corotinaOcultacao = null;
            }

            if (_painelFeedback != null)
                _painelFeedback.SetActive(false);

            if (_textoSinergias != null)
                _textoSinergias.text = string.Empty;

            if (_particulasSinergia != null)
                _particulasSinergia.Stop();
        }

        // ── Handlers ────────────────────────────────────────────────────────────

        private void OnSinergiasAlteradas(List<string> sinergias)
        {
            ShowSynergyFeedback(sinergias);
        }

        // ── Coroutines ───────────────────────────────────────────────────────────

        private System.Collections.IEnumerator OcultarAposDelay()
        {
            yield return new WaitForSeconds(_duracaoExibicao);
            HideSynergyFeedback();
        }
    }
}
