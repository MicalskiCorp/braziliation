using System;
using System.Text;
using Braziliation.SaveSystem;
using Xunit;

namespace Braziliation.Game.Tests;

/// <summary>
/// Regra de seleção do slot no menu (contrato em Sistemas/UI.md › Estado do slot):
/// <see cref="SaveLoadResult.IsUsable"/> decide Continuar e
/// <see cref="SaveLoadResult.CanOverwrite"/> decide Novo Jogo. A regressão travada aqui é
/// "Novo Jogo grava por cima de um save de build mais nova".
/// </summary>
public sealed class SaveLoadResultTests
{
    private const int Slot = 0;

    [Theory]
    [InlineData(SaveLoadStatus.Empty, true)]
    [InlineData(SaveLoadStatus.Ok, true)]
    [InlineData(SaveLoadStatus.Migrated, true)]
    // Bloquear Corrupt deixaria o slot inutilizável para sempre: não há tela para apagar.
    [InlineData(SaveLoadStatus.Corrupt, true)]
    // ADR-007: downgrade é perda de dados, nunca sobrescrever.
    [InlineData(SaveLoadStatus.FromNewerBuild, false)]
    // Bug de release: o patch com o degrau de migração recupera o save.
    [InlineData(SaveLoadStatus.NoMigrationPath, false)]
    public void AllowsOverwrite_Follows_The_Slot_Contract(SaveLoadStatus status, bool expected)
    {
        Assert.Equal(expected, SaveLoadResult.AllowsOverwrite(status));
    }

    [Fact]
    public void New_Status_Forces_A_Decision_On_Overwrite()
    {
        // Se este teste quebrou, nasceu um SaveLoadStatus novo. Ele já sai bloqueado para Novo
        // Jogo (lista positiva); decida se pode sobrescrever, acrescente a linha no [Theory]
        // acima e o texto do SaveSlotEntryView, e só então atualize a contagem.
        Assert.Equal(6, Enum.GetValues(typeof(SaveLoadStatus)).Length);
    }

    [Fact]
    public void Undefined_Status_Is_Not_Overwritable()
    {
        Assert.False(SaveLoadResult.AllowsOverwrite((SaveLoadStatus)999));
    }

    [Fact]
    public void Save_From_Newer_Build_Cannot_Be_Overwritten_Or_Continued()
    {
        var storage = new InMemorySaveStorage();
        var svc = new SaveGameService(storage);
        var future = SaveSlot.CurrentSchemaVersion + 1;
        storage.Write(Slot, Encoding.UTF8.GetBytes($$"""{"SchemaVersion":{{future}},"SlotIndex":0,"PlayerName":"Futuro"}"""));

        var result = svc.LoadDetailed(Slot);

        Assert.False(result.CanOverwrite);
        Assert.False(result.IsUsable);
    }

    [Fact]
    public void Corrupt_Slot_Can_Be_Overwritten_But_Not_Continued()
    {
        var storage = new InMemorySaveStorage();
        var svc = new SaveGameService(storage);
        storage.Write(Slot, Encoding.UTF8.GetBytes("{ isto não é json"));

        var result = svc.LoadDetailed(Slot);

        Assert.True(result.CanOverwrite);
        Assert.False(result.IsUsable);
    }

    [Fact]
    public void Empty_Slot_Can_Start_A_New_Game()
    {
        var svc = new SaveGameService(new InMemorySaveStorage());

        var result = svc.LoadDetailed(Slot);

        Assert.True(result.CanOverwrite);
        Assert.False(result.IsUsable);
    }
}
