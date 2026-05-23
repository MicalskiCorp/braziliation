using UnityEngine;
using Braziliation.Build;
using Braziliation.Crafting;

namespace Braziliation.UI
{
    /// <summary>
    /// Atualiza a aparência visual do personagem conforme o estágio de expansão de cada receptáculo.
    /// Reage a mudanças na build via PlayerBuildController.OnBuildUpdated.
    ///
    /// ExpansionLevel é lido via ReceptacleController.GetReceptacle() enquanto BuildState não expõe
    /// o dado diretamente — TODO: migrar para BuildState.GetReceptacle() quando a API for implementada.
    ///
    /// TODO: criar sprites de progressão por estágio no pipeline de arte
    /// </summary>
    public sealed class BuildProgressionView : MonoBehaviour
    {
        [Header("Referências")]
        [Tooltip("PlayerBuildController da cena — fonte dos eventos de atualização de build.")]
        [SerializeField] private PlayerBuildController _buildController;

        [Tooltip("ReceptacleController da cena — fonte dos níveis de expansão de cada receptáculo.")]
        [SerializeField] private ReceptacleController _receptacleController;

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
        /// Lê o ExpansionLevel de cada receptáculo e aplica o sprite correspondente
        /// ao estágio de progressão do personagem.
        /// O parâmetro <paramref name="state"/> está reservado para uso futuro quando BuildState
        /// expuser o nível de expansão diretamente.
        /// </summary>
        /// <param name="state">Estado atual da build (reservado para uso futuro).</param>
        public void UpdateVisuals(BuildState state)
        {
            if (_receptacleController == null)
            {
                Debug.LogWarning("[BuildProgressionView] ReceptacleController não vinculado — visuais não atualizados.");
                return;
            }

            // Lê ExpansionLevel via ReceptacleController enquanto BuildState não expõe o dado
            // TODO: migrar para state.GetReceptacle(ReceptacleType.Exoskeleton).ExpansionLevel quando disponível
            var exo   = _receptacleController.GetReceptacle(ReceptacleType.Exoskeleton);
            var capa  = _receptacleController.GetReceptacle(ReceptacleType.Cape);
            var espinha = _receptacleController.GetReceptacle(ReceptacleType.Spine);

            AplicarSprite(exoskeletonStages, exo?.ExpansionLevel ?? 0);
            AplicarSprite(capeStages,        capa?.ExpansionLevel ?? 0);
            AplicarSprite(spineStages,       espinha?.ExpansionLevel ?? 0);

            // TODO: quando o personagem tiver SpriteRenderers independentes por parte do corpo,
            // aplicar cada array em seu próprio renderer (ex: _rendererCapa, _rendererEspinha)
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
