using System;

namespace Braziliation.Enemies
{
    /// <summary>
    /// Motor de IA de inimigos: uma máquina de estados determinística, sem Unity.
    /// A variação entre inimigos vem do <see cref="EnemyBehaviorProfile"/>
    /// (números + <see cref="EnemyAggressionStyle"/>), não de código novo por inimigo.
    ///
    /// Uso: crie um cérebro por inimigo e chame <see cref="Tick"/> a cada passo de
    /// física, passando o que ele percebe; aplique o <see cref="EnemyIntent"/> devolvido.
    ///
    /// Determinístico por construção: mesma sequência de sentidos e de deltas produz
    /// sempre a mesma sequência de intenções. Sem <c>Random</c>, sem relógio global.
    /// </summary>
    public sealed class EnemyBrain
    {
        private readonly EnemyBehaviorProfile _profile;

        private EnemyState _state = EnemyState.Idle;
        private int _facing;
        private int _patrolDirection;
        private bool _engaged;
        private float _stateTime;
        private float _reactionTime;
        private float _pauseTime;
        private float _attackCooldown;
        private float _windupTime;
        private bool _windingUp;

        public EnemyBrain(EnemyBehaviorProfile profile, int initialFacing = 1)
        {
            _profile = profile ?? throw new ArgumentNullException(nameof(profile));
            _facing = initialFacing >= 0 ? 1 : -1;
            _patrolDirection = _facing;
        }

        public EnemyState State => _state;

        public int Facing => _facing;

        /// <summary>Segundos no estado atual. Útil para animação e depuração.</summary>
        public float StateTime => _stateTime;

        /// <summary>Verdadeiro enquanto o inimigo considera o alvo ativo (já passou a histerese).</summary>
        public bool HasEngagedTarget => _engaged;

        public EnemyIntent Tick(in EnemySenses senses, float deltaTime)
        {
            if (deltaTime < 0f)
                deltaTime = 0f;

            if (senses.HealthFraction <= 0f)
            {
                Transition(EnemyState.Dead);
                return EnemyIntent.Still(EnemyState.Dead, _facing);
            }

            AdvanceTimers(deltaTime);
            UpdateEngagement(senses);

            var intent = Decide(senses, deltaTime);
            _facing = intent.Facing;
            return intent;
        }

        // ------------------------------------------------------------------ timers
        private void AdvanceTimers(float deltaTime)
        {
            _stateTime += deltaTime;
            _attackCooldown = Math.Max(0f, _attackCooldown - deltaTime);
            _pauseTime = Math.Max(0f, _pauseTime - deltaTime);

            if (_reactionTime > 0f)
                _reactionTime = Math.Max(0f, _reactionTime - deltaTime);

            if (_windingUp)
                _windupTime = Math.Max(0f, _windupTime - deltaTime);
        }

        /// <summary>
        /// Aquisição e perda de alvo com histerese: entra em combate no
        /// <c>DetectRadius</c> e só sai no <c>LoseTargetRadius</c>, que é maior.
        /// Sem isso o inimigo oscila entre perseguir e patrulhar na borda do raio.
        /// </summary>
        private void UpdateEngagement(in EnemySenses senses)
        {
            if (!senses.HasTarget)
            {
                _engaged = false;
                return;
            }

            var detectRadius = _profile.Style == EnemyAggressionStyle.Ambusher
                ? _profile.DetectRadius * 0.5f
                : _profile.DetectRadius;

            if (!_engaged)
            {
                if (senses.TargetDistance <= detectRadius)
                {
                    _engaged = true;
                    _reactionTime = _profile.ReactionSeconds;
                }
                return;
            }

            var loseRadius = Math.Max(_profile.LoseTargetRadius, detectRadius);
            if (senses.TargetDistance > loseRadius || IsBeyondLeash(senses))
                _engaged = false;
        }

        private bool IsBeyondLeash(in EnemySenses senses)
        {
            if (_profile.LeashRadius <= 0f)
                return false;

            return Math.Abs(senses.PositionX - senses.AnchorX) > _profile.LeashRadius;
        }

        // ----------------------------------------------------------------- decisão
        private EnemyIntent Decide(in EnemySenses senses, float deltaTime)
        {
            if (ShouldFlee(senses))
                return Flee(senses);

            if (_engaged)
            {
                if (_reactionTime > 0f)
                {
                    Transition(EnemyState.Alert);
                    return EnemyIntent.Still(EnemyState.Alert, FacingTowards(senses.SignedTargetOffsetX));
                }

                return Engage(senses);
            }

            _windingUp = false;

            if (IsBeyondLeash(senses) || IsOutsidePatrolBand(senses))
                return ReturnToAnchor(senses);

            return Patrol(senses, deltaTime);
        }

        private bool ShouldFlee(in EnemySenses senses)
        {
            return _profile.FleeHealthFraction > 0f
                   && senses.HealthFraction <= _profile.FleeHealthFraction
                   && senses.HasTarget;
        }

        private EnemyIntent Flee(in EnemySenses senses)
        {
            Transition(EnemyState.Flee);
            _windingUp = false;

            var away = senses.SignedTargetOffsetX >= 0f ? -1 : 1;
            var direction = BlockedAhead(senses, away, respectLedges: true) ? 0 : away;
            return new EnemyIntent(EnemyState.Flee, direction, _profile.FleeSpeed, away, false, false);
        }

        private EnemyIntent Engage(in EnemySenses senses)
        {
            var towards = FacingTowards(senses.SignedTargetOffsetX);
            var distance = senses.TargetDistance;

            if (_windingUp)
            {
                if (_windupTime > 0f)
                {
                    Transition(EnemyState.Attack);
                    return EnemyIntent.Still(EnemyState.Attack, towards);
                }

                _windingUp = false;
                _attackCooldown = _profile.AttackCooldownSeconds;
                Transition(EnemyState.Attack);
                return new EnemyIntent(EnemyState.Attack, 0f, 0f, towards, false, true);
            }

            if (distance <= _profile.AttackRange && _attackCooldown <= 0f)
            {
                _windingUp = true;
                _windupTime = _profile.AttackWindupSeconds;
                Transition(EnemyState.Attack);

                // Sem tempo de preparação o ataque sai no mesmo tick.
                if (_windupTime <= 0f)
                {
                    _windingUp = false;
                    _attackCooldown = _profile.AttackCooldownSeconds;
                    return new EnemyIntent(EnemyState.Attack, 0f, 0f, towards, false, true);
                }

                return EnemyIntent.Still(EnemyState.Attack, towards);
            }

            return MoveWhileEngaged(senses, towards, distance);
        }

        /// <summary>Movimento durante o combate. É aqui que o estilo muda o comportamento.</summary>
        private EnemyIntent MoveWhileEngaged(in EnemySenses senses, int towards, float distance)
        {
            switch (_profile.Style)
            {
                case EnemyAggressionStyle.Sentry:
                    // Guarda o posto: encara o alvo mas não sai do lugar.
                    Transition(EnemyState.Alert);
                    return EnemyIntent.Still(EnemyState.Alert, towards);

                case EnemyAggressionStyle.Skirmisher:
                    if (distance < _profile.PreferredDistance * 0.85f)
                    {
                        var away = -towards;
                        Transition(EnemyState.Reposition);
                        var backOff = BlockedAhead(senses, away, respectLedges: true) ? 0 : away;
                        // Recua sem dar as costas: continua encarando o alvo.
                        return new EnemyIntent(EnemyState.Reposition, backOff, _profile.ChaseSpeed, towards, false, false);
                    }

                    if (distance > _profile.PreferredDistance * 1.15f)
                        return Chase(senses, towards);

                    Transition(EnemyState.Alert);
                    return EnemyIntent.Still(EnemyState.Alert, towards);

                default:
                    return Chase(senses, towards);
            }
        }

        private EnemyIntent Chase(in EnemySenses senses, int towards)
        {
            Transition(EnemyState.Chase);

            var respectLedges = _profile.TurnsAtLedges && !_profile.IgnoresLedgesWhileChasing;
            var blocked = BlockedAhead(senses, towards, respectLedges);
            var jump = blocked && _profile.CanJump && senses.IsGrounded && senses.WallAhead;

            // Perseguindo, obstáculo não faz virar: ele para e continua encarando o alvo.
            var direction = blocked && !jump ? 0 : towards;
            return new EnemyIntent(EnemyState.Chase, direction, _profile.ChaseSpeed, towards, jump, false);
        }

        private EnemyIntent ReturnToAnchor(in EnemySenses senses)
        {
            var offset = senses.SignedAnchorOffsetX;
            if (Math.Abs(offset) <= 0.1f)
            {
                _patrolDirection = _facing;
                Transition(EnemyState.Idle);
                return EnemyIntent.Still(EnemyState.Idle, _facing);
            }

            Transition(EnemyState.Returning);
            var towards = FacingTowards(offset);
            var blocked = BlockedAhead(senses, towards, _profile.TurnsAtLedges);
            var direction = blocked ? 0 : towards;
            return new EnemyIntent(EnemyState.Returning, direction, _profile.PatrolSpeed, towards, false, false);
        }

        private bool IsOutsidePatrolBand(in EnemySenses senses)
        {
            if (_profile.PatrolRange <= 0f)
                return false;

            // Folga de 1 unidade: só "volta pra faixa" quando saiu de verdade,
            // senão ele fica corrigindo posição na borda a cada tick.
            return Math.Abs(senses.PositionX - senses.AnchorX) > _profile.PatrolRange + 1f;
        }

        private EnemyIntent Patrol(in EnemySenses senses, float deltaTime)
        {
            var patrols = _profile.Style != EnemyAggressionStyle.Sentry
                          && _profile.Style != EnemyAggressionStyle.Ambusher
                          && _profile.Style != EnemyAggressionStyle.Charger
                          && _profile.PatrolRange > 0f
                          && _profile.PatrolSpeed > 0f;

            if (!patrols)
            {
                Transition(EnemyState.Idle);
                return EnemyIntent.Still(EnemyState.Idle, _facing);
            }

            if (_pauseTime > 0f)
            {
                Transition(EnemyState.Idle);
                return EnemyIntent.Still(EnemyState.Idle, _facing);
            }

            var offsetFromAnchor = senses.PositionX - senses.AnchorX;
            var reachedEdge = (_patrolDirection > 0 && offsetFromAnchor >= _profile.PatrolRange)
                              || (_patrolDirection < 0 && offsetFromAnchor <= -_profile.PatrolRange);

            // Precipício e parede viram o inimigo mesmo antes da ponta da faixa.
            // É isto que impede o bicho de caminhar para fora do mapa.
            var blocked = BlockedAhead(senses, _patrolDirection, _profile.TurnsAtLedges);

            if (reachedEdge || blocked)
            {
                _patrolDirection = -_patrolDirection;
                _pauseTime = _profile.PatrolPauseSeconds;

                if (_pauseTime > 0f)
                {
                    Transition(EnemyState.Idle);
                    return EnemyIntent.Still(EnemyState.Idle, _patrolDirection);
                }
            }

            Transition(EnemyState.Patrol);
            return new EnemyIntent(EnemyState.Patrol, _patrolDirection, _profile.PatrolSpeed,
                                   _patrolDirection, false, false);
        }

        /// <summary>
        /// Há obstáculo na direção pedida? Só conta quando o sensor aponta para o lado
        /// em que ele vai andar — os sentidos são medidos na direção que ele encara.
        /// </summary>
        private bool BlockedAhead(in EnemySenses senses, int direction, bool respectLedges)
        {
            if (direction == 0 || senses.Facing != direction)
                return false;

            if (_profile.TurnsAtWalls && senses.WallAhead)
                return true;

            return respectLedges && senses.LedgeAhead && senses.IsGrounded;
        }

        private static int FacingTowards(float offset) => offset >= 0f ? 1 : -1;

        private void Transition(EnemyState next)
        {
            if (_state == next)
                return;

            _state = next;
            _stateTime = 0f;
        }
    }
}
