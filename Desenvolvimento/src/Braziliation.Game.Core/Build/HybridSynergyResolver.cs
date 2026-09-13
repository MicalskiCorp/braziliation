using System.Collections.Generic;

namespace Braziliation.Build;

/// <summary>
/// Detecção e resolução de sinergias híbridas na build do personagem.
/// Sinergias híbridas emergem quando itens de pilares diferentes são combinados na build.
/// C# puro: sem dependências Unity.
/// </summary>
public sealed class HybridSynergyResolver
{
    // Tabela de sinergias híbridas — chave normalizada em ordem alfabética (A|B == B|A).
    // Conforme Build.md — Sinergias Híbridas:
    //   Mecânico × Biológico → "PrótesisViva"
    //   Biológico × Místico  → "MutaçãoArcana"
    //   Mecânico × Místico   → "ArmaduraEncantada"
    // Nota: "Biological" < "Mechanical" < "Mystical" em ordem alfabética ordinal.
    private static readonly Dictionary<string, List<string>> _hybridEffectTable =
        new Dictionary<string, List<string>>
        {
            ["Biological|Mechanical"] = new List<string> { "PrótesisViva" },
            ["Biological|Mystical"]   = new List<string> { "MutaçãoArcana" },
            ["Mechanical|Mystical"]   = new List<string> { "ArmaduraEncantada" },
        };

    /// <summary>
    /// Verifica se a build atual possui pelo menos uma combinação híbrida válida
    /// (item com pilar diferente do receptáculo onde está instalado, conforme spec de Crafting).
    /// Retorna verdadeiro se algum efeito híbrido estiver ativo.
    /// </summary>
    /// <param name="state">Estado atual da build.</param>
    public bool HasHybridSynergy(BuildState state)
    {
        return GetActiveHybridEffects(state).Count > 0;
    }

    /// <summary>
    /// Retorna a lista de identificadores de efeitos híbridos ativos na build atual.
    /// Percorre todos os itens instalados e verifica combinações de pilares contra a tabela interna.
    /// </summary>
    /// <param name="state">Estado atual da build.</param>
    public List<string> GetActiveHybridEffects(BuildState state)
    {
        var activeEffects = new List<string>();
        var equippedItems = state.GetEquippedItems();

        // Verifica cada par de itens equipados em busca de combinações híbridas registradas
        for (int i = 0; i < equippedItems.Count; i++)
        {
            for (int j = i + 1; j < equippedItems.Count; j++)
            {
                var pillarA = equippedItems[i].Pillar;
                var pillarB = equippedItems[j].Pillar;

                if (pillarA == pillarB)
                    continue;

                // Chave normalizada em ordem alfabética para garantir busca simétrica
                string key = BuildHybridKey(pillarA, pillarB);

                if (_hybridEffectTable.TryGetValue(key, out var effects))
                {
                    foreach (var effect in effects)
                    {
                        if (!activeEffects.Contains(effect))
                            activeEffects.Add(effect);
                    }
                }
            }
        }

        return activeEffects;
    }

    /// <summary>
    /// Constrói a chave de lookup para a tabela de sinergias híbridas.
    /// A chave é ordenada para garantir simetria (A|B == B|A).
    /// </summary>
    private static string BuildHybridKey(Crafting.PillarType a, Crafting.PillarType b)
    {
        string nameA = a.ToString();
        string nameB = b.ToString();

        return string.Compare(nameA, nameB, System.StringComparison.Ordinal) <= 0
            ? $"{nameA}|{nameB}"
            : $"{nameB}|{nameA}";
    }
}
