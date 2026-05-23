using System.Collections.Generic;

namespace Braziliation.Crafting;

/// <summary>
/// Representa o pilar temático de um componente ou item.
/// Cada pilar corresponde a um receptáculo específico da build do personagem.
/// </summary>
public enum PillarType
{
    /// <summary>Máquinas, engrenagens, exoesqueleto dos trilhos.</summary>
    Mechanical,

    /// <summary>Magia, runas, capa das lendas do mar.</summary>
    Mystical,

    /// <summary>Flora, fungos, espinha de fungo.</summary>
    Biological
}

/// <summary>
/// Modelo de um componente de crafting — material bruto coletado no mundo.
/// Componentes precisam ser combinados na mesa de crafting para gerar itens utilizáveis.
/// C# puro: sem dependências Unity.
/// </summary>
public sealed class ItemComponent
{
    /// <summary>Identificador único do componente (ex: "comp_gear_oxidized").</summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>Nome exibido na UI para o jogador.</summary>
    public string DisplayName { get; set; } = string.Empty;

    /// <summary>Texto narrativo que contextualiza o componente no mundo do jogo.</summary>
    public string Lore { get; set; } = string.Empty;

    /// <summary>Pilar ao qual este componente pertence.</summary>
    public PillarType Pillar { get; set; }

    /// <summary>
    /// Stats configuráveis deste componente (ex: "attack", "defense", "speed").
    /// Chave: nome do stat. Valor: magnitude.
    /// TODO-DESIGN: definir quais stats existem e seus valores com o game design.
    /// </summary>
    public Dictionary<string, float> Stats { get; set; } = new Dictionary<string, float>();
}
