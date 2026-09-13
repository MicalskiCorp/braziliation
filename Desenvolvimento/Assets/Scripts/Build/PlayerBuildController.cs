using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using Braziliation.Build;
using Braziliation.Core;

namespace Braziliation.Build
{
    /// <summary>
    /// Aplica os stats e habilidades da build atual ao jogador.
    /// Reage a mudanças nos receptáculos (equip/unequip) e propaga o estado para sistemas dependentes.
    ///
    /// Depende de: ReceptacleController.OnItemEquipped
    /// Depende de: ReceptacleController.OnItemUnequipped
    /// </summary>
    public sealed class PlayerBuildController : MonoBehaviour
    {
        [Header("Referências")]
        /// <summary>
        /// Componente do jogador que implementa IStatReceiver (ex: PlayerController).
        /// Receberá os stats agregados da build ao chamar ApplyBuild().
        /// </summary>
        [SerializeField] private MonoBehaviour _statReceiverComponent;

        /// <summary>
        /// Referência ao HybridSynergyActivator para avaliar sinergias ao mudar a build.
        /// </summary>
        [SerializeField] private HybridSynergyActivator _synergyActivator;

        /// <summary>
        /// Referência ao ExplorationFlagHandler para sincronizar flags ao mudar a build.
        /// </summary>
        [SerializeField] private ExplorationFlagHandler _explorationFlagHandler;

        [Header("Eventos")]
        /// <summary>Disparado sempre que a build é aplicada ao personagem.</summary>
        public UnityEvent OnBuildUpdated;

        // Estado atual da build — injetado via SetBuildState() ou criado aqui em Awake
        private BuildState _buildState;
        private IStatReceiver _statReceiver;

        private void Awake()
        {
            _buildState = new BuildState();

            if (_statReceiverComponent is IStatReceiver receiver)
                _statReceiver = receiver;
            else
                Debug.LogWarning("[PlayerBuildController] _statReceiverComponent não implementa IStatReceiver.");
        }

        /// <summary>
        /// Lê o BuildState atual, agrega os stats de todos os itens equipados
        /// e os aplica ao PlayerController via IStatReceiver.
        /// </summary>
        public void ApplyBuild()
        {
            var statsAgregados = AgregarStats(_buildState);
            _statReceiver?.ApplyStats(statsAgregados);
            OnBuildUpdated?.Invoke();
        }

        /// <summary>
        /// Chamado quando um item é equipado ou desequipado em qualquer receptáculo.
        /// Avalia sinergias híbridas, sincroniza flags de exploração e aplica a build atualizada.
        /// </summary>
        public void OnBuildChanged()
        {
            // Avalia sinergias híbridas — delega ao HybridSynergyActivator
            _synergyActivator?.EvaluateSynergies(_buildState);

            // Sincroniza flags de exploração — delega ao ExplorationFlagHandler
            _explorationFlagHandler?.SyncFlags(_buildState);

            ApplyBuild();
        }

        /// <summary>
        /// Expõe o BuildState atual para outros sistemas (ex: ExplorationFlagHandler).
        /// </summary>
        public BuildState GetBuildState() => _buildState;

        /// <summary>
        /// Permite injetar o BuildState atualizado externamente (ex: ao carregar save).
        /// </summary>
        public void SetBuildState(BuildState state)
        {
            _buildState = state;
        }

        /// <summary>
        /// Configura as dependências de runtime quando o setup é feito por bootstrap automático.
        /// </summary>
        public void ConfigureDependencies(
            MonoBehaviour statReceiverComponent,
            HybridSynergyActivator synergyActivator,
            ExplorationFlagHandler explorationFlagHandler)
        {
            _statReceiverComponent = statReceiverComponent;
            _synergyActivator = synergyActivator;
            _explorationFlagHandler = explorationFlagHandler;

            _statReceiver = _statReceiverComponent as IStatReceiver;
            if (_statReceiver == null && _statReceiverComponent != null)
                Debug.LogWarning("[PlayerBuildController] Componente informado não implementa IStatReceiver.");
        }

        /// <summary>
        /// Agrega os stats de todos os itens equipados nos receptáculos em um único dicionário somado.
        /// </summary>
        private Dictionary<string, float> AgregarStats(BuildState state)
        {
            var total = new Dictionary<string, float>();

            foreach (var item in state.GetEquippedItems())
            {
                foreach (var kvp in item.Stats)
                {
                    if (total.ContainsKey(kvp.Key))
                        total[kvp.Key] += kvp.Value;
                    else
                        total[kvp.Key] = kvp.Value;
                }
            }

            return total;
        }
    }
}
