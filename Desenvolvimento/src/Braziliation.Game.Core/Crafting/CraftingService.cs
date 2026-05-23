using System;
using System.Collections.Generic;

namespace Braziliation.Crafting;

/// <summary>
/// Serviço de resolução de crafting.
/// Busca receitas, valida compatibilidade de slots e resolve crafts híbridos.
/// C# puro: sem dependências Unity. Sem estado estático — todos os dados são recebidos por parâmetro.
/// </summary>
public sealed class CraftingService
{
    /// <summary>
    /// Busca a receita correspondente aos dois inputs fornecidos e retorna o item resultante.
    /// A busca é simétrica: (A, B) equivale a (B, A).
    /// Retorna null se nenhuma receita for encontrada.
    /// </summary>
    /// <param name="a">Primeiro componente de entrada.</param>
    /// <param name="b">Segundo componente de entrada.</param>
    /// <param name="recipes">Catálogo de receitas disponíveis.</param>
    public ItemComponent? Craft(ItemComponent a, ItemComponent b, List<CraftingRecipe> recipes)
    {
        foreach (var recipe in recipes)
        {
            bool match = (recipe.InputA.Id == a.Id && recipe.InputB.Id == b.Id)
                      || (recipe.InputA.Id == b.Id && recipe.InputB.Id == a.Id);

            if (match)
                return recipe.Result;
        }

        return null;
    }

    /// <summary>
    /// Verifica se um item pode ser instalado em um slot.
    /// Um item híbrido (com Stats de mais de um pilar) é compatível com qualquer slot
    /// cujo pilar coincida com um dos seus tipos.
    /// TODO-DESIGN: a lógica de compatibilidade de itens híbridos depende da decisão de design
    /// sobre como a tipagem híbrida será representada no ItemComponent (ex: lista de pilares).
    /// Implementação atual: verifica apenas o Pillar primário do item.
    /// </summary>
    /// <param name="item">Item a ser instalado.</param>
    /// <param name="slot">Slot de destino.</param>
    public bool ValidateSlotCompatibility(ItemComponent item, SlotData slot)
    {
        return item.Pillar == slot.AcceptedType;
    }

    /// <summary>
    /// Retorna verdadeiro se os dois componentes pertencem a pilares diferentes,
    /// caracterizando um craft híbrido.
    /// </summary>
    /// <param name="a">Primeiro componente.</param>
    /// <param name="b">Segundo componente.</param>
    public bool IsHybridCraft(ItemComponent a, ItemComponent b)
    {
        return a.Pillar != b.Pillar;
    }

    /// <summary>
    /// Resolve o pilar resultante de um craft com três tipos envolvidos (item híbrido + componente de 3º tipo).
    /// Conforme a spec: o 3º tipo é somado ao tipo do componente; qual dos dois tipos do híbrido acompanha
    /// é definido por sorteio 50/50.
    /// Retorna um novo ItemComponent com o Pillar sorteado e os dados do componente 'b'.
    /// TODO-DESIGN: a composição completa do item resultante (Stats, DisplayName, Lore) depende
    /// de decisão de design — atualmente apenas o Pillar é sorteado.
    /// </summary>
    /// <param name="a">Item híbrido (dois tipos) que já está na mesa.</param>
    /// <param name="b">Componente de terceiro tipo sendo adicionado.</param>
    /// <param name="rng">Instância de Random para o sorteio 50/50.</param>
    public ItemComponent RollHybridResult(ItemComponent a, ItemComponent b, Random rng)
    {
        // TODO-DESIGN: quando ItemComponent suportar múltiplos pilares, extrair os dois
        // pilares do item híbrido 'a' e sortear qual acompanha o pilar de 'b'.
        // Por ora, o pilar sorteado é entre o Pillar de 'a' e o Pillar de 'b'.
        bool keepA = rng.Next(0, 2) == 0; // 50/50

        return new ItemComponent
        {
            Id = b.Id,
            DisplayName = b.DisplayName,
            Lore = b.Lore,
            Pillar = keepA ? a.Pillar : b.Pillar,
            Stats = new System.Collections.Generic.Dictionary<string, float>(b.Stats)
        };
    }
}
