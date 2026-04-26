using Braziliation.SaveSystem;
using Xunit;

namespace Braziliation.Game.Tests;

public sealed class SaveGameServiceTests
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private static (SaveGameService svc, InMemorySaveStorage storage) CreateSut()
    {
        var storage = new InMemorySaveStorage();
        return (new SaveGameService(storage), storage);
    }

    private static SaveSlot BuildSlot(int index) => new()
    {
        SlotIndex = index,
        PlayerName = $"Player{index}",
        PlaytimeSeconds = index * 100.0,
        LastSaved = new DateTimeOffset(2024, 1, 1, 0, 0, 0, TimeSpan.Zero),
        SceneName = "Level_01",
        CheckpointId = index,
    };

    // ── Construction guard ────────────────────────────────────────────────────

    [Fact]
    public void Constructor_WithNullStorage_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => new SaveGameService(null!));
    }

    // ── Save / Load consistency ───────────────────────────────────────────────

    [Fact]
    public void Save_ThenLoad_ReturnsSameData()
    {
        var (svc, _) = CreateSut();
        var original = BuildSlot(0);

        svc.Save(original);
        var loaded = svc.Load(0);

        Assert.NotNull(loaded);
        Assert.Equal(original.SlotIndex, loaded.SlotIndex);
        Assert.Equal(original.PlayerName, loaded.PlayerName);
        Assert.Equal(original.PlaytimeSeconds, loaded.PlaytimeSeconds);
        Assert.Equal(original.LastSaved, loaded.LastSaved);
        Assert.Equal(original.SceneName, loaded.SceneName);
        Assert.Equal(original.CheckpointId, loaded.CheckpointId);
    }

    [Fact]
    public void Save_OverwritesExistingSlot()
    {
        var (svc, _) = CreateSut();
        svc.Save(BuildSlot(0));

        var updated = new SaveSlot
        {
            SlotIndex = 0,
            PlayerName = "UpdatedName",
            PlaytimeSeconds = 9999.0,
            LastSaved = new DateTimeOffset(2025, 1, 1, 0, 0, 0, TimeSpan.Zero),
            SceneName = "Level_02",
            CheckpointId = 10,
        };
        svc.Save(updated);

        var loaded = svc.Load(0);
        Assert.NotNull(loaded);
        Assert.Equal("UpdatedName", loaded.PlayerName);
        Assert.Equal(9999.0, loaded.PlaytimeSeconds);
    }

    // ── Missing slot ──────────────────────────────────────────────────────────

    [Fact]
    public void Load_NonexistentSlot_ReturnsNull()
    {
        var (svc, _) = CreateSut();
        Assert.Null(svc.Load(99));
    }

    // ── Corrupted save handling ───────────────────────────────────────────────

    [Fact]
    public void Load_CorruptedJson_ReturnsNull()
    {
        var (svc, storage) = CreateSut();
        storage.Write(0, "{ not valid json !!!"u8.ToArray());
        Assert.Null(svc.Load(0));
    }

    [Fact]
    public void Load_EmptyBytes_ReturnsNull()
    {
        var (svc, storage) = CreateSut();
        storage.Write(0, Array.Empty<byte>());
        Assert.Null(svc.Load(0));
    }

    [Fact]
    public void Load_NullFromStorage_ReturnsNull()
    {
        var (svc, _) = CreateSut();
        Assert.Null(svc.Load(0));
    }

    // ── Multiple slots isolation ──────────────────────────────────────────────

    [Fact]
    public void MultipleSlots_AreIsolated()
    {
        var (svc, _) = CreateSut();
        svc.Save(BuildSlot(0));
        svc.Save(BuildSlot(1));

        var loaded0 = svc.Load(0);
        var loaded1 = svc.Load(1);

        Assert.NotNull(loaded0);
        Assert.NotNull(loaded1);
        Assert.Equal("Player0", loaded0.PlayerName);
        Assert.Equal("Player1", loaded1.PlayerName);
    }

    [Fact]
    public void MultipleSlots_DeletingOneDoesNotAffectOthers()
    {
        var (svc, _) = CreateSut();
        svc.Save(BuildSlot(0));
        svc.Save(BuildSlot(1));
        svc.Save(BuildSlot(2));

        svc.DeleteSlot(1);

        Assert.True(svc.SlotExists(0));
        Assert.False(svc.SlotExists(1));
        Assert.True(svc.SlotExists(2));
    }

    // ── SlotExists ────────────────────────────────────────────────────────────

    [Fact]
    public void SlotExists_BeforeSave_ReturnsFalse()
    {
        var (svc, _) = CreateSut();
        Assert.False(svc.SlotExists(0));
    }

    [Fact]
    public void SlotExists_AfterSave_ReturnsTrue()
    {
        var (svc, _) = CreateSut();
        svc.Save(BuildSlot(0));
        Assert.True(svc.SlotExists(0));
    }

    // ── DeleteSlot ────────────────────────────────────────────────────────────

    [Fact]
    public void DeleteSlot_AfterSave_SlotNoLongerExists()
    {
        var (svc, _) = CreateSut();
        svc.Save(BuildSlot(0));
        svc.DeleteSlot(0);

        Assert.False(svc.SlotExists(0));
        Assert.Null(svc.Load(0));
    }

    // ── Null guard ────────────────────────────────────────────────────────────

    [Fact]
    public void Save_WithNullSlot_ThrowsArgumentNullException()
    {
        var (svc, _) = CreateSut();
        Assert.Throws<ArgumentNullException>(() => svc.Save(null!));
    }

    // ── Serialization integrity (Steam Cloud determinism) ─────────────────────

    [Fact]
    public void Save_SameSlot_ProducesDeterministicBytes()
    {
        var slot = new SaveSlot
        {
            SlotIndex = 0,
            PlayerName = "Deterministic",
            PlaytimeSeconds = 42.0,
            LastSaved = new DateTimeOffset(2024, 6, 1, 12, 0, 0, TimeSpan.Zero),
            SceneName = "Level_01",
            CheckpointId = 5,
        };

        var storageA = new InMemorySaveStorage();
        var storageB = new InMemorySaveStorage();
        new SaveGameService(storageA).Save(slot);
        new SaveGameService(storageB).Save(slot);

        Assert.True(storageA.Read(0)!.SequenceEqual(storageB.Read(0)!));
    }
}
