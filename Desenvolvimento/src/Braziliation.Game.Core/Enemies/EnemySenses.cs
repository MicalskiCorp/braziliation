namespace Braziliation.Enemies
{
    /// <summary>Estado interno do inimigo, exposto para animação, som e depuração.</summary>
    public enum EnemyState
    {
        /// <summary>Parado, sem alvo.</summary>
        Idle = 0,

        /// <summary>Andando entre as pontas da faixa de patrulha.</summary>
        Patrol = 1,

        /// <summary>Avistou o alvo e ainda está reagindo (janela de <c>ReactionSeconds</c>).</summary>
        Alert = 2,

        /// <summary>Indo na direção do alvo.</summary>
        Chase = 3,

        /// <summary>Ajustando distância sem atacar (recuo do skirmisher).</summary>
        Reposition = 4,

        /// <summary>Preparando/desferindo o ataque.</summary>
        Attack = 5,

        /// <summary>Voltando para a âncora depois de perder o alvo ou estourar a coleira.</summary>
        Returning = 6,

        /// <summary>Fugindo do alvo por vida baixa.</summary>
        Flee = 7,

        /// <summary>Sem vida. Não produz mais movimento.</summary>
        Dead = 8,
    }

    /// <summary>
    /// Tudo que o inimigo "percebe" em um tick. É a única entrada do
    /// <see cref="EnemyBrain"/> — o cérebro não conhece Unity, colisor nem cena,
    /// o que permite testá-lo sem engine.
    /// </summary>
    public readonly struct EnemySenses
    {
        public EnemySenses(
            float positionX,
            float anchorX,
            bool hasTarget,
            float targetX,
            float targetDistance,
            bool isGrounded,
            bool wallAhead,
            bool ledgeAhead,
            float healthFraction,
            int facing)
        {
            PositionX = positionX;
            AnchorX = anchorX;
            HasTarget = hasTarget;
            TargetX = targetX;
            TargetDistance = targetDistance;
            IsGrounded = isGrounded;
            WallAhead = wallAhead;
            LedgeAhead = ledgeAhead;
            HealthFraction = healthFraction;
            Facing = facing >= 0 ? 1 : -1;
        }

        /// <summary>Posição horizontal atual do inimigo.</summary>
        public float PositionX { get; }

        /// <summary>Ponto de origem da patrulha (normalmente onde ele nasceu).</summary>
        public float AnchorX { get; }

        public bool HasTarget { get; }

        public float TargetX { get; }

        /// <summary>Distância até o alvo (euclidiana, para respeitar diferença de altura).</summary>
        public float TargetDistance { get; }

        public bool IsGrounded { get; }

        /// <summary>Há parede logo à frente, na direção em que ele encara.</summary>
        public bool WallAhead { get; }

        /// <summary>Falta chão logo à frente, na direção em que ele encara.</summary>
        public bool LedgeAhead { get; }

        /// <summary>Vida atual sobre vida máxima, de 0 a 1.</summary>
        public float HealthFraction { get; }

        /// <summary>Direção que o inimigo encara: -1 esquerda, 1 direita.</summary>
        public int Facing { get; }

        /// <summary>Distância horizontal com sinal até o alvo (positivo = alvo à direita).</summary>
        public float SignedTargetOffsetX => TargetX - PositionX;

        /// <summary>Distância com sinal até a âncora (positivo = âncora à direita).</summary>
        public float SignedAnchorOffsetX => AnchorX - PositionX;
    }

    /// <summary>Decisão do <see cref="EnemyBrain"/> para o tick. O adaptador Unity só aplica.</summary>
    public readonly struct EnemyIntent
    {
        public EnemyIntent(EnemyState state, float moveDirection, float speed, int facing, bool jump, bool attack)
        {
            State = state;
            MoveDirection = moveDirection;
            Speed = speed;
            Facing = facing >= 0 ? 1 : -1;
            Jump = jump;
            Attack = attack;
        }

        public EnemyState State { get; }

        /// <summary>-1, 0 ou 1.</summary>
        public float MoveDirection { get; }

        /// <summary>Velocidade desejada em unidades/segundo.</summary>
        public float Speed { get; }

        public int Facing { get; }

        public bool Jump { get; }

        /// <summary>Pulso de ataque: verdadeiro em exatamente um tick por ataque.</summary>
        public bool Attack { get; }

        /// <summary>Velocidade horizontal resultante, já com sinal.</summary>
        public float VelocityX => MoveDirection * Speed;

        public static EnemyIntent Still(EnemyState state, int facing) =>
            new EnemyIntent(state, 0f, 0f, facing, false, false);
    }
}
