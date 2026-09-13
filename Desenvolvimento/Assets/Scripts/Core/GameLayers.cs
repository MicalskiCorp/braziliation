using UnityEngine;

namespace Braziliation.Core
{
    /// <summary>
    /// Camadas de física do projeto, em um lugar só.
    /// Definidas em ProjectSettings/TagManager.asset: 8 = Ground, 9 = Player, 10 = Enemy.
    ///
    /// Por que isso importa: sem máscara, <c>Physics2D.OverlapCircle</c> devolve
    /// *qualquer* colisor, inclusive o do próprio objeto que perguntou. Foi assim que
    /// o player conseguia pular infinito (o teste de chão encostava no próprio corpo)
    /// e se machucava sozinho ao atacar.
    /// </summary>
    public static class GameLayers
    {
        public const string GroundName = "Ground";
        public const string PlayerName = "Player";
        public const string EnemyName = "Enemy";

        public static int Ground => LayerMask.NameToLayer(GroundName);
        public static int Player => LayerMask.NameToLayer(PlayerName);
        public static int Enemy => LayerMask.NameToLayer(EnemyName);

        public static LayerMask GroundMask => MaskOf(GroundName);
        public static LayerMask PlayerMask => MaskOf(PlayerName);
        public static LayerMask EnemyMask => MaskOf(EnemyName);

        /// <summary>Máscara da camada, ou 0 se a camada não existir no projeto.</summary>
        public static LayerMask MaskOf(string layerName)
        {
            var layer = LayerMask.NameToLayer(layerName);
            return layer < 0 ? 0 : 1 << layer;
        }

        /// <summary>
        /// Aplica a camada ao objeto se ela existir. Não falha em projeto sem as camadas
        /// configuradas — apenas avisa, para a cena continuar carregando.
        /// </summary>
        public static void Apply(GameObject target, string layerName)
        {
            if (target == null)
                return;

            var layer = LayerMask.NameToLayer(layerName);
            if (layer < 0)
            {
                Debug.LogWarning($"[GameLayers] Camada '{layerName}' não existe em TagManager.asset. " +
                                 $"'{target.name}' fica na camada padrão.");
                return;
            }

            target.layer = layer;
        }
    }
}
