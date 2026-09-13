using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using Braziliation.Serialization;

namespace Braziliation.SaveSystem;

/// <summary>
/// Salva e carrega instâncias de <see cref="SaveSlot"/> por meio de um backend de
/// armazenamento plugável. Cada slot é independente.
///
/// Carregamento nunca lança: um slot ausente, corrompido ou de outra versão de schema
/// vira um <see cref="SaveLoadResult"/> que diz **qual** dos casos ocorreu. Use
/// <see cref="LoadDetailed"/> quando a UI precisar reagir de formas diferentes —
/// especialmente <see cref="SaveLoadStatus.FromNewerBuild"/>, onde sobrescrever o slot
/// destrói progresso do jogador.
/// </summary>
public sealed class SaveGameService
{
    private readonly ISaveStorage _storage;
    private readonly Dictionary<int, ISaveMigration> _migrations;

    public SaveGameService(ISaveStorage storage, IEnumerable<ISaveMigration>? migrations = null)
    {
        if (storage is null) throw new ArgumentNullException(nameof(storage));
        _storage = storage;

        _migrations = new Dictionary<int, ISaveMigration>();
        foreach (var migration in migrations ?? Enumerable.Empty<ISaveMigration>())
        {
            if (migration is null)
                throw new ArgumentException("Migração nula na coleção.", nameof(migrations));
            if (_migrations.ContainsKey(migration.FromVersion))
                throw new ArgumentException(
                    $"Há mais de uma migração a partir da versão {migration.FromVersion}.",
                    nameof(migrations));
            _migrations.Add(migration.FromVersion, migration);
        }
    }

    public void Save(SaveSlot slot)
    {
        if (slot is null) throw new ArgumentNullException(nameof(slot));
        slot.SchemaVersion = SaveSlot.CurrentSchemaVersion;
        var bytes = JsonSerializer.SerializeToUtf8Bytes(slot, SaveJsonOptions.Default);
        _storage.Write(slot.SlotIndex, bytes);
    }

    /// <summary>
    /// Carrega o slot, ou devolve null quando ele não existe, está corrompido ou não pode
    /// ser migrado. Conveniência para chamadores que só querem "tem save utilizável?" —
    /// prefira <see cref="LoadDetailed"/> quando a distinção importar.
    /// </summary>
    public SaveSlot? Load(int slotIndex) => LoadDetailed(slotIndex).Slot;

    /// <summary>Carrega o slot informando exatamente o que aconteceu.</summary>
    public SaveLoadResult LoadDetailed(int slotIndex)
    {
        var bytes = _storage.Read(slotIndex);
        if (bytes is null || bytes.Length == 0)
            return SaveLoadResult.Empty;

        JsonObject? payload;
        try
        {
            payload = JsonNode.Parse(Encoding.UTF8.GetString(bytes)) as JsonObject;
        }
        catch (JsonException)
        {
            return SaveLoadResult.Corrupt();
        }

        if (payload is null)
            return SaveLoadResult.Corrupt();

        var foundVersion = ReadSchemaVersion(payload);
        if (foundVersion < 0)
            return SaveLoadResult.Corrupt();

        if (foundVersion > SaveSlot.CurrentSchemaVersion)
            return SaveLoadResult.FromNewerBuild(foundVersion);

        var version = foundVersion;
        while (version < SaveSlot.CurrentSchemaVersion)
        {
            if (!_migrations.TryGetValue(version, out var migration))
                return SaveLoadResult.NoMigrationPath(foundVersion);

            payload = migration.Upgrade(payload)
                      ?? throw new InvalidOperationException(
                          $"Migração a partir da versão {version} devolveu null.");
            version++;
        }

        SaveSlot? slot;
        try
        {
            slot = payload.Deserialize<SaveSlot>(SaveJsonOptions.Default);
        }
        catch (JsonException)
        {
            return SaveLoadResult.Corrupt(foundVersion);
        }

        if (slot is null)
            return SaveLoadResult.Corrupt(foundVersion);

        slot.SchemaVersion = SaveSlot.CurrentSchemaVersion;

        return foundVersion == SaveSlot.CurrentSchemaVersion
            ? SaveLoadResult.Ok(slot)
            : SaveLoadResult.Migrated(slot, foundVersion);
    }

    public bool SlotExists(int slotIndex) => _storage.Exists(slotIndex);

    public void DeleteSlot(int slotIndex) => _storage.Delete(slotIndex);

    // ── Auxiliares ────────────────────────────────────────────────────────────────

    /// <summary>
    /// Lê SchemaVersion do payload bruto. Busca sem diferenciar maiúsculas para casar com
    /// <c>PropertyNameCaseInsensitive</c> das opções de serialização. Devolve -1 quando o
    /// campo falta ou não é um inteiro — payload que não veio deste jogo.
    /// </summary>
    private static int ReadSchemaVersion(JsonObject payload)
    {
        foreach (var pair in payload)
        {
            if (!string.Equals(pair.Key, nameof(SaveSlot.SchemaVersion), StringComparison.OrdinalIgnoreCase))
                continue;

            return pair.Value is JsonValue value && value.TryGetValue<int>(out var version)
                ? version
                : -1;
        }

        return -1;
    }
}
