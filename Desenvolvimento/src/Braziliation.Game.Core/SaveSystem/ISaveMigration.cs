using System.Text.Json.Nodes;

namespace Braziliation.SaveSystem;

/// <summary>
/// Um degrau de migração de save: transforma o JSON bruto da versão
/// <see cref="FromVersion"/> para <c>FromVersion + 1</c>.
///
/// Trabalha sobre <see cref="JsonObject"/>, não sobre <see cref="SaveSlot"/>, de
/// propósito: o modelo C# só descreve o schema **atual**, então desserializar antes de
/// migrar perderia justamente os campos antigos que a migração precisa ler.
///
/// Ao subir <see cref="SaveSlot.CurrentSchemaVersion"/>, registre aqui o degrau
/// correspondente — <see cref="SaveGameService"/> devolve
/// <see cref="SaveLoadStatus.NoMigrationPath"/> se ele faltar, e há um teste que trava
/// a cadeia completa de 1 até a versão atual.
/// </summary>
public interface ISaveMigration
{
    /// <summary>Versão de origem. O degrau produz <c>FromVersion + 1</c>.</summary>
    int FromVersion { get; }

    /// <summary>
    /// Devolve o payload convertido. Pode mutar e devolver o mesmo objeto.
    /// Não precisa gravar <c>SchemaVersion</c> — o serviço cuida disso.
    /// </summary>
    JsonObject Upgrade(JsonObject payload);
}
