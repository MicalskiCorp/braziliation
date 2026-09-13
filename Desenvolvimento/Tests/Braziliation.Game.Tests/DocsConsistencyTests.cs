using System.Text.RegularExpressions;
using Xunit;

namespace Braziliation.Game.Tests;

/// <summary>
/// A documentação é lida por agentes como verdade. Documentação desatualizada não gera
/// erro — gera agente seguindo instrução errada. Em 2026-09 havia ~18 contradições entre
/// docs e código. Estes testes transformam as mais recorrentes em falha de build.
/// </summary>
public sealed class DocsConsistencyTests
{
    private static string GitRoot => RepoRootFinder.FindGitRoot();
    private static string UnityRoot => RepoRootFinder.FindRepositoryRoot();

    /// <summary>Pastas que não são documentação do projeto (geradas, de terceiros ou saída de IA).</summary>
    private static readonly HashSet<string> SkippedDirectoryNames = new(StringComparer.OrdinalIgnoreCase)
    {
        ".git", "Library", "Temp", "Logs", "obj", "bin", "UserSettings", ".vs", "node_modules",
        "TextMesh Pro", "Outputs", "Rejected",
    };

    private static IEnumerable<string> MarkdownFiles()
    {
        var pending = new Stack<string>();
        pending.Push(GitRoot);
        while (pending.Count > 0)
        {
            var dir = pending.Pop();
            foreach (var sub in Directory.EnumerateDirectories(dir))
                if (!SkippedDirectoryNames.Contains(Path.GetFileName(sub)))
                    pending.Push(sub);
            foreach (var file in Directory.EnumerateFiles(dir, "*.md"))
                yield return file;
        }
    }

    private static string Relative(string path) => Path.GetRelativePath(GitRoot, path).Replace('\\', '/');

    [Fact]
    public void Retired_Test_Folder_Is_Not_Referenced_In_Markdown()
    {
        // Histórico pode citar a pasta aposentada; instrução viva não.
        var allowed = new HashSet<string> { "Desenvolvimento/CHANGELOG.md", "Desenvolvimento/Docs/TODO-arquivo.md" };

        var offenders = MarkdownFiles()
            .Where(f => !allowed.Contains(Relative(f)))
            .Where(f => File.ReadAllText(f).Contains("dotnet-tests", StringComparison.Ordinal))
            .Select(Relative)
            .ToList();

        Assert.True(offenders.Count == 0,
            "Instruções apontando para a pasta de testes aposentada (o CI roda Desenvolvimento/Tests/): " +
            string.Join(", ", offenders));
    }

    private static readonly Regex MarkdownLink = new(@"\[[^\]]*\]\(([^)\s]+)(?:\s+""[^""]*"")?\)", RegexOptions.Compiled);
    private static readonly Regex FencedCode = new(@"```.*?```", RegexOptions.Singleline | RegexOptions.Compiled);
    private static readonly Regex InlineCode = new(@"`[^`\n]*`", RegexOptions.Compiled);
    private static readonly Regex UriScheme = new(@"^[a-zA-Z][a-zA-Z0-9+.-]*:", RegexOptions.Compiled);

    [Fact]
    public void Relative_Markdown_Links_Resolve()
    {
        // Templates usam placeholders ({Nome}.md) de propósito.
        var templateDirs = new[] { "Desenvolvimento/Docs/Models/", "Design/Models/" };
        var broken = new List<string>();

        foreach (var file in MarkdownFiles())
        {
            var rel = Relative(file);
            if (templateDirs.Any(rel.StartsWith))
                continue;

            var text = InlineCode.Replace(FencedCode.Replace(File.ReadAllText(file), string.Empty), string.Empty);
            foreach (Match match in MarkdownLink.Matches(text))
            {
                var target = match.Groups[1].Value;
                if (UriScheme.IsMatch(target) || target.StartsWith('#') || target.Contains('{'))
                    continue;

                target = Uri.UnescapeDataString(target.Split('#')[0]);
                if (target.Length == 0)
                    continue;

                var resolved = Path.GetFullPath(Path.Combine(Path.GetDirectoryName(file)!, target));
                if (!File.Exists(resolved) && !Directory.Exists(resolved))
                    broken.Add($"{rel} → {target}");
            }
        }

        Assert.True(broken.Count == 0, "Links relativos quebrados:\n" + string.Join("\n", broken));
    }

    [Fact]
    public void Every_Scripts_Folder_Is_Documented_In_AssetsStructure()
    {
        var doc = File.ReadAllText(Path.Combine(UnityRoot, "Docs", "Architecture", "Assets", "AssetsStructure.md"));
        var missing = Directory.EnumerateDirectories(Path.Combine(UnityRoot, "Assets", "Scripts"))
            .Select(Path.GetFileName)
            .Where(name => !doc.Contains($"{name}/", StringComparison.Ordinal))
            .ToList();

        Assert.True(missing.Count == 0,
            "Pastas de Assets/Scripts sem entrada em AssetsStructure.md: " + string.Join(", ", missing));
    }

    [Fact]
    public void Every_Core_Folder_Has_A_System_Page()
    {
        var sistemas = Path.Combine(UnityRoot, "Docs", "Architecture", "Sistemas");
        var index = File.ReadAllText(Path.Combine(sistemas, "index.md"));

        var missing = Directory.EnumerateDirectories(Path.Combine(UnityRoot, "src", "Braziliation.Game.Core"))
            .Select(Path.GetFileName)
            .Where(name => name is not ("bin" or "obj"))
            .Where(name => !File.Exists(Path.Combine(sistemas, $"{name}.md")) || !index.Contains($"({name}.md)", StringComparison.Ordinal))
            .ToList();

        Assert.True(missing.Count == 0,
            "Namespaces do core sem página (ou sem linha no índice) em Docs/Architecture/Sistemas/: " + string.Join(", ", missing));
    }

    [Fact]
    public void Superseded_Adrs_Name_Their_Replacement()
    {
        var text = File.ReadAllText(Path.Combine(UnityRoot, "Docs", "Architecture", "architecture_decisions.md"));
        var problems = new List<string>();

        foreach (Match adr in Regex.Matches(text, @"^## (ADR-\d{3}).*?(?=^## |\z)", RegexOptions.Multiline | RegexOptions.Singleline))
        {
            var id = adr.Groups[1].Value;
            var status = Regex.Match(adr.Value, @"\*\*Status:\*\*(.*?)(?=\n- \*\*|\z)", RegexOptions.Singleline).Groups[1].Value;
            var superseded = status.Contains("Superseded", StringComparison.OrdinalIgnoreCase)
                             || status.Contains("Substituí", StringComparison.OrdinalIgnoreCase);
            if (!superseded)
                continue;

            var replacement = Regex.Matches(status, @"ADR-\d{3}").Select(m => m.Value).Where(r => r != id);
            if (!replacement.Any())
                problems.Add(id);
        }

        Assert.True(problems.Count == 0, "ADR substituído sem indicar o substituto: " + string.Join(", ", problems));
    }

    [Fact]
    public void Every_Skill_Is_Listed_In_Agents_Catalog()
    {
        var catalog = File.ReadAllText(Path.Combine(GitRoot, "AGENTS.md"));
        var missing = Directory.EnumerateDirectories(Path.Combine(GitRoot, ".claude", "skills"))
            .Select(Path.GetFileName)
            .Where(name => !catalog.Contains($"`{name}`", StringComparison.Ordinal))
            .ToList();

        Assert.True(missing.Count == 0, "Skills sem linha no catálogo do AGENTS.md: " + string.Join(", ", missing));
    }
}
