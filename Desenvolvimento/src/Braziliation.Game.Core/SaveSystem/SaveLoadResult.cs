namespace Braziliation.SaveSystem;

/// <summary>
/// Desfecho de uma tentativa de carregar um slot.
/// Existe porque <c>null</c> não distingue "slot vazio" de "save corrompido" de
/// "save de uma versão futura do jogo" — e tratar os três igual significa apagar
/// progresso do jogador sem avisar depois de um patch.
/// </summary>
public enum SaveLoadStatus
{
    /// <summary>Carregado, já na versão atual do schema.</summary>
    Ok,

    /// <summary>Não há nada gravado neste slot.</summary>
    Empty,

    /// <summary>Bytes ilegíveis como JSON, ou JSON que não descreve um slot.</summary>
    Corrupt,

    /// <summary>Carregado após migração bem-sucedida de uma versão anterior.</summary>
    Migrated,

    /// <summary>
    /// Gravado por uma build **mais nova** do jogo. Nunca migre nem sobrescreva:
    /// downgrade é perda de dados. A UI deve bloquear o slot e explicar.
    /// </summary>
    FromNewerBuild,

    /// <summary>
    /// Versão anterior para a qual não existe caminho de migração registrado.
    /// É um bug de release — alguém subiu <see cref="SaveSlot.CurrentSchemaVersion"/>
    /// sem escrever a <see cref="ISaveMigration"/> correspondente.
    /// </summary>
    NoMigrationPath,
}

/// <summary>Resultado de <see cref="SaveGameService.LoadDetailed"/>.</summary>
public readonly struct SaveLoadResult
{
    private SaveLoadResult(SaveLoadStatus status, SaveSlot? slot, int foundVersion)
    {
        Status = status;
        Slot = slot;
        FoundVersion = foundVersion;
    }

    public SaveLoadStatus Status { get; }

    /// <summary>O slot carregado, ou null em qualquer status que não seja Ok/Migrated.</summary>
    public SaveSlot? Slot { get; }

    /// <summary>Versão de schema encontrada nos bytes. -1 quando não foi possível ler.</summary>
    public int FoundVersion { get; }

    /// <summary>Verdadeiro quando há um slot utilizável. Decide o Continuar do menu.</summary>
    public bool IsUsable => Status is SaveLoadStatus.Ok or SaveLoadStatus.Migrated;

    /// <summary>
    /// Verdadeiro quando Novo Jogo pode gravar por cima deste slot. Decide o Novo Jogo do menu.
    /// </summary>
    public bool CanOverwrite => AllowsOverwrite(Status);

    /// <summary>
    /// Regra de sobrescrita por status (contrato em <c>Sistemas/UI.md</c> › Estado do slot).
    /// É uma lista **positiva**: um status novo nasce bloqueado até alguém decidir.
    /// <see cref="SaveLoadStatus.Corrupt"/> pode ser sobrescrito porque não há tela para apagar o
    /// slot; <see cref="SaveLoadStatus.FromNewerBuild"/> e <see cref="SaveLoadStatus.NoMigrationPath"/>
    /// nunca, porque os bytes ainda podem ser lidos por outra build.
    /// </summary>
    public static bool AllowsOverwrite(SaveLoadStatus status) =>
        status is SaveLoadStatus.Empty
            or SaveLoadStatus.Ok
            or SaveLoadStatus.Migrated
            or SaveLoadStatus.Corrupt;

    internal static SaveLoadResult Ok(SaveSlot slot) =>
        new(SaveLoadStatus.Ok, slot, slot.SchemaVersion);

    internal static SaveLoadResult Migrated(SaveSlot slot, int foundVersion) =>
        new(SaveLoadStatus.Migrated, slot, foundVersion);

    internal static readonly SaveLoadResult Empty = new(SaveLoadStatus.Empty, null, -1);

    internal static SaveLoadResult Corrupt(int foundVersion = -1) =>
        new(SaveLoadStatus.Corrupt, null, foundVersion);

    internal static SaveLoadResult FromNewerBuild(int foundVersion) =>
        new(SaveLoadStatus.FromNewerBuild, null, foundVersion);

    internal static SaveLoadResult NoMigrationPath(int foundVersion) =>
        new(SaveLoadStatus.NoMigrationPath, null, foundVersion);
}
