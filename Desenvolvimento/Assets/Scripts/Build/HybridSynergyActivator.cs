using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using Braziliation.Build;

namespace Braziliation.Build
{
    /// <summary>
    /// Avalia as sinergias híbridas ativas na build e aplica ou remove efeitos conforme mudanças.
    /// Delega a detecção de combinações ao HybridSynergyResolver do Core.
    ///
    /// Chamado por PlayerBuildController.OnBuildChanged() após cada mudança de item equipado.
    ///
    /// TODO-DESIGN: tabela de sinergias a definir (Build.md — Sinergias Híbridas):
    ///   Mecânico × Biológico → "Prótese Viva" (resistência física + regeneração biológica)
    ///   Biológico × Místico  → "Mutação Arcana" (percepção de entidades + rastros espirituais)
    ///   Mecânico × Místico   → "Armadura Encantada" (força física + proteção sobrenatural)
    /// </summary>
    public sealed class HybridSynergyActivator : MonoBehaviour
    {
        [Header("Eventos")]
        /// <summary>Disparado quando a lista de sinergias ativas muda. Parâmetro: lista de IDs de efeitos ativos.</summary>
        public UnityEvent<List<string>> OnSynergiesChanged;

        private HybridSynergyResolver _synergyResolver;
        private List<string> _efeitosAtivos = new List<string>();

        private void Awake()
        {
            _synergyResolver = new HybridSynergyResolver();
        }

        /// <summary>
        /// Avalia o conjunto de sinergias híbridas ativas na build atual.
        /// Aplica novos efeitos e remove os que não estão mais presentes.
        /// </summary>
        /// <param name="state">Estado atual da build do jogador.</param>
        public void EvaluateSynergies(BuildState state)
        {
            if (state == null)
            {
                Debug.LogWarning("[HybridSynergyActivator] BuildState nulo.");
                return;
            }

            var novosEfeitos = _synergyResolver.GetActiveHybridEffects(state);

            // Remove efeitos que não estão mais ativos na build atual
            foreach (var efeito in _efeitosAtivos)
            {
                if (!novosEfeitos.Contains(efeito))
                    RemoverEfeito(efeito);
            }

            // Aplica efeitos que passaram a estar ativos
            foreach (var efeito in novosEfeitos)
            {
                if (!_efeitosAtivos.Contains(efeito))
                    AplicarEfeito(efeito);
            }

            _efeitosAtivos = novosEfeitos;
            OnSynergiesChanged?.Invoke(_efeitosAtivos);
        }

        /// <summary>
        /// Aplica um efeito de sinergia híbrida ao personagem.
        /// TODO-DESIGN: mapear cada ID de efeito para sua implementação concreta de gameplay
        /// </summary>
        private void AplicarEfeito(string efeito)
        {
            // TODO-DESIGN: implementar efeitos concretos quando a tabela de sinergias for definida
            Debug.Log($"[HybridSynergyActivator] Sinergia híbrida ativada: '{efeito}'");
        }

        /// <summary>
        /// Remove um efeito de sinergia híbrida do personagem.
        /// TODO-DESIGN: reverter o efeito conforme sua implementação concreta de gameplay
        /// </summary>
        private void RemoverEfeito(string efeito)
        {
            // TODO-DESIGN: reverter efeitos concretos quando a tabela de sinergias for definida
            Debug.Log($"[HybridSynergyActivator] Sinergia híbrida removida: '{efeito}'");
        }
    }
}
