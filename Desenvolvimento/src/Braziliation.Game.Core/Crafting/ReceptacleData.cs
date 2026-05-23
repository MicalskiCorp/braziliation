using System.Collections.Generic;

namespace Braziliation.Crafting;

/// <summary>
/// Tipos de receptáculo disponíveis na build do personagem.
/// Cada receptáculo corresponde a um pilar temático.
/// </summary>
public enum ReceptacleType
{
    /// <summary>Exoesqueleto dos Trilhos — pilar Mecânico.</summary>
    Exoskeleton,

    /// <summary>Capa das Lendas do Mar — pilar Místico.</summary>
    Cape,

    /// <summary>Espinha de Fungo — pilar Biológico.</summary>
    Spine
}

/// <summary>
/// Modelo de um receptáculo da build do personagem.
/// Contém os slots onde itens criados na mesa de crafting são instalados.
/// C# puro: sem dependências Unity.
/// </summary>
public sealed class ReceptacleData
{
    /// <summary>Nome exibido na UI para o jogador (ex: "Exoesqueleto dos Trilhos").</summary>
    public string DisplayName { get; set; } = string.Empty;

    /// <summary>Tipo deste receptáculo.</summary>
    public ReceptacleType Type { get; set; }

    /// <summary>Pilar ao qual este receptáculo pertence.</summary>
    public PillarType Pillar { get; set; }

    /// <summary>
    /// Nível de expansão atual (começa em 0).
    /// Aumenta quando o jogador entrega materiais especiais a NPCs específicos.
    /// </summary>
    public int ExpansionLevel { get; set; } = 0;

    /// <summary>
    /// Slots disponíveis neste receptáculo.
    /// TODO-DESIGN: número inicial de slots a confirmar com game design — valor atual: 2.
    /// </summary>
    public List<SlotData> Slots { get; set; } = new List<SlotData>
    {
        new SlotData(),
        new SlotData()
        // TODO-DESIGN: valor a definir pelo game design (quantidade inicial de slots por receptáculo)
    };
}
