using System.Text;
using System.Text.Json.Nodes;
using Braziliation.SaveSystem;
using Xunit;

namespace Braziliation.Game.Tests;

/// <summary>
/// Cobre o que <c>Load</c> devolvia como null indistinto: slot vazio, corrompido, de
/// versão futura e de versão antiga migrável. A regressão que estes testes travam é
/// "patch do jogo apaga o save do jogador em silêncio".
/// </summary>
public sealed class SaveMigrationTests
{
    private const int Slot = 0;

    private static byte[] Utf8(string json) => Encoding.UTF8.GetBytes(json);

    private static (SaveGameService svc, InMemorySaveStorage storage) CreateSut(
        params ISaveMigration[] migrations)
    {
        var storage = new InMemorySaveStorage();
        return (new SaveGameService(storage, migrations), storage);
    }

    /// <summary>Degrau de teste: renomeia um campo e soma 1 à versão.</summary>
    private sealed class RenameHeroToPlayerName : ISaveMigration
    {
        public int FromVersion { get; }

        public RenameHeroToPlayerName(int fromVersion) => FromVersion = fromVersion;

        public JsonObject Upgrade(JsonObject payload)
        {
            if (payload.Remove("Hero", out var hero))
                payload["PlayerName"] = hero;
            return payload;
        }
    }

    // ── Casos que antes eram todos "null" ─────────────────────────────────────

    [Fact]
    public void Empty_Slot_Reports_Empty()
    {
        var (svc, _) = CreateSut();
        Assert.Equal(SaveLoadStatus.Empty, svc.LoadDetailed(Slot).Status);
    }

    [Fact]
    public void Unparseable_Bytes_Report_Corrupt()
    {
        var (svc, storage) = CreateSut();
        storage.Write(Slot, Utf8("{ isto não é json"));

        var result = svc.LoadDetailed(Slot);

        Assert.Equal(SaveLoadStatus.Corrupt, result.Status);
        Assert.Null(result.Slot);
    }

    [Fact]
    public void Json_Without_SchemaVersion_Reports_Corrupt()
    {
        var (svc, storage) = CreateSut();
        storage.Write(Slot, Utf8("""{"SlotIndex":0,"PlayerName":"Zé"}"""));

        Assert.Equal(SaveLoadStatus.Corrupt, svc.LoadDetailed(Slot).Status);
    }

    [Fact]
    public void Save_From_Newer_Build_Is_Refused_And_Preserved()
    {
        var (svc, storage) = CreateSut();
        var future = SaveSlot.CurrentSchemaVersion + 7;
        storage.Write(Slot, Utf8($$"""{"SchemaVersion":{{future}},"SlotIndex":0,"PlayerName":"Futuro"}"""));

        var result = svc.LoadDetailed(Slot);

        Assert.Equal(SaveLoadStatus.FromNewerBuild, result.Status);
        Assert.Equal(future, result.FoundVersion);
        Assert.False(result.IsUsable);
        // O ponto principal: os bytes continuam lá para a próxima build ler.
        Assert.True(svc.SlotExists(Slot));
    }

    [Fact]
    public void Older_Version_Without_Registered_Migration_Reports_NoMigrationPath()
    {
        var (svc, storage) = CreateSut(); // nenhuma migração registrada
        storage.Write(Slot, Utf8("""{"SchemaVersion":0,"SlotIndex":0,"Hero":"Zé"}"""));

        var result = svc.LoadDetailed(Slot);

        Assert.Equal(SaveLoadStatus.NoMigrationPath, result.Status);
        Assert.Equal(0, result.FoundVersion);
        Assert.True(svc.SlotExists(Slot));
    }

    // ── Migração de fato ──────────────────────────────────────────────────────

    [Fact]
    public void Registered_Migration_Upgrades_Old_Payload()
    {
        var (svc, storage) = CreateSut(new RenameHeroToPlayerName(fromVersion: 0));
        storage.Write(Slot, Utf8("""{"SchemaVersion":0,"SlotIndex":0,"Hero":"Zé","CheckpointId":4}"""));

        var result = svc.LoadDetailed(Slot);

        Assert.Equal(SaveLoadStatus.Migrated, result.Status);
        Assert.Equal(0, result.FoundVersion);
        Assert.True(result.IsUsable);
        Assert.Equal("Zé", result.Slot!.PlayerName);
        Assert.Equal(4, result.Slot.CheckpointId);
        Assert.Equal(SaveSlot.CurrentSchemaVersion, result.Slot.SchemaVersion);
    }

    [Fact]
    public void Migrations_Chain_Across_Multiple_Versions()
    {
        // Simula duas versões de distância usando degraus encadeados.
        var steps = new ISaveMigration[]
        {
            new RenameHeroToPlayerName(0),
            new RenameHeroToPlayerName(1) // no-op no payload já renomeado
        };
        var storage = new InMemorySaveStorage();
        var svc = new SaveGameService(storage, steps);

        // Só é encadeável se a versão atual estiver 2 à frente; caso contrário o teste
        // vira uma verificação de que a cadeia curta funciona. Ambos são úteis.
        storage.Write(Slot, Utf8("""{"SchemaVersion":0,"SlotIndex":0,"Hero":"Zé"}"""));

        var result = svc.LoadDetailed(Slot);

        Assert.True(result.IsUsable);
        Assert.Equal("Zé", result.Slot!.PlayerName);
    }

    [Fact]
    public void Duplicate_Migration_For_Same_Version_Is_Rejected()
    {
        var storage = new InMemorySaveStorage();
        var ex = Assert.Throws<ArgumentException>(() => new SaveGameService(
            storage,
            new ISaveMigration[] { new RenameHeroToPlayerName(0), new RenameHeroToPlayerName(0) }));
        Assert.Contains("mais de uma migração", ex.Message);
    }

    // ── Guarda de release ─────────────────────────────────────────────────────

    [Fact]
    public void Current_Version_RoundTrips_As_Ok_Not_Migrated()
    {
        var (svc, _) = CreateSut();
        svc.Save(new SaveSlot { SlotIndex = Slot, PlayerName = "Atual", CheckpointId = 9 });

        var result = svc.LoadDetailed(Slot);

        Assert.Equal(SaveLoadStatus.Ok, result.Status);
        Assert.Equal("Atual", result.Slot!.PlayerName);
    }

    /// <summary>
    /// Se alguém subir CurrentSchemaVersion sem escrever o degrau, este teste falha
    /// antes do release em vez de o jogador descobrir com o save perdido.
    /// </summary>
    [Fact]
    public void Every_Version_Below_Current_Must_Have_A_Migration_Registered()
    {
        var registered = SaveMigrations.All.Select(m => m.FromVersion).ToHashSet();

        var missing = Enumerable
            .Range(1, Math.Max(0, SaveSlot.CurrentSchemaVersion - 1))
            .Where(v => !registered.Contains(v))
            .ToList();

        Assert.True(missing.Count == 0,
            "Faltam migrações a partir das versões: " + string.Join(", ", missing) +
            $". CurrentSchemaVersion = {SaveSlot.CurrentSchemaVersion}.");
    }
}
