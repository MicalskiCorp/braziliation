namespace Braziliation.Enemies
{
    /// <summary>
    /// Estilo de agressão do inimigo. Muda a *forma* de agir, não só os números:
    /// dois inimigos com a mesma velocidade e o mesmo raio se comportam de modo
    /// diferente conforme o estilo.
    /// </summary>
    public enum EnemyAggressionStyle
    {
        /// <summary>Patrulha uma faixa e persegue quem entrar no raio. Padrão do bicho de rua.</summary>
        Patroller = 0,

        /// <summary>Não patrulha: guarda um ponto e só ataca quem chega perto. Guarda de porta, torre.</summary>
        Sentry = 1,

        /// <summary>Espera parado, e ao detectar avança em linha reta sem recuar. Investida pesada.</summary>
        Charger = 2,

        /// <summary>Mantém distância preferida: aproxima se longe, recua se perto. Inimigo de ataque à distância.</summary>
        Skirmisher = 3,

        /// <summary>Fica imóvel até o alvo chegar muito perto, então persegue rápido. Emboscada.</summary>
        Ambusher = 4,
    }

    /// <summary>
    /// Dados de comportamento de um arquétipo de inimigo. É a única coisa que muda
    /// entre inimigos que usam o mesmo <see cref="EnemyBrain"/> — nada de código novo
    /// por inimigo enquanto o estilo existente atender.
    /// </summary>
    public sealed class EnemyBehaviorProfile
    {
        public string Id { get; set; } = "generico";

        public EnemyAggressionStyle Style { get; set; } = EnemyAggressionStyle.Patroller;

        // ---------------------------------------------------------------- patrulha
        /// <summary>Velocidade de patrulha, em unidades/segundo.</summary>
        public float PatrolSpeed { get; set; } = 2f;

        /// <summary>Meia-largura da faixa de patrulha ao redor da âncora (ponto de spawn).</summary>
        public float PatrolRange { get; set; } = 2f;

        /// <summary>Pausa ao chegar na ponta da patrulha, em segundos. 0 = vira na hora.</summary>
        public float PatrolPauseSeconds { get; set; }

        // ------------------------------------------------------------- perseguição
        public float ChaseSpeed { get; set; } = 3f;

        /// <summary>Raio para *adquirir* o alvo.</summary>
        public float DetectRadius { get; set; } = 4f;

        /// <summary>
        /// Raio para *perder* o alvo. Deve ser maior que <see cref="DetectRadius"/>:
        /// a histerese evita o inimigo piscando entre perseguir e patrulhar na borda.
        /// </summary>
        public float LoseTargetRadius { get; set; } = 6f;

        /// <summary>
        /// Distância máxima da âncora que o inimigo aceita percorrer perseguindo.
        /// Passou disso, ele desiste e volta. Evita puxar o mapa inteiro atrás de você.
        /// </summary>
        public float LeashRadius { get; set; } = 8f;

        /// <summary>Tempo entre avistar o alvo e começar a agir. Dá janela de reação ao jogador.</summary>
        public float ReactionSeconds { get; set; } = 0.2f;

        // ------------------------------------------------------------------ ataque
        public float AttackRange { get; set; } = 1.2f;
        public float AttackWindupSeconds { get; set; } = 0.25f;
        public float AttackCooldownSeconds { get; set; } = 1f;

        /// <summary>Distância que o <see cref="EnemyAggressionStyle.Skirmisher"/> tenta manter.</summary>
        public float PreferredDistance { get; set; } = 3f;

        // ------------------------------------------------------------------- fuga
        /// <summary>Fração de vida abaixo da qual o inimigo foge. 0 desliga a fuga.</summary>
        public float FleeHealthFraction { get; set; }

        public float FleeSpeed { get; set; } = 3.5f;

        // ------------------------------------------------------- navegação e terreno
        /// <summary>Vira ao detectar precipício à frente. Desligue para inimigos que voam ou caem de propósito.</summary>
        public bool TurnsAtLedges { get; set; } = true;

        /// <summary>Vira ao detectar parede à frente.</summary>
        public bool TurnsAtWalls { get; set; } = true;

        /// <summary>Permite pular obstáculos durante a perseguição.</summary>
        public bool CanJump { get; set; }

        /// <summary>
        /// Ignora precipício enquanto persegue (mas ainda respeita ao patrulhar).
        /// Inimigo raivoso que se joga atrás do jogador.
        /// </summary>
        public bool IgnoresLedgesWhileChasing { get; set; }

        /// <summary>Perfil do inimigo básico da demo: patrulha curta, persegue, morde de perto.</summary>
        public static EnemyBehaviorProfile CreateDefaultPatroller() => new EnemyBehaviorProfile
        {
            Id = "patrulheiro-padrao",
            Style = EnemyAggressionStyle.Patroller,
            PatrolSpeed = 1.6f,
            PatrolRange = 2f,
            PatrolPauseSeconds = 0.6f,
            ChaseSpeed = 3.2f,
            DetectRadius = 5f,
            LoseTargetRadius = 7.5f,
            LeashRadius = 8f,
            ReactionSeconds = 0.25f,
            AttackRange = 1.4f,
            AttackWindupSeconds = 0.2f,
            AttackCooldownSeconds = 1.1f,
            TurnsAtLedges = true,
            TurnsAtWalls = true,
        };
    }
}
