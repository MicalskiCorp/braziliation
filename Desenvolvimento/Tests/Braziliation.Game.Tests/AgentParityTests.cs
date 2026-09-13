using Xunit;

namespace Braziliation.Game.Tests;

/// <summary>
/// Os 11 agentes existem em dois formatos — Claude Code (<c>.claude/agents/*.md</c>) e
/// VS Code Copilot (<c>.github/agents/*.agent.md</c>). O frontmatter difere de propósito
/// (cada harness tem seu vocabulário de `tools:`), mas o **corpo** é o mesmo prompt e
/// precisa continuar sendo.
///
/// Sem esta guarda a sincronia dependia de lembrar de rodar a skill `novo-agente`, e
/// divergência silenciosa entre os dois significa dois agentes com o mesmo nome se
/// comportando diferente conforme a ferramenta usada.
/// </summary>
public sealed class AgentParityTests
{
    /// <summary>Claude (kebab-case) → Copilot (PascalCase).</summary>
    private static readonly Dictionary<string, string> AgentPairs = new()
    {
        ["agent-architect"] = "AgentArchitect",
        ["game-architect"] = "GameArchitect",
        ["game-creative"] = "GameCreative",
        ["gameplay-engineer"] = "GameplayEngineer",
        ["historiador"] = "Historiador",
        ["qa-engineer"] = "QAEngineer",
        ["sprite-artist"] = "SpriteArtist",
        ["systems-developer"] = "SystemsDeveloper",
        ["tech-lead"] = "TechLead",
        ["test-engineer"] = "TestEngineer",
        ["unity-developer"] = "UnityDeveloper",
    };

    private static string ClaudeDir => Path.Combine(RepoRootFinder.FindGitRoot(), ".claude", "agents");
    private static string CopilotDir => Path.Combine(RepoRootFinder.FindGitRoot(), ".github", "agents");

    public static TheoryData<string, string> Pairs()
    {
        var data = new TheoryData<string, string>();
        foreach (var pair in AgentPairs)
            data.Add(pair.Key, pair.Value);
        return data;
    }

    /// <summary>Tudo depois do frontmatter YAML, normalizado para comparação.</summary>
    private static string ReadBody(string path)
    {
        // utf-8-sig: os arquivos Copilot têm BOM, os Claude não.
        var text = File.ReadAllText(path).TrimStart('\uFEFF');
        var parts = text.Split("---", 3);
        var body = parts.Length >= 3 ? parts[2] : text;
        return body.Replace("\r\n", "\n").Trim();
    }

    [Theory]
    [MemberData(nameof(Pairs))]
    public void Agent_Body_Is_Identical_Across_Both_Formats(string claudeName, string copilotName)
    {
        var claudePath = Path.Combine(ClaudeDir, $"{claudeName}.md");
        var copilotPath = Path.Combine(CopilotDir, $"{copilotName}.agent.md");

        Assert.True(File.Exists(claudePath), $"Ausente: {claudePath}");
        Assert.True(File.Exists(copilotPath), $"Ausente: {copilotPath}");

        Assert.True(
            ReadBody(claudePath) == ReadBody(copilotPath),
            $"O corpo de '{claudeName}' divergiu entre os dois formatos. " +
            "Ajuste os dois (skill `novo-agente`) — o frontmatter pode diferir, o prompt não.");
    }

    [Fact]
    public void Both_Directories_Contain_Exactly_The_Mapped_Agents()
    {
        var claude = Directory.GetFiles(ClaudeDir, "*.md")
            .Select(Path.GetFileNameWithoutExtension)
            .OrderBy(n => n).ToList();

        var copilot = Directory.GetFiles(CopilotDir, "*.agent.md")
            .Select(f => Path.GetFileName(f)!.Replace(".agent.md", string.Empty))
            .OrderBy(n => n).ToList();

        Assert.Equal(AgentPairs.Keys.OrderBy(n => n), claude);
        Assert.Equal(AgentPairs.Values.OrderBy(n => n), copilot);
    }

    /// <summary>
    /// Um agente sem `model:` roda no modelo da conversa pai — o que para prompts longos
    /// como o do @GameArchitect (579 linhas) é uma escolha cara feita por omissão.
    /// </summary>
    [Theory]
    [MemberData(nameof(Pairs))]
    public void Claude_Agent_Declares_A_Model(string claudeName, string copilotName)
    {
        _ = copilotName;
        var lines = File.ReadAllLines(Path.Combine(ClaudeDir, $"{claudeName}.md"));
        var frontmatterEnd = Array.FindIndex(lines, 1, l => l.Trim() == "---");

        Assert.True(frontmatterEnd > 0, $"Frontmatter malformado em {claudeName}.md");
        Assert.Contains(lines[1..frontmatterEnd], l => l.StartsWith("model:", StringComparison.Ordinal));
    }
}
