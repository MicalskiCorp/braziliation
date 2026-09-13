namespace Braziliation.SaveSystem;

/// <summary>
/// Registro único das migrações de save do jogo.
///
/// Toda vez que <see cref="SaveSlot.CurrentSchemaVersion"/> subir, adicione aqui o
/// degrau que sai da versão anterior. O teste
/// <c>Every_Version_Below_Current_Must_Have_A_Migration_Registered</c> falha se você
/// esquecer — de propósito: o custo de esquecer é o save do jogador.
///
/// Está vazio hoje porque a versão atual é a 1, a primeira. Não é um TODO.
/// </summary>
public static class SaveMigrations
{
    /// <summary>
    /// Migrações na ordem em que devem ser aplicadas.
    /// Passe para o construtor de <see cref="SaveGameService"/>.
    /// </summary>
    public static IReadOnlyList<ISaveMigration> All { get; } = new List<ISaveMigration>
    {
        // Exemplo do formato, para quando a versão 2 existir:
        //
        //   new DelegateSaveMigration(fromVersion: 1, payload =>
        //   {
        //       if (payload.Remove("Hero", out var hero))
        //           payload["PlayerName"] = hero;
        //       return payload;
        //   }),
    };
}
