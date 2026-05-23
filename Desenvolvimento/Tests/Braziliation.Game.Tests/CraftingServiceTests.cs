using System.Collections.Generic;
using Braziliation.Crafting;
using Xunit;

namespace Braziliation.Game.Tests;

public sealed class CraftingServiceTests
{
    private readonly CraftingService _sut = new();

    // ── Helpers ───────────────────────────────────────────────────────────────

    private static ItemComponent Item(string id, PillarType pillar,
        Dictionary<string, float>? stats = null) => new()
    {
        Id          = id,
        DisplayName = $"Display_{id}",
        Lore        = $"Lore_{id}",
        Pillar      = pillar,
        Stats       = stats ?? new Dictionary<string, float>()
    };

    private static CraftingRecipe Recipe(ItemComponent a, ItemComponent b, ItemComponent result) =>
        new() { InputA = a, InputB = b, Result = result };

    /// <summary>Substituição de System.Random com valor fixo para testes determinísticos.</summary>
    private sealed class FixedRandom : System.Random
    {
        private readonly int _value;
        public FixedRandom(int value) : base() => _value = value;
        public override int Next(int minValue, int maxValue) => _value;
    }

    // ── Craft ─────────────────────────────────────────────────────────────────

    [Fact]
    public void Craft_MatchingInputsAB_ReturnsRecipeResult()
    {
        var a        = Item("gear", PillarType.Mechanical);
        var b        = Item("rune", PillarType.Mystical);
        var expected = Item("hybrid_item", PillarType.Mechanical);
        var recipes  = new List<CraftingRecipe> { Recipe(a, b, expected) };

        var result = _sut.Craft(a, b, recipes);

        Assert.Equal(expected.Id, result!.Id);
    }

    [Fact]
    public void Craft_SymmetricInputsBA_ReturnsRecipeResult()
    {
        var a        = Item("gear", PillarType.Mechanical);
        var b        = Item("rune", PillarType.Mystical);
        var expected = Item("hybrid_item", PillarType.Biological);
        var recipes  = new List<CraftingRecipe> { Recipe(a, b, expected) };

        // ordem invertida deve produzir o mesmo resultado
        var result = _sut.Craft(b, a, recipes);

        Assert.Equal(expected.Id, result!.Id);
    }

    [Fact]
    public void Craft_NoMatchingRecipe_ReturnsNull()
    {
        var a       = Item("gear", PillarType.Mechanical);
        var b       = Item("rune", PillarType.Mystical);
        var other   = Item("fungus", PillarType.Biological);
        var recipes = new List<CraftingRecipe> { Recipe(a, other, Item("x", PillarType.Mechanical)) };

        var result = _sut.Craft(a, b, recipes);

        Assert.Null(result);
    }

    [Fact]
    public void Craft_EmptyRecipeList_ReturnsNull()
    {
        var result = _sut.Craft(
            Item("gear", PillarType.Mechanical),
            Item("rune", PillarType.Mystical),
            new List<CraftingRecipe>());

        Assert.Null(result);
    }

    [Fact]
    public void Craft_MultipleMatchingRecipes_ReturnsFirstMatch()
    {
        var a      = Item("gear", PillarType.Mechanical);
        var b      = Item("rune", PillarType.Mystical);
        var first  = Item("first_result", PillarType.Mechanical);
        var second = Item("second_result", PillarType.Biological);
        var recipes = new List<CraftingRecipe>
        {
            Recipe(a, b, first),
            Recipe(a, b, second)
        };

        var result = _sut.Craft(a, b, recipes);

        Assert.Equal("first_result", result!.Id);
    }

    // ── ValidateSlotCompatibility ─────────────────────────────────────────────

    [Theory]
    [InlineData(PillarType.Mechanical)]
    [InlineData(PillarType.Mystical)]
    [InlineData(PillarType.Biological)]
    public void ValidateSlotCompatibility_MatchingPillar_ReturnsTrue(PillarType pillar)
    {
        var item = Item("x", pillar);
        var slot = new SlotData { AcceptedType = pillar };

        Assert.True(_sut.ValidateSlotCompatibility(item, slot));
    }

    [Theory]
    [InlineData(PillarType.Mechanical, PillarType.Mystical)]
    [InlineData(PillarType.Mechanical, PillarType.Biological)]
    [InlineData(PillarType.Mystical,   PillarType.Mechanical)]
    [InlineData(PillarType.Mystical,   PillarType.Biological)]
    [InlineData(PillarType.Biological, PillarType.Mechanical)]
    [InlineData(PillarType.Biological, PillarType.Mystical)]
    public void ValidateSlotCompatibility_MismatchedPillar_ReturnsFalse(
        PillarType itemPillar, PillarType slotPillar)
    {
        var item = Item("x", itemPillar);
        var slot = new SlotData { AcceptedType = slotPillar };

        Assert.False(_sut.ValidateSlotCompatibility(item, slot));
    }

    // ── IsHybridCraft ─────────────────────────────────────────────────────────

    [Theory]
    [InlineData(PillarType.Mechanical, PillarType.Mystical)]
    [InlineData(PillarType.Mechanical, PillarType.Biological)]
    [InlineData(PillarType.Mystical,   PillarType.Biological)]
    public void IsHybridCraft_DifferentPillars_ReturnsTrue(PillarType pillarA, PillarType pillarB)
    {
        Assert.True(_sut.IsHybridCraft(Item("a", pillarA), Item("b", pillarB)));
    }

    [Theory]
    [InlineData(PillarType.Mechanical)]
    [InlineData(PillarType.Mystical)]
    [InlineData(PillarType.Biological)]
    public void IsHybridCraft_SamePillar_ReturnsFalse(PillarType pillar)
    {
        Assert.False(_sut.IsHybridCraft(Item("a", pillar), Item("b", pillar)));
    }

    // ── RollHybridResult ──────────────────────────────────────────────────────

    [Fact]
    public void RollHybridResult_RngReturnsZero_KeepsAPillar()
    {
        var a = Item("a", PillarType.Mechanical);
        var b = Item("b", PillarType.Mystical);

        var result = _sut.RollHybridResult(a, b, new FixedRandom(0));

        Assert.Equal(PillarType.Mechanical, result.Pillar);
    }

    [Fact]
    public void RollHybridResult_RngReturnsOne_UsesBPillar()
    {
        var a = Item("a", PillarType.Mechanical);
        var b = Item("b", PillarType.Mystical);

        var result = _sut.RollHybridResult(a, b, new FixedRandom(1));

        Assert.Equal(PillarType.Mystical, result.Pillar);
    }

    [Fact]
    public void RollHybridResult_AlwaysCopiesMetadataFromB()
    {
        var a = Item("a_id", PillarType.Mechanical);
        var b = Item("b_id", PillarType.Mystical);

        // independentemente do pillar sorteado, Id/DisplayName/Lore vêm de b
        var result = _sut.RollHybridResult(a, b, new FixedRandom(0));

        Assert.Equal(b.Id, result.Id);
        Assert.Equal(b.DisplayName, result.DisplayName);
        Assert.Equal(b.Lore, result.Lore);
    }

    [Fact]
    public void RollHybridResult_StatsIsIndependentCopyFromB()
    {
        var stats = new Dictionary<string, float> { ["attack"] = 5f, ["defense"] = 3f };
        var a = Item("a", PillarType.Mechanical);
        var b = Item("b", PillarType.Mystical, stats);

        var result = _sut.RollHybridResult(a, b, new FixedRandom(0));

        Assert.NotSame(b.Stats, result.Stats);
        Assert.Equal(b.Stats["attack"],  result.Stats["attack"]);
        Assert.Equal(b.Stats["defense"], result.Stats["defense"]);
    }

    [Fact]
    public void RollHybridResult_StatsMutation_DoesNotAffectOriginalB()
    {
        var stats = new Dictionary<string, float> { ["attack"] = 5f };
        var b     = Item("b", PillarType.Mystical, stats);

        var result = _sut.RollHybridResult(Item("a", PillarType.Mechanical), b, new FixedRandom(0));
        result.Stats["attack"] = 999f;

        Assert.Equal(5f, b.Stats["attack"]);
    }
}
