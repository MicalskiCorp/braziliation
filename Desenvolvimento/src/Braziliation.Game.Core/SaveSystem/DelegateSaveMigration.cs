using System.Text.Json.Nodes;

namespace Braziliation.SaveSystem;

/// <summary>
/// <see cref="ISaveMigration"/> a partir de uma lambda, para degraus curtos que não
/// merecem uma classe própria. Degraus complexos devem virar tipo nomeado e testado.
/// </summary>
public sealed class DelegateSaveMigration : ISaveMigration
{
    private readonly Func<JsonObject, JsonObject> _upgrade;

    public DelegateSaveMigration(int fromVersion, Func<JsonObject, JsonObject> upgrade)
    {
        if (fromVersion < 0)
            throw new ArgumentOutOfRangeException(nameof(fromVersion), "Versão de origem não pode ser negativa.");
        FromVersion = fromVersion;
        _upgrade = upgrade ?? throw new ArgumentNullException(nameof(upgrade));
    }

    public int FromVersion { get; }

    public JsonObject Upgrade(JsonObject payload) => _upgrade(payload);
}
