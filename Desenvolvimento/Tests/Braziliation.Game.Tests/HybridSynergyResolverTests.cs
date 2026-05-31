using System.Collections.Generic;
using Braziliation.Build;
using Braziliation.Crafting;
using Xunit;

namespace Braziliation.Game.Tests;

public sealed class HybridSynergyResolverTests
{
    private readonly HybridSynergyResolver _sut = new();

    // ── Helpers ───────────────────────────────────────────────────────────────

    private static ItemComponent Item(string id, PillarType pillar) => new()
    {
        Id     = id,
        Pillar = pillar,
        Stats  = new Dictionary<string, float>()
    };

    private static BuildState StateWith(params ItemComponent[] items)
    {
        // Distribui os itens em receptáculos separados (um por item) para simular build real.
        var receptacles = new List<ReceptacleData>();
        foreach (var item in items)
        {
            receptacles.Add(new ReceptacleData
            {
                Pillar = item.Pillar,
                Slots  = new List<SlotData> { new SlotData { AcceptedType = item.Pillar, EquippedItem = item } }
            });
        }
        return new BuildState { Receptacles = receptacles };
    }

    // ── Estado vazio ──────────────────────────────────────────────────────────

    [Fact]
    public void GetActiveHybridEffects_EmptyBuild_ReturnsEmpty()
    {
        var result = _sut.GetActiveHybridEffects(new BuildState());

        Assert.Empty(result);
    }

    [Fact]
    public void HasHybridSynergy_EmptyBuild_ReturnsFalse()
    {
        Assert.False(_sut.HasHybridSynergy(new BuildState()));
    }

    // ── Pilares iguais — sem sinergia ─────────────────────────────────────────

    [Theory]
    [InlineData(PillarType.Mechanical)]
    [InlineData(PillarType.Mystical)]
    [InlineData(PillarType.Biological)]
    public void GetActiveHybridEffects_SamePillarItems_ReturnsEmpty(PillarType pillar)
    {
        var state = StateWith(Item("a", pillar), Item("b", pillar));

        Assert.Empty(_sut.GetActiveHybridEffects(state));
    }

    [Theory]
    [InlineData(PillarType.Mechanical)]
    [InlineData(PillarType.Mystical)]
    [InlineData(PillarType.Biological)]
    public void HasHybridSynergy_SamePillarItems_ReturnsFalse(PillarType pillar)
    {
        var state = StateWith(Item("a", pillar), Item("b", pillar));

        Assert.False(_sut.HasHybridSynergy(state));
    }

    // ── Pilares diferentes — sinergia detectada (tabela populada após Opção B) ─

    [Fact]
    public void GetActiveHybridEffects_MechanicalBiological_ReturnsPrótesisViva()
    {
        var state = StateWith(
            Item("gear",   PillarType.Mechanical),
            Item("fungus", PillarType.Biological));

        var result = _sut.GetActiveHybridEffects(state);

        Assert.Contains("PrótesisViva", result);
    }

    [Fact]
    public void GetActiveHybridEffects_BiologicalMystical_ReturnsMutaçãoArcana()
    {
        var state = StateWith(
            Item("fungus", PillarType.Biological),
            Item("rune",   PillarType.Mystical));

        var result = _sut.GetActiveHybridEffects(state);

        Assert.Contains("MutaçãoArcana", result);
    }

    [Fact]
    public void GetActiveHybridEffects_MechanicalMystical_ReturnsArmaduraEncantada()
    {
        var state = StateWith(
            Item("gear", PillarType.Mechanical),
            Item("rune", PillarType.Mystical));

        var result = _sut.GetActiveHybridEffects(state);

        Assert.Contains("ArmaduraEncantada", result);
    }

    [Fact]
    public void HasHybridSynergy_DifferentPillarItems_ReturnsTrue()
    {
        var state = StateWith(
            Item("gear", PillarType.Mechanical),
            Item("rune", PillarType.Mystical));

        Assert.True(_sut.HasHybridSynergy(state));
    }

    // ── Simetria da chave ────────────────────────────────────────────────────

    [Fact]
    public void GetActiveHybridEffects_PairOrderDoesNotMatter_SameSynergy()
    {
        // (Mechanical, Biological) e (Biological, Mechanical) devem retornar o mesmo efeito
        var stateAB = StateWith(Item("gear",   PillarType.Mechanical), Item("fungus", PillarType.Biological));
        var stateBA = StateWith(Item("fungus", PillarType.Biological), Item("gear",   PillarType.Mechanical));

        var resultAB = _sut.GetActiveHybridEffects(stateAB);
        var resultBA = _sut.GetActiveHybridEffects(stateBA);

        Assert.Equal(resultAB, resultBA);
    }

    // ── Build completa com todos os pilares ───────────────────────────────────

    [Fact]
    public void GetActiveHybridEffects_AllThreePillars_ReturnsAllThreeSynergies()
    {
        var state = StateWith(
            Item("gear",   PillarType.Mechanical),
            Item("rune",   PillarType.Mystical),
            Item("fungus", PillarType.Biological));

        var result = _sut.GetActiveHybridEffects(state);

        Assert.Contains("PrótesisViva",     result);
        Assert.Contains("MutaçãoArcana",    result);
        Assert.Contains("ArmaduraEncantada", result);
        Assert.Equal(3, result.Count);
    }

    [Fact]
    public void GetActiveHybridEffects_NoDuplicateEffects_WhenMultipleItemsSamePair()
    {
        // Dois itens Mechanical + um Mystical → ArmaduraEncantada deve aparecer apenas 1x
        var state = StateWith(
            Item("gear_a", PillarType.Mechanical),
            Item("gear_b", PillarType.Mechanical),
            Item("rune",   PillarType.Mystical));

        var result = _sut.GetActiveHybridEffects(state);

        var count = result.FindAll(e => e == "ArmaduraEncantada").Count;
        Assert.Equal(1, count);
    }
}
