using System;
using System.Collections.Generic;
using Braziliation.Hydric;
using Xunit;

namespace Braziliation.Game.Tests;

/// <summary>
/// Estado global do rio em Blumenau (GDD/Features/Blumenau-SistemaHidrico.md): quatro estados
/// discretos, mudados pela campanha, nunca pelo jogador. A comporta trava em Cheia e Saturação.
/// </summary>
public sealed class HydricStateManagerTests
{
    // ── Estado inicial ────────────────────────────────────────────────────────

    [Fact]
    public void New_Manager_Starts_In_Routine()
    {
        Assert.Equal(HydricState.Routine, new HydricStateManager().Current);
    }

    [Fact]
    public void Initial_State_Can_Be_Injected()
    {
        Assert.Equal(HydricState.Flood, new HydricStateManager(HydricState.Flood).Current);
    }

    [Fact]
    public void Undefined_Initial_State_Is_Rejected()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => new HydricStateManager((HydricState)42));
    }

    // ── Transições ────────────────────────────────────────────────────────────

    [Fact]
    public void SetState_Changes_Current_And_Reports_Previous_And_New()
    {
        var manager = new HydricStateManager();
        var seen = new List<(HydricState from, HydricState to)>();
        manager.StateChanged += (from, to) => seen.Add((from, to));

        manager.SetState(HydricState.Alert);

        Assert.Equal(HydricState.Alert, manager.Current);
        Assert.Equal(new[] { (HydricState.Routine, HydricState.Alert) }, seen);
    }

    [Fact]
    public void SetState_To_Current_State_Does_Not_Notify()
    {
        var manager = new HydricStateManager(HydricState.Alert);
        var calls = 0;
        manager.StateChanged += (_, _) => calls++;

        manager.SetState(HydricState.Alert);

        Assert.Equal(0, calls);
    }

    [Fact]
    public void Campaign_Can_Jump_Between_Any_States()
    {
        // Evento de campanha pode forçar um estado (ex.: o clero abre comportas): sem ordem obrigatória.
        var manager = new HydricStateManager();
        var seen = new List<HydricState>();
        manager.StateChanged += (_, to) => seen.Add(to);

        manager.SetState(HydricState.Saturation);
        manager.SetState(HydricState.Routine);
        manager.SetState(HydricState.Flood);

        Assert.Equal(new[] { HydricState.Saturation, HydricState.Routine, HydricState.Flood }, seen);
    }

    [Fact]
    public void SetState_Undefined_Throws_And_Keeps_Current()
    {
        var manager = new HydricStateManager(HydricState.Alert);

        Assert.Throws<ArgumentOutOfRangeException>(() => manager.SetState((HydricState)99));
        Assert.Equal(HydricState.Alert, manager.Current);
    }

    [Fact]
    public void Two_Managers_Are_Independent()
    {
        var a = new HydricStateManager();
        var b = new HydricStateManager();

        a.SetState(HydricState.Flood);

        Assert.Equal(HydricState.Routine, b.Current);
    }

    // ── Regras por estado ─────────────────────────────────────────────────────

    [Theory]
    [InlineData(HydricState.Routine, false)]
    [InlineData(HydricState.Alert, false)]
    [InlineData(HydricState.Flood, true)]
    [InlineData(HydricState.Saturation, true)]
    public void Floodgates_Lock_In_Flood_And_Saturation(HydricState state, bool locked)
    {
        Assert.Equal(locked, state.LocksFloodgates());
    }

    [Fact]
    public void Persisted_Values_Never_Change()
    {
        // O estado do rio vai entrar no save da campanha: renumerar muda o rio de quem já jogou.
        Assert.Equal(0, (int)HydricState.Routine);
        Assert.Equal(1, (int)HydricState.Alert);
        Assert.Equal(2, (int)HydricState.Flood);
        Assert.Equal(3, (int)HydricState.Saturation);
        Assert.Equal(4, Enum.GetValues(typeof(HydricState)).Length);
    }
}
