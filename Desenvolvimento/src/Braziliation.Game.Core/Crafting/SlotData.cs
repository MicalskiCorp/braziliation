namespace Braziliation.Crafting;

/// <summary>
/// Modelo de um slot individual dentro de um receptáculo.
/// Cada slot aceita apenas itens do tipo correspondente ao seu pilar.
/// </summary>
public sealed class SlotData
{
    /// <summary>Tipo de pilar aceito por este slot.</summary>
    public PillarType AcceptedType { get; set; }

    /// <summary>
    /// Item atualmente instalado neste slot.
    /// Null quando o slot está vazio.
    /// </summary>
    public ItemComponent? EquippedItem { get; set; }

    /// <summary>Indica se o slot não possui nenhum item instalado.</summary>
    public bool IsEmpty => EquippedItem == null;
}
