namespace Braziliation.Hydric;

/// <summary>
/// Os quatro estados do rio Itajaí-Açu em Blumenau (GDD/Features/Blumenau-SistemaHidrico.md).
/// Mudam pela campanha, nunca pela mão do jogador.
/// </summary>
/// <remarks>
/// O valor numérico vai entrar no save da campanha: nunca renumerar nem reordenar.
/// </remarks>
public enum HydricState
{
    /// <summary>Rotina — nível normal, acesso completo, comportas abertas.</summary>
    Routine = 0,

    /// <summary>Alerta — rio subindo, passarelas elevando, bairros baixos fechando.</summary>
    Alert = 1,

    /// <summary>Cheia — bairros baixos inundados, comportas fechadas, docas ativas.</summary>
    Flood = 2,

    /// <summary>Saturação — o sistema falha: comportas travam, passarelas colapsam, subterrâneos se abrem.</summary>
    Saturation = 3,
}

/// <summary>Regras de mundo derivadas do estado do rio. Funções puras, sem estado.</summary>
public static class HydricStateRules
{
    /// <summary>
    /// Verdadeiro quando a alavanca da comporta deixa de responder: em Cheia (comportas fechadas pelo
    /// sistema) e em Saturação (comportas travam).
    /// </summary>
    public static bool LocksFloodgates(this HydricState state) =>
        state is HydricState.Flood or HydricState.Saturation;
}
