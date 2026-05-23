namespace Braziliation.Crafting;

/// <summary>
/// Modelo de uma receita de crafting que define quais componentes produzem qual item.
/// Receitas são resolvidas pelo <see cref="CraftingService"/>.
/// C# puro: sem dependências Unity.
/// </summary>
public sealed class CraftingRecipe
{
    /// <summary>Primeiro componente de entrada.</summary>
    public ItemComponent InputA { get; set; } = new ItemComponent();

    /// <summary>Segundo componente de entrada.</summary>
    public ItemComponent InputB { get; set; } = new ItemComponent();

    /// <summary>Item resultante da combinação.</summary>
    public ItemComponent Result { get; set; } = new ItemComponent();

    /// <summary>
    /// Verdadeiro se os dois inputs pertencem a pilares diferentes.
    /// Receitas híbridas podem desbloquear sinergias e efeitos ocultos.
    /// </summary>
    public bool IsHybridSynergy { get; set; }

    /// <summary>
    /// Descrição textual do efeito especial gerado por esta sinergia híbrida.
    /// Vazio para receitas de pilar único.
    /// </summary>
    public string SynergyDescription { get; set; } = string.Empty;
}
