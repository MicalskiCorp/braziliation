using UnityEngine;
using Braziliation.Build;
using Braziliation.Crafting;

namespace Braziliation.UI
{
    /// <summary>
    /// Atualiza a aparência visual do personagem conforme o estágio de expansão de cada receptáculo.
    /// Reage a mudanças na build via PlayerBuildController.OnBuildUpdated e lê o ExpansionLevel só do
    /// BuildState emitido (BuildState.GetReceptacle) — não depende do ReceptacleController.
    ///
    /// TODO: criar sprites de progressão por estágio no pipeline de arte
    /// </summary>
    public sealed class BuildProgressionView : MonoBehaviour
    {
        [Header("Referências")]
        [Tooltip("PlayerBuildController da cena — fonte dos eventos de atualização de build.")]
        [SerializeField] private PlayerBuildController _buildController;

        [Tooltip("SpriteRenderer do personagem — receberá os sprites de progressão.")]
        [SerializeField] private SpriteRenderer _spriteRenderer;

        [Header("Estágios do Exoesqueleto")]
        [Tooltip("Sprites de progressão do Exoesqueleto dos Trilhos — índice 0 = base, índices seguintes = expansões.")]
        [SerializeField] private Sprite[] exoskeletonStages;

        [Header("Estágios da Capa")]
        [Tooltip("Sprites de progressão da Capa das Lendas do Mar — índice 0 = base, índices seguintes = expansões.")]
        [SerializeField] private Sprite[] capeStages;

        [Header("Estágios da Espinha")]
        [Tooltip("Sprites de progressão da Espinha de Fungo — índice 0 = base, índices seguintes = expansões.")]
        [SerializeField] private Sprite[] spineStages;

        private void OnEnable()
        {
            if (_buildController == null) return;

            // Subscreve no evento de build atualizada para manter visuais sincronizados
            _buildController.OnBuildUpdated.AddListener(OnBuildAtualizada);
        }

        private void OnDisable()
        {
            if (_buildController == null) return;

            _buildController.OnBuildUpdated.RemoveListener(OnBuildAtualizada);
        }

        /// <summary>
        /// Lê o ExpansionLevel de cada receptáculo no estado da build e aplica o sprite correspondente
        /// ao estágio de progressão do personagem. Receptáculo ausente conta como estágio 0.
        /// </summary>
        /// <param name="state">Estado atual da build, emitido pelo PlayerBuildController.</param>
        public void UpdateVisuals(BuildState state)
        {
            if (state == null)
            {
                Debug.LogWarning("[BuildProgressionView] BuildState nulo — visuais não atualizados.");
                return;
            }

            AplicarSprite(exoskeletonStages, state.GetReceptacle(ReceptacleType.Exoskeleton)?.ExpansionLevel ?? 0);
            AplicarSprite(capeStages,        state.GetReceptacle(ReceptacleType.Cape)?.ExpansionLevel ?? 0);
            AplicarSprite(spineStages,       state.GetReceptacle(ReceptacleType.Spine)?.ExpansionLevel ?? 0);

            // Os três arrays caem no mesmo renderer e só o último aparece: dívida "três arrays de
            // estágio no mesmo SpriteRenderer" (tech_debt.md), pendência ⏸ em Docs/TODO.md › UI e arte.
        }

        // ── Handlers ────────────────────────────────────────────────────────────

        private void OnBuildAtualizada()
        {
            if (_buildController == null) return;
            UpdateVisuals(_buildController.GetBuildState());
        }

        // ── Helpers ─────────────────────────────────────────────────────────────

        private void AplicarSprite(Sprite[] estagios, int nivel)
        {
            if (estagios == null || estagios.Length == 0 || _spriteRenderer == null) return;

            int indiceSeguro = Mathf.Clamp(nivel, 0, estagios.Length - 1);
            _spriteRenderer.sprite = estagios[indiceSeguro];
        }
    }
}
