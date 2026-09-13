using System;
using Braziliation.Enemies;
using Xunit;

namespace Braziliation.Game.Tests
{
    public class EnemyBrainTests
    {
        private const float Step = 1f / 50f; // passo de física padrão do Unity

        private static EnemyBehaviorProfile Patroller() => new EnemyBehaviorProfile
        {
            Style = EnemyAggressionStyle.Patroller,
            PatrolSpeed = 2f,
            PatrolRange = 2f,
            PatrolPauseSeconds = 0f,
            ChaseSpeed = 3f,
            DetectRadius = 4f,
            LoseTargetRadius = 6f,
            LeashRadius = 8f,
            ReactionSeconds = 0f,
            AttackRange = 1f,
            AttackWindupSeconds = 0f,
            AttackCooldownSeconds = 1f,
        };

        private static EnemySenses Senses(
            float positionX = 0f,
            float anchorX = 0f,
            bool hasTarget = false,
            float targetX = 0f,
            float? targetDistance = null,
            bool isGrounded = true,
            bool wallAhead = false,
            bool ledgeAhead = false,
            float healthFraction = 1f,
            int facing = 1)
        {
            return new EnemySenses(
                positionX, anchorX, hasTarget, targetX,
                targetDistance ?? Math.Abs(targetX - positionX),
                isGrounded, wallAhead, ledgeAhead, healthFraction, facing);
        }

        // ------------------------------------------------------------------ patrulha
        [Fact]
        public void Patrulha_anda_para_a_direcao_inicial()
        {
            var brain = new EnemyBrain(Patroller());

            var intent = brain.Tick(Senses(), Step);

            Assert.Equal(EnemyState.Patrol, intent.State);
            Assert.Equal(1f, intent.MoveDirection);
            Assert.Equal(2f, intent.Speed);
        }

        [Fact]
        public void Patrulha_inverte_ao_atingir_a_ponta_da_faixa()
        {
            var brain = new EnemyBrain(Patroller());
            brain.Tick(Senses(), Step);

            var intent = brain.Tick(Senses(positionX: 2f), Step);

            Assert.Equal(-1f, intent.MoveDirection);
        }

        [Fact]
        public void Patrulha_nao_ultrapassa_a_faixa_ao_longo_do_tempo()
        {
            // Regressão: com os pontos de patrulha presos ao próprio inimigo, ele
            // andava para sempre em uma direção e caía do mapa.
            var brain = new EnemyBrain(Patroller());
            var x = 0f;
            var min = 0f;
            var max = 0f;

            for (var i = 0; i < 2000; i++)
            {
                var intent = brain.Tick(Senses(positionX: x, facing: brain.Facing), Step);
                x += intent.VelocityX * Step;
                min = Math.Min(min, x);
                max = Math.Max(max, x);
            }

            Assert.InRange(max, 1.9f, 2.2f);
            Assert.InRange(min, -2.2f, -1.9f);
        }

        [Fact]
        public void Patrulha_vira_ao_detectar_precipicio_antes_da_ponta()
        {
            var brain = new EnemyBrain(Patroller());
            brain.Tick(Senses(), Step);

            var intent = brain.Tick(Senses(positionX: 0.5f, ledgeAhead: true, facing: 1), Step);

            Assert.Equal(-1f, intent.MoveDirection);
        }

        [Fact]
        public void Patrulha_vira_ao_detectar_parede()
        {
            var brain = new EnemyBrain(Patroller());
            brain.Tick(Senses(), Step);

            var intent = brain.Tick(Senses(positionX: 0.5f, wallAhead: true, facing: 1), Step);

            Assert.Equal(-1f, intent.MoveDirection);
        }

        [Fact]
        public void Precipicio_no_ar_nao_faz_virar()
        {
            // Pulando/caindo, o sensor de chão à frente não vale.
            var brain = new EnemyBrain(Patroller());
            brain.Tick(Senses(), Step);

            var intent = brain.Tick(Senses(positionX: 0.5f, ledgeAhead: true, isGrounded: false, facing: 1), Step);

            Assert.Equal(1f, intent.MoveDirection);
        }

        [Fact]
        public void Patrulha_pausa_na_ponta_quando_o_perfil_pede()
        {
            var profile = Patroller();
            profile.PatrolPauseSeconds = 0.5f;
            var brain = new EnemyBrain(profile);
            brain.Tick(Senses(), Step);

            var atEdge = brain.Tick(Senses(positionX: 2f), Step);

            Assert.Equal(EnemyState.Idle, atEdge.State);
            Assert.Equal(0f, atEdge.MoveDirection);
        }

        // -------------------------------------------------------------- perseguição
        [Fact]
        public void Persegue_alvo_dentro_do_raio_de_deteccao()
        {
            var brain = new EnemyBrain(Patroller());

            var intent = brain.Tick(Senses(hasTarget: true, targetX: 3f), Step);

            Assert.Equal(EnemyState.Chase, intent.State);
            Assert.Equal(1f, intent.MoveDirection);
            Assert.Equal(3f, intent.Speed);
        }

        [Fact]
        public void Espera_o_tempo_de_reacao_antes_de_perseguir()
        {
            var profile = Patroller();
            profile.ReactionSeconds = 0.2f;
            var brain = new EnemyBrain(profile);

            var spotted = brain.Tick(Senses(hasTarget: true, targetX: 3f), Step);
            Assert.Equal(EnemyState.Alert, spotted.State);
            Assert.Equal(0f, spotted.MoveDirection);

            for (var i = 0; i < 12; i++)
                brain.Tick(Senses(hasTarget: true, targetX: 3f), Step);

            Assert.Equal(EnemyState.Chase, brain.State);
        }

        [Fact]
        public void Histerese_mantem_o_alvo_entre_o_raio_de_deteccao_e_o_de_perda()
        {
            var brain = new EnemyBrain(Patroller());
            brain.Tick(Senses(hasTarget: true, targetX: 3f), Step);

            // 5 unidades: fora do DetectRadius (4) mas dentro do LoseTargetRadius (6)
            var intent = brain.Tick(Senses(hasTarget: true, targetX: 5f), Step);

            Assert.True(brain.HasEngagedTarget);
            Assert.Equal(EnemyState.Chase, intent.State);
        }

        [Fact]
        public void Desiste_do_alvo_alem_do_raio_de_perda()
        {
            var brain = new EnemyBrain(Patroller());
            brain.Tick(Senses(hasTarget: true, targetX: 3f), Step);

            brain.Tick(Senses(hasTarget: true, targetX: 7f), Step);

            Assert.False(brain.HasEngagedTarget);
        }

        [Fact]
        public void Coleira_faz_voltar_para_a_ancora()
        {
            var brain = new EnemyBrain(Patroller());
            brain.Tick(Senses(hasTarget: true, targetX: 3f), Step);

            // Longe demais da âncora: solta o alvo e volta.
            var intent = brain.Tick(Senses(positionX: 9f, anchorX: 0f, hasTarget: true, targetX: 10f), Step);

            Assert.False(brain.HasEngagedTarget);
            Assert.Equal(EnemyState.Returning, intent.State);
            Assert.Equal(-1f, intent.MoveDirection);
        }

        // ------------------------------------------------------------------- ataque
        [Fact]
        public void Ataca_quando_o_alvo_entra_no_alcance()
        {
            var brain = new EnemyBrain(Patroller());

            var intent = brain.Tick(Senses(hasTarget: true, targetX: 0.5f), Step);

            Assert.Equal(EnemyState.Attack, intent.State);
            Assert.True(intent.Attack);
            Assert.Equal(0f, intent.MoveDirection);
        }

        [Fact]
        public void Ataque_respeita_o_cooldown()
        {
            var brain = new EnemyBrain(Patroller());
            var first = brain.Tick(Senses(hasTarget: true, targetX: 0.5f), Step);
            Assert.True(first.Attack);

            var pulses = 0;
            for (var i = 0; i < 40; i++)
            {
                if (brain.Tick(Senses(hasTarget: true, targetX: 0.5f), Step).Attack)
                    pulses++;
            }

            // 40 ticks = 0,8s, abaixo do cooldown de 1s
            Assert.Equal(0, pulses);
        }

        [Fact]
        public void Ataque_com_preparacao_so_libera_o_pulso_no_fim()
        {
            var profile = Patroller();
            profile.AttackWindupSeconds = 0.2f;
            var brain = new EnemyBrain(profile);

            var start = brain.Tick(Senses(hasTarget: true, targetX: 0.5f), Step);
            Assert.Equal(EnemyState.Attack, start.State);
            Assert.False(start.Attack);

            var pulses = 0;
            for (var i = 0; i < 12; i++)
            {
                if (brain.Tick(Senses(hasTarget: true, targetX: 0.5f), Step).Attack)
                    pulses++;
            }

            Assert.Equal(1, pulses);
        }

        // ------------------------------------------------------------------ estilos
        [Fact]
        public void Sentinela_encara_o_alvo_mas_nao_sai_do_posto()
        {
            var profile = Patroller();
            profile.Style = EnemyAggressionStyle.Sentry;
            var brain = new EnemyBrain(profile);

            var intent = brain.Tick(Senses(hasTarget: true, targetX: 3f), Step);

            Assert.Equal(0f, intent.MoveDirection);
            Assert.Equal(1, intent.Facing);
        }

        [Fact]
        public void Sentinela_nao_patrulha()
        {
            var profile = Patroller();
            profile.Style = EnemyAggressionStyle.Sentry;
            var brain = new EnemyBrain(profile);

            var intent = brain.Tick(Senses(), Step);

            Assert.Equal(EnemyState.Idle, intent.State);
            Assert.Equal(0f, intent.MoveDirection);
        }

        [Fact]
        public void Skirmisher_recua_quando_o_alvo_chega_perto_demais()
        {
            var profile = Patroller();
            profile.Style = EnemyAggressionStyle.Skirmisher;
            profile.PreferredDistance = 3f;
            profile.AttackRange = 0.5f;
            var brain = new EnemyBrain(profile);

            var intent = brain.Tick(Senses(hasTarget: true, targetX: 1f), Step);

            Assert.Equal(EnemyState.Reposition, intent.State);
            Assert.Equal(-1f, intent.MoveDirection);
            // Recua sem dar as costas
            Assert.Equal(1, intent.Facing);
        }

        [Fact]
        public void Skirmisher_aproxima_quando_o_alvo_esta_longe_demais()
        {
            var profile = Patroller();
            profile.Style = EnemyAggressionStyle.Skirmisher;
            profile.PreferredDistance = 2f;
            var brain = new EnemyBrain(profile);

            var intent = brain.Tick(Senses(hasTarget: true, targetX: 3.5f), Step);

            Assert.Equal(EnemyState.Chase, intent.State);
            Assert.Equal(1f, intent.MoveDirection);
        }

        [Fact]
        public void Emboscador_ignora_o_alvo_ate_ele_chegar_perto()
        {
            var profile = Patroller();
            profile.Style = EnemyAggressionStyle.Ambusher;
            var brain = new EnemyBrain(profile);

            // Raio efetivo do emboscador = metade do DetectRadius (4) = 2
            var longe = brain.Tick(Senses(hasTarget: true, targetX: 3f), Step);
            Assert.False(brain.HasEngagedTarget);
            Assert.Equal(EnemyState.Idle, longe.State);

            brain.Tick(Senses(hasTarget: true, targetX: 1.8f), Step);
            Assert.True(brain.HasEngagedTarget);
        }

        // --------------------------------------------------------------------- fuga
        [Fact]
        public void Foge_do_alvo_com_vida_baixa()
        {
            var profile = Patroller();
            profile.FleeHealthFraction = 0.25f;
            var brain = new EnemyBrain(profile);

            var intent = brain.Tick(Senses(hasTarget: true, targetX: 2f, healthFraction: 0.2f), Step);

            Assert.Equal(EnemyState.Flee, intent.State);
            Assert.Equal(-1f, intent.MoveDirection);
        }

        [Fact]
        public void Nao_foge_quando_o_perfil_nao_permite()
        {
            var brain = new EnemyBrain(Patroller());

            var intent = brain.Tick(Senses(hasTarget: true, targetX: 2f, healthFraction: 0.05f), Step);

            Assert.NotEqual(EnemyState.Flee, intent.State);
        }

        // ------------------------------------------------------------------- morte
        [Fact]
        public void Morto_para_de_agir()
        {
            var brain = new EnemyBrain(Patroller());

            var intent = brain.Tick(Senses(hasTarget: true, targetX: 1f, healthFraction: 0f), Step);

            Assert.Equal(EnemyState.Dead, intent.State);
            Assert.Equal(0f, intent.MoveDirection);
            Assert.False(intent.Attack);
        }

        // ------------------------------------------------------------- determinismo
        [Fact]
        public void Mesma_entrada_produz_mesma_saida()
        {
            var a = new EnemyBrain(Patroller());
            var b = new EnemyBrain(Patroller());

            for (var i = 0; i < 500; i++)
            {
                var senses = Senses(positionX: i * 0.01f, hasTarget: i % 3 == 0, targetX: 3f, facing: 1);
                var ia = a.Tick(senses, Step);
                var ib = b.Tick(senses, Step);

                Assert.Equal(ia.State, ib.State);
                Assert.Equal(ia.MoveDirection, ib.MoveDirection);
                Assert.Equal(ia.Attack, ib.Attack);
            }
        }

        [Fact]
        public void Perfil_nulo_e_rejeitado()
        {
            Assert.Throws<ArgumentNullException>(() => new EnemyBrain(null!));
        }
    }
}
