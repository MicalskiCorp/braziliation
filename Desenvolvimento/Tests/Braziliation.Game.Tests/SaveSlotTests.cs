using System.Text.Json;
using Braziliation.SaveSystem;
using Xunit;

namespace Braziliation.Game.Tests;

public sealed class SaveSlotTests
{
    // ── Defaults ──────────────────────────────────────────────────────────────

    [Fact]
    public void Constructor_DefaultSlotIndex_IsZero()
    {
        Assert.Equal(0, new SaveSlot().SlotIndex);
    }

    [Fact]
    public void Constructor_DefaultPlayerName_IsEmpty()
    {
        Assert.Equal(string.Empty, new SaveSlot().PlayerName);
    }

    [Fact]
    public void Constructor_DefaultPlaytimeSeconds_IsZero()
    {
        Assert.Equal(0d, new SaveSlot().PlaytimeSeconds);
    }

    [Fact]
    public void Constructor_DefaultSceneName_IsEmpty()
    {
        Assert.Equal(string.Empty, new SaveSlot().SceneName);
    }

    [Fact]
    public void Constructor_DefaultCheckpointId_IsZero()
    {
        Assert.Equal(0, new SaveSlot().CheckpointId);
    }

    // ── Property assignment ───────────────────────────────────────────────────

    [Fact]
    public void SlotIndex_CanBeSetToAnyInt()
    {
        var slot = new SaveSlot { SlotIndex = 99 };
        Assert.Equal(99, slot.SlotIndex);
    }

    [Fact]
    public void PlayerName_WithSpecialCharacters_IsPreserved()
    {
        const string name = "José & Çãõ \"Player\" <1>";
        var slot = new SaveSlot { PlayerName = name };
        Assert.Equal(name, slot.PlayerName);
    }

    [Fact]
    public void PlaytimeSeconds_CanBeVeryLarge()
    {
        var slot = new SaveSlot { PlaytimeSeconds = double.MaxValue };
        Assert.Equal(double.MaxValue, slot.PlaytimeSeconds);
    }

    // ── JSON serialization roundtrip ──────────────────────────────────────────

    [Fact]
    public void Serialization_Roundtrip_PreservesAllFields()
    {
        var original = new SaveSlot
        {
            SlotIndex = 2,
            PlayerName = "Heitor",
            PlaytimeSeconds = 3723.5,
            LastSaved = new DateTimeOffset(2024, 6, 15, 10, 30, 0, TimeSpan.Zero),
            SceneName = "Level_01",
            CheckpointId = 3,
        };

        var json = JsonSerializer.Serialize(original);
        var restored = JsonSerializer.Deserialize<SaveSlot>(json);

        Assert.NotNull(restored);
        Assert.Equal(original.SlotIndex, restored.SlotIndex);
        Assert.Equal(original.PlayerName, restored.PlayerName);
        Assert.Equal(original.PlaytimeSeconds, restored.PlaytimeSeconds);
        Assert.Equal(original.LastSaved, restored.LastSaved);
        Assert.Equal(original.SceneName, restored.SceneName);
        Assert.Equal(original.CheckpointId, restored.CheckpointId);
    }

    [Fact]
    public void Serialization_EmptyStrings_RoundtripCorrectly()
    {
        var original = new SaveSlot { SlotIndex = 0, PlayerName = string.Empty, SceneName = string.Empty };
        var json = JsonSerializer.Serialize(original);
        var restored = JsonSerializer.Deserialize<SaveSlot>(json);
        Assert.NotNull(restored);
        Assert.Equal(string.Empty, restored.PlayerName);
        Assert.Equal(string.Empty, restored.SceneName);
    }

    [Fact]
    public void Serialization_SameInput_ProducesDeterministicOutput()
    {
        var slot = new SaveSlot
        {
            SlotIndex = 1,
            PlayerName = "Luana",
            PlaytimeSeconds = 100.0,
            LastSaved = new DateTimeOffset(2024, 1, 1, 0, 0, 0, TimeSpan.Zero),
            SceneName = "Menu",
            CheckpointId = 0,
        };

        var json1 = JsonSerializer.Serialize(slot);
        var json2 = JsonSerializer.Serialize(slot);

        Assert.Equal(json1, json2);
    }

    // ── Slot isolation ────────────────────────────────────────────────────────

    [Fact]
    public void TwoSlots_WithDifferentIndices_AreIndependentObjects()
    {
        var slot0 = new SaveSlot { SlotIndex = 0, PlayerName = "Slot0" };
        var slot1 = new SaveSlot { SlotIndex = 1, PlayerName = "Slot1" };

        Assert.NotEqual(slot0.SlotIndex, slot1.SlotIndex);
        Assert.NotEqual(slot0.PlayerName, slot1.PlayerName);
    }
}
