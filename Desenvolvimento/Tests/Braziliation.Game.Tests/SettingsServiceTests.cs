using Braziliation.Settings;
using Xunit;

namespace Braziliation.Game.Tests;

public sealed class SettingsServiceTests
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private static (SettingsService svc, InMemorySettingsStorage storage) CreateSut()
    {
        var storage = new InMemorySettingsStorage();
        return (new SettingsService(storage), storage);
    }

    // ── Construction guard ────────────────────────────────────────────────────

    [Fact]
    public void Constructor_WithNullStorage_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => new SettingsService(null!));
    }

    // ── Save / Load consistency ───────────────────────────────────────────────

    [Fact]
    public void Save_ThenLoad_ReturnsSameSettings()
    {
        var (svc, _) = CreateSut();
        var original = new GameSettings { MasterVolume = 0.75f, MusicVolume = 0.5f, SfxVolume = 0.25f };

        svc.Save(original);
        var loaded = svc.Load();

        Assert.Equal(original.MasterVolume, loaded.MasterVolume);
        Assert.Equal(original.MusicVolume, loaded.MusicVolume);
        Assert.Equal(original.SfxVolume, loaded.SfxVolume);
    }

    [Fact]
    public void Save_ThenLoad_WithZeroVolumes_RoundtripCorrectly()
    {
        var (svc, _) = CreateSut();
        svc.Save(new GameSettings { MasterVolume = 0f, MusicVolume = 0f, SfxVolume = 0f });
        var loaded = svc.Load();
        Assert.Equal(0f, loaded.MasterVolume);
        Assert.Equal(0f, loaded.MusicVolume);
        Assert.Equal(0f, loaded.SfxVolume);
    }

    [Fact]
    public void Save_MultipleTimes_LastSaveWins()
    {
        var (svc, _) = CreateSut();
        svc.Save(new GameSettings { MasterVolume = 0.2f });
        svc.Save(new GameSettings { MasterVolume = 0.9f });
        var loaded = svc.Load();
        Assert.Equal(0.9f, loaded.MasterVolume);
    }

    // ── Missing / corrupted data → defaults ───────────────────────────────────

    [Fact]
    public void Load_WhenNoDataStored_ReturnsDefaults()
    {
        var (svc, _) = CreateSut();
        var result = svc.Load();
        Assert.Equal(1f, result.MasterVolume);
        Assert.Equal(1f, result.MusicVolume);
        Assert.Equal(1f, result.SfxVolume);
    }

    [Fact]
    public void Load_CorruptedData_ReturnsDefaults()
    {
        var (svc, storage) = CreateSut();
        storage.Write("not valid json!!!"u8.ToArray());
        var result = svc.Load();
        Assert.Equal(1f, result.MasterVolume);
        Assert.Equal(1f, result.MusicVolume);
        Assert.Equal(1f, result.SfxVolume);
    }

    [Fact]
    public void Load_EmptyBytes_ReturnsDefaults()
    {
        var (svc, storage) = CreateSut();
        storage.Write(Array.Empty<byte>());
        var result = svc.Load();
        Assert.Equal(1f, result.MasterVolume);
        Assert.Equal(1f, result.MusicVolume);
        Assert.Equal(1f, result.SfxVolume);
    }

    // ── Out-of-range values in JSON are clamped on load ───────────────────────

    [Fact]
    public void Load_JsonWithOverflowVolumes_ClampsToOne()
    {
        var (svc, storage) = CreateSut();
        storage.Write("""{"MasterVolume":5.0,"MusicVolume":99.0,"SfxVolume":1.0}"""u8.ToArray());
        var result = svc.Load();
        Assert.Equal(1f, result.MasterVolume);
        Assert.Equal(1f, result.MusicVolume);
        Assert.Equal(1f, result.SfxVolume);
    }

    [Fact]
    public void Load_JsonWithNegativeVolumes_ClampsToZero()
    {
        var (svc, storage) = CreateSut();
        storage.Write("""{"MasterVolume":-3.0,"MusicVolume":-0.1,"SfxVolume":0.5}"""u8.ToArray());
        var result = svc.Load();
        Assert.Equal(0f, result.MasterVolume);
        Assert.Equal(0f, result.MusicVolume);
        Assert.Equal(0.5f, result.SfxVolume);
    }

    // ── Null guard ────────────────────────────────────────────────────────────

    [Fact]
    public void Save_WithNullSettings_ThrowsArgumentNullException()
    {
        var (svc, _) = CreateSut();
        Assert.Throws<ArgumentNullException>(() => svc.Save(null!));
    }

    // ── Serialization integrity (Steam Cloud determinism) ─────────────────────

    [Fact]
    public void Save_SameSettings_ProducesDeterministicBytes()
    {
        var settings = new GameSettings { MasterVolume = 0.75f, MusicVolume = 0.5f, SfxVolume = 0.25f };

        var storageA = new InMemorySettingsStorage();
        var storageB = new InMemorySettingsStorage();
        new SettingsService(storageA).Save(settings);
        new SettingsService(storageB).Save(settings);

        Assert.True(storageA.Read()!.SequenceEqual(storageB.Read()!));
    }
}
