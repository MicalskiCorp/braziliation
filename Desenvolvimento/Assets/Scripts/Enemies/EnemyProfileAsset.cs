using Braziliation.Enemies;
using UnityEngine;

namespace Braziliation.Gameplay.Enemies
{
    /// <summary>
    /// Perfil de comportamento de um arquétipo de inimigo, editável no Inspector.
    /// É só um invólucro do <see cref="EnemyBehaviorProfile"/> (C# puro, testado sem
    /// engine) — a lógica vive no <see cref="EnemyBrain"/>, aqui ficam só os números.
    ///
    /// Crie um asset por arquétipo em Assets/ScriptableObjects/Enemies/ e aponte o
    /// <see cref="EnemyController"/> para ele. Vários inimigos podem compartilhar o
    /// mesmo perfil.
    /// </summary>
    [CreateAssetMenu(
        fileName = "EnemyProfile_Novo",
        menuName = "Braziliation/Inimigos/Perfil de Comportamento",
        order = 0)]
    public sealed class EnemyProfileAsset : ScriptableObject
    {
        [Header("Identidade")]
        [Tooltip("Identificador do arquétipo, para logs e depuração.")]
        [SerializeField] private string _id = "novo-inimigo";

        [Tooltip("Muda a forma de agir, não só os números.")]
        [SerializeField] private EnemyAggressionStyle _style = EnemyAggressionStyle.Patroller;

        [Header("Patrulha")]
        [SerializeField] private float _patrolSpeed = 1.6f;
        [Tooltip("Meia-largura da faixa de patrulha ao redor do ponto de spawn.")]
        [SerializeField] private float _patrolRange = 2f;
        [Tooltip("Pausa ao chegar na ponta da faixa. 0 = vira na hora.")]
        [SerializeField] private float _patrolPauseSeconds = 0.6f;

        [Header("Perseguição")]
        [SerializeField] private float _chaseSpeed = 3.2f;
        [SerializeField] private float _detectRadius = 5f;
        [Tooltip("Deve ser maior que o raio de detecção: a histerese evita oscilar na borda.")]
        [SerializeField] private float _loseTargetRadius = 7.5f;
        [Tooltip("Distância máxima da âncora perseguindo. Passou disso, desiste e volta.")]
        [SerializeField] private float _leashRadius = 8f;
        [Tooltip("Janela de reação entre avistar e agir — dá tempo do jogador responder.")]
        [SerializeField] private float _reactionSeconds = 0.25f;

        [Header("Ataque")]
        [SerializeField] private float _attackRange = 1.4f;
        [SerializeField] private float _attackWindupSeconds = 0.2f;
        [SerializeField] private float _attackCooldownSeconds = 1.1f;
        [Tooltip("Distância que o estilo Skirmisher tenta manter do alvo.")]
        [SerializeField] private float _preferredDistance = 3f;

        [Header("Fuga")]
        [Tooltip("Fração de vida abaixo da qual foge. 0 desliga.")]
        [Range(0f, 1f)]
        [SerializeField] private float _fleeHealthFraction;
        [SerializeField] private float _fleeSpeed = 3.5f;

        [Header("Terreno")]
        [SerializeField] private bool _turnsAtLedges = true;
        [SerializeField] private bool _turnsAtWalls = true;
        [SerializeField] private bool _canJump;
        [Tooltip("Persegue mesmo em direção a um precipício. Inimigo raivoso.")]
        [SerializeField] private bool _ignoresLedgesWhileChasing;

        public EnemyBehaviorProfile ToProfile() => new EnemyBehaviorProfile
        {
            Id = _id,
            Style = _style,
            PatrolSpeed = _patrolSpeed,
            PatrolRange = _patrolRange,
            PatrolPauseSeconds = _patrolPauseSeconds,
            ChaseSpeed = _chaseSpeed,
            DetectRadius = _detectRadius,
            LoseTargetRadius = _loseTargetRadius,
            LeashRadius = _leashRadius,
            ReactionSeconds = _reactionSeconds,
            AttackRange = _attackRange,
            AttackWindupSeconds = _attackWindupSeconds,
            AttackCooldownSeconds = _attackCooldownSeconds,
            PreferredDistance = _preferredDistance,
            FleeHealthFraction = _fleeHealthFraction,
            FleeSpeed = _fleeSpeed,
            TurnsAtLedges = _turnsAtLedges,
            TurnsAtWalls = _turnsAtWalls,
            CanJump = _canJump,
            IgnoresLedgesWhileChasing = _ignoresLedgesWhileChasing,
        };
    }
}
