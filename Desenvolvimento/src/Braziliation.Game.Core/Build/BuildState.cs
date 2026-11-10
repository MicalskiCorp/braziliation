using System.Collections.Generic;
using Braziliation.Crafting;

namespace Braziliation.Build;

/// <summary>
/// Estado atual da build do personagem — o que está instalado nos três receptáculos.
/// Este modelo agrega toda a progressão material do jogador derivada do sistema de crafting.
/// É a **fonte única** dos receptáculos: o <c>ReceptacleController</c> (Unity) altera as instâncias
/// devolvidas por <see cref="GetReceptacle"/>, e quem lê (build, sinergias, flags, UI) lê daqui.
/// C# puro: sem dependências Unity.
/// </summary>
public sealed class BuildState
{
    /// <summary>
    /// Os três receptáculos da build: Exoesqueleto (Mecânico), Capa (Místico), Espinha (Biológico).
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
    /// Build inicial do jogo: os três receptáculos de Build.md, sem itens e sem expansão.
    /// Cada chamada devolve um estado novo e independente.
    /// </summary>
    public static BuildState CreateDefault() => new BuildState
    {
        Receptacles = new List<ReceptacleData>
        {
            new ReceptacleData
            {
                DisplayName = "Exoesqueleto dos Trilhos",
                Type        = ReceptacleType.Exoskeleton,
                Pillar      = PillarType.Mechanical,
            },
            new ReceptacleData
            {
                DisplayName = "Capa das Lendas do Mar",
                Type        = ReceptacleType.Cape,
                Pillar      = PillarType.Mystical,
            },
            new ReceptacleData
            {
                DisplayName = "Espinha de Fungo",
                Type        = ReceptacleType.Spine,
                Pillar      = PillarType.Biological,
            },
        },
    };

    /// <summary>
    /// Receptáculo do tipo informado, ou null se a build não tiver um. Devolve a própria instância
    /// guardada no estado: alterar o retorno altera a build.
    /// </summary>
    public ReceptacleData? GetReceptacle(ReceptacleType type)
    {
        foreach (var receptacle in Receptacles)
        {
            if (receptacle.Type == type)
                return receptacle;
        }

        return null;
    }

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
