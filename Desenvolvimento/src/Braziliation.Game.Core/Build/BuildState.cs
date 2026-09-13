using System.Collections.Generic;
using Braziliation.Crafting;

namespace Braziliation.Build;

/// <summary>
/// Estado atual da build do personagem — o que está instalado nos três receptáculos.
/// Este modelo agrega toda a progressão material do jogador derivada do sistema de crafting.
/// C# puro: sem dependências Unity.
/// </summary>
public sealed class BuildState
{
    /// <summary>
    /// Os três receptáculos da build: Exoesqueleto (Mecânico), Capa (Místico), Espinha (Biológico).
    /// TODO-DESIGN: valor a definir pelo game design (quantidade de receptáculos = 3, confirmado na spec).
    /// </summary>
    public List<ReceptacleData> Receptacles { get; set; } = new List<ReceptacleData>();

    /// <summary>
    /// Conjunto de habilidades ativas derivadas dos itens instalados.
    /// Chave: identificador da habilidade (ex: "NightVision", "WaterBreathing").
    /// </summary>
    public HashSet<string> ActiveAbilities { get; set; } = new HashSet<string>();

    /// <summary>
    /// Resistências elementais e de status do personagem.
    /// Chave: nome da resistência (ex: "Poison", "Fire"). Valor: magnitude.
    /// TODO-DESIGN: escala de valores a definir pelo game design.
    /// </summary>
    public Dictionary<string, float> Resistances { get; set; } = new Dictionary<string, float>();

    /// <summary>
    /// Flags de exploração desbloqueadas pela build atual.
    /// Controlam acesso a zonas específicas do mundo (ex: "NightVision", "HiddenPaths", "UnderwaterBreathing").
    /// </summary>
    public HashSet<string> UnlockedExplorationFlags { get; set; } = new HashSet<string>();

    /// <summary>
    /// Retorna todos os itens atualmente instalados em qualquer slot de qualquer receptáculo.
    /// Slots vazios são ignorados.
    /// </summary>
    public List<ItemComponent> GetEquippedItems()
    {
        var items = new List<ItemComponent>();

        foreach (var receptacle in Receptacles)
        {
            foreach (var slot in receptacle.Slots)
            {
                if (!slot.IsEmpty && slot.EquippedItem != null)
                    items.Add(slot.EquippedItem);
            }
        }

        return items;
    }

    /// <summary>
    /// Verifica se uma habilidade específica está ativa na build atual.
    /// </summary>
    /// <param name="ability">Identificador da habilidade (ex: "NightVision").</param>
    public bool HasAbility(string ability)
    {
        return ActiveAbilities.Contains(ability);
    }
}
