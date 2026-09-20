using Xunit;

namespace Braziliation.Game.Tests;

/// <summary>
/// ADR-008: Claude Code é o único harness de agentes. O antigo AgentParityTests
/// comparava cada agente com o seu espelho Copilot; o espelho saiu, e fica o que
/// continua valendo — definição válida, registro no mapa e a .github/ sem agentes.
/// </summary>
public sealed class AgentDefinitionTests
{
    private static string GitRoot => RepoRootFinder.FindGitRoot();
    private static string AgentsDir => Path.Combine(GitRoot, ".claude", "agents");

    public static TheoryData<string> Agents()
    {
        var data = new TheoryData<string>();
        foreach (var file in Directory.GetFiles(Path.Combine(RepoRootFinder.FindGitRoot(), ".claude", "agents"), "*.md"))
            data.Add(Path.GetFileNameWithoutExtension(file));
        return data;
    }

    private static string[] Frontmatter(string name)
    {
        var lines = File.ReadAllLines(Path.Combine(AgentsDir, $"{name}.md"));
        var end = lines.Length > 1 ? Array.FindIndex(lines, 1, l => l.Trim() == "---") : -1;
        Assert.True(lines.Length > 0 && lines[0].Trim() == "---" && end > 0, $"Frontmatter malformado em {name}.md");
        return lines[1..end];
    }

    /// <summary>
    /// Um agente sem `model:` roda no modelo da conversa pai — escolha cara feita por
    /// omissão. Nome diferente do arquivo quebra a invocação por `@agent-{nome}`.
    /// </summary>
    [Theory]
    [MemberData(nameof(Agents))]
    public void Agent_Name_Matches_File_And_Declares_A_Model(string name)
    {
        var frontmatter = Frontmatter(name);
        Assert.Contains($"name: {name}", frontmatter);
        Assert.Contains(frontmatter, l => l.StartsWith("model:", StringComparison.Ordinal));
    }

    /// <summary>
    /// O modelo do projeto é reativo: nenhum agente invoca outro — cada camada escreve no
    /// TODO da seguinte e o usuário aciona (AGENTS.md, "Fluxo entre Camadas"; manual de
    /// processos, O1). Declarar `Task` ou `Agent` em `tools:` dá ao agente exatamente a
    /// capacidade que o modelo proíbe. O @AgentArchitect declarou as duas até 2026-09-19,
    /// enquanto o próprio corpo dele dizia "não invoca os agentes — o usuário aciona".
    /// </summary>
    [Theory]
    [MemberData(nameof(Agents))]
    public void Agent_Does_Not_Declare_Subagent_Tools(string name)
    {
        var tools = Frontmatter(name).FirstOrDefault(l => l.StartsWith("tools:", StringComparison.Ordinal));
        if (tools is null)
            return;

        var declared = tools["tools:".Length..]
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);

        foreach (var proibida in new[] { "Task", "Agent" })
            Assert.False(
                declared.Contains(proibida, StringComparer.Ordinal),
                $"@{name} declara `{proibida}` em tools:. O modelo é reativo — nenhum agente " +
                "invoca outro; a camada escreve no TODO da seguinte e o usuário aciona.");
    }

    /// <summary>O AGENTS.md é o inventário que os agentes leem; agente fora dele é invisível à orquestração.</summary>
    [Theory]
    [MemberData(nameof(Agents))]
    public void Agent_Is_Listed_In_Agents_Map(string name)
    {
        var map = File.ReadAllText(Path.Combine(GitRoot, "AGENTS.md")).Replace("-", string.Empty).ToLowerInvariant();
        Assert.True(map.Contains("@" + name.Replace("-", string.Empty).ToLowerInvariant(), StringComparison.Ordinal),
            $"@{name} não aparece na tabela de agentes do AGENTS.md");
    }

    /// <summary>A .github/ fica só com o que a plataforma GitHub usa (ADR-008).</summary>
    [Fact]
    public void Github_Folder_Holds_Only_Platform_Files()
    {
        var allowed = new HashSet<string>(StringComparer.Ordinal) { "workflows", "ISSUE_TEMPLATE", "PULL_REQUEST_TEMPLATE.md" };
        var extra = Directory.EnumerateFileSystemEntries(Path.Combine(GitRoot, ".github"))
            .Select(Path.GetFileName)
            .Where(n => !allowed.Contains(n!))
            .ToList();

        Assert.True(extra.Count == 0,
            "A .github/ só guarda CI e templates do GitHub; agentes, prompts e instruções de outros harnesses saíram no ADR-008: " +
            string.Join(", ", extra));
    }
}
