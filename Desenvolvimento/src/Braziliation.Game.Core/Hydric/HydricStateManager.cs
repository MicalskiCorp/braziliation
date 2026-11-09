using System;

namespace Braziliation.Hydric;

/// <summary>
/// Estado global do rio em Blumenau. Serviço comum, registrado no <c>GameServiceLocator</c>, que dura
/// entre cenas; **não** é singleton estático, ao contrário do que a feature sugeria, porque o core
/// não guarda estado estático. Quem muda o estado são os eventos de campanha, por <see cref="SetState"/>.
/// Quem reage (comportas, passarelas, docas, sinos, HUD) assina <see cref="StateChanged"/> e lê
/// <see cref="Current"/> ao se inscrever.
/// </summary>
public sealed class HydricStateManager
{
    /// <summary>Estado atual do rio.</summary>
    public HydricState Current { get; private set; }

    /// <summary>Disparado depois de cada mudança real de estado: (anterior, novo).</summary>
    public event Action<HydricState, HydricState>? StateChanged;

    /// <param name="initial">Estado de partida; Rotina por padrão. Quando o rio entrar no save, vem dele.</param>
    public HydricStateManager(HydricState initial = HydricState.Routine)
    {
        Current = Validate(initial);
    }

    /// <summary>
    /// Leva o rio ao estado pedido. Pedir o estado atual não notifica ninguém. Qualquer estado pode
    /// seguir qualquer outro: um evento de campanha pode forçar um salto (o clero abrindo comportas).
    /// </summary>
    /// <exception cref="ArgumentOutOfRangeException">Valor fora do enum; o estado atual não muda.</exception>
    public void SetState(HydricState next)
    {
        Validate(next);
        if (next == Current)
            return;

        var previous = Current;
        Current = next;
        StateChanged?.Invoke(previous, next);
    }

    private static HydricState Validate(HydricState state)
    {
        if (!Enum.IsDefined(typeof(HydricState), state))
            throw new ArgumentOutOfRangeException(nameof(state), state, "Estado do rio inexistente.");
        return state;
    }
}
