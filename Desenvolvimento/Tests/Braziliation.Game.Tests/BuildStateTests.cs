using System.Collections.Generic;
using Braziliation.Build;
using Braziliation.Crafting;
using Xunit;

namespace Braziliation.Game.Tests;

public sealed class BuildStateTests
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private static ItemComponent Item(string id, PillarType pillar) => new()
    {
        Id          = id,
        DisplayName = $"Display_{id}",
        Lore        = $"Lore_{id}",
        Pillar      = pillar,
        Stats       = new Dictionary<string, float>()
    };

    private static ReceptacleData Receptacle(PillarType pillar, params ItemComponent?[] items)
    {
        var slots = new List<SlotData>();
        foreach (var item in items)
            slots.Add(new SlotData { AcceptedType = pillar, EquippedItem = item });

        return new ReceptacleData { Pillar = pillar, Slots = slots };
    }

    // ── Defaults ─────────────────────────────────────────────────────────────

    [Fact]
    public void Receptacles_EmptyByDefault()
    {
        Assert.Empty(new BuildState().Receptacles);
    }

    [Fact]
    public void ActiveAbilities_EmptyByDefault()
    {
        Assert.Empty(new BuildState().ActiveAbilities);
    }

    [Fact]
    public void Resistances_EmptyByDefault()
    {
        Assert.Empty(new BuildState().Resistances);
    }

    [Fact]
    public void UnlockedExplorationFlags_EmptyByDefault()
    {
        Assert.Empty(new BuildState().UnlockedExplorationFlags);
    }

    // ── GetEquippedItems ──────────────────────────────────────────────────────

    [Fact]
    public void GetEquippedItems_NoReceptacles_ReturnsEmpty()
    {
        Assert.Empty(new BuildState().GetEquippedItems());
    }

    [Fact]
    public void GetEquippedItems_AllSlotsEmpty_ReturnsEmpty()
    {
        var state = new BuildState
        {
            Receptacles = new List<ReceptacleData>
            {
                Receptacle(PillarType.Mechanical, (ItemComponent?)null),
                Receptacle(PillarType.Mystical,   (ItemComponent?)null),
            }
        };

        Assert.Empty(state.GetEquippedItems());
    }

    [Fact]
    public void GetEquippedItems_SingleEquippedItem_ReturnsThatItem()
    {
        var item  = Item("gear_01", PillarType.Mechanical);
        var state = new BuildState
        {
            Receptacles = new List<ReceptacleData> { Receptacle(PillarType.Mechanical, item) }
        };

        var result = state.GetEquippedItems();

        Assert.Single(result);
        Assert.Equal("gear_01", result[0].Id);
    }

    [Fact]
    public void GetEquippedItems_MixedSlots_ReturnsOnlyEquipped()
    {
        var item  = Item("rune_01", PillarType.Mystical);
        var state = new BuildState
        {
            Receptacles = new List<ReceptacleData>
            {
                Receptacle(PillarType.Mystical, item, (ItemComponent?)null)
            }
        };

        var result = state.GetEquippedItems();

        Assert.Single(result);
        Assert.Equal("rune_01", result[0].Id);
    }

    [Fact]
    public void GetEquippedItems_MultipleReceptaclesWithItems_ReturnsAll()
    {
        var gear   = Item("gear_01",   PillarType.Mechanical);
        var rune   = Item("rune_01",   PillarType.Mystical);
        var fungus = Item("fungus_01", PillarType.Biological);

        var state = new BuildState
        {
            Receptacles = new List<ReceptacleData>
            {
                Receptacle(PillarType.Mechanical, gear),
                Receptacle(PillarType.Mystical,   rune),
                Receptacle(PillarType.Biological, fungus),
            }
        };

        Assert.Equal(3, state.GetEquippedItems().Count);
    }

    [Fact]
    public void GetEquippedItems_MultipleSlotsSameReceptacle_ReturnsAllEquipped()
    {
        var a     = Item("gear_a", PillarType.Mechanical);
        var b     = Item("gear_b", PillarType.Mechanical);
        var state = new BuildState
        {
            Receptacles = new List<ReceptacleData> { Receptacle(PillarType.Mechanical, a, b) }
        };

        Assert.Equal(2, state.GetEquippedItems().Count);
    }

    // ── HasAbility ────────────────────────────────────────────────────────────

    [Fact]
    public void HasAbility_AbilityPresent_ReturnsTrue()
    {
        var state = new BuildState { ActiveAbilities = new HashSet<string> { "NightVision" } };

        Assert.True(state.HasAbility("NightVision"));
    }

    [Fact]
    public void HasAbility_AbilityAbsent_ReturnsFalse()
    {
        Assert.False(new BuildState().HasAbility("NightVision"));
    }

    [Fact]
    public void HasAbility_MultipleAbilities_ReturnsTrueForEach()
    {
        var state = new BuildState
        {
            ActiveAbilities = new HashSet<string> { "NightVision", "WaterBreathing", "HiddenPaths" }
        };

        Assert.True(state.HasAbility("NightVision"));
        Assert.True(state.HasAbility("WaterBreathing"));
        Assert.True(state.HasAbility("HiddenPaths"));
        Assert.False(state.HasAbility("UnknownAbility"));
    }

    // ── Resistances ──────────────────────────────────────────────────────────

    [Fact]
    public void Resistances_CanBeSetAndRead()
    {
        var state = new BuildState
        {
            Resistances = new Dictionary<string, float> { ["Poison"] = 0.5f, ["Fire"] = 0.25f }
        };

        Assert.Equal(0.5f,  state.Resistances["Poison"]);
        Assert.Equal(0.25f, state.Resistances["Fire"]);
    }

    // ── UnlockedExplorationFlags ──────────────────────────────────────────────

    [Fact]
    public void UnlockedExplorationFlags_CanAddAndCheck()
    {
        var state = new BuildState();
        state.UnlockedExplorationFlags.Add("NightVision");

        Assert.Contains("NightVision", state.UnlockedExplorationFlags);
        Assert.DoesNotContain("HiddenPaths", state.UnlockedExplorationFlags);
    }
}
