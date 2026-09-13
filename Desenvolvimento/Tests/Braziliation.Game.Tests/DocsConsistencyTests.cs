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

    internal static IEnumerable<string> MarkdownFiles()
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

    /// <summary>
    /// As fichas de Sistemas/ são o índice de scripts. Antes havia um índice paralelo
    /// (indices/sistemas.md) mantido à mão que chegou a listar 18 de 71 scripts — e era o
    /// último passo do fluxo de leitura dos agentes.
    /// </summary>
    [Fact]
    public void Every_Script_Is_Listed_In_A_System_Page()
    {
        var sistemas = Path.Combine(UnityRoot, "Docs", "Architecture", "Sistemas");
        var fichas = string.Concat(Directory.EnumerateFiles(sistemas, "*.md").Select(File.ReadAllText));

        var roots = new[]
        {
            Path.Combine(UnityRoot, "Assets", "Scripts"),
            Path.Combine(UnityRoot, "Assets", "Editor"),
            Path.Combine(UnityRoot, "src", "Braziliation.Game.Core"),
        };

        var missing = roots
            .SelectMany(root => Directory.EnumerateFiles(root, "*.cs", SearchOption.AllDirectories))
            .Where(f => !f.Split(Path.DirectorySeparatorChar).Any(part => part is "bin" or "obj"))
            .Select(Path.GetFileName)
            .Where(name => !fichas.Contains($"`{name}`", StringComparison.Ordinal))
            .OrderBy(name => name)
            .ToList();

        Assert.True(missing.Count == 0,
            "Scripts sem linha na \"Fontes Técnicas\" de nenhuma ficha em Docs/Architecture/Sistemas/: " +
            string.Join(", ", missing));
    }

    /// <summary>Era o passo manual "features × backlog" da varredura do @GameArchitect.</summary>
    [Fact]
    public void Every_Feature_Is_Listed_In_Features_Index_And_Backlog()
    {
        var features = Path.Combine(UnityRoot, "Docs", "GDD", "Features");
        var index = File.ReadAllText(Path.Combine(features, "index.md"));
        var backlog = File.ReadAllText(Path.Combine(UnityRoot, "Docs", "Roadmap", "backlog.md"));

        var problems = Directory.EnumerateFiles(features, "*.md")
            .Select(Path.GetFileName)
            .Where(name => name != "index.md")
            .SelectMany(name => new[]
            {
                index.Contains(name, StringComparison.Ordinal) ? null : $"{name} fora do Features/index.md",
                backlog.Contains(name, StringComparison.Ordinal) ? null : $"{name} fora do Roadmap/backlog.md",
            })
            .Where(p => p is not null)
            .ToList();

        Assert.True(problems.Count == 0, string.Join("\n", problems));
    }

    /// <summary>Pastas de conteúdo por asset (um pacote por asset/tema), não roteadas por índice.</summary>
    private static readonly string[] AssetFolderPrefixes =
    {
        "Design/ArteFonte/IA/ContextPacks/",
        "Design/ArteConceitual/ReferenciasVisuais/",
    };

    /// <summary>Arquivos de operação conhecidos por nome — não precisam de linha no roteador.</summary>
    private static readonly HashSet<string> RouterExempt = new(StringComparer.Ordinal) { "TODO.md", "TODO-arquivo.md" };

    /// <summary>
    /// A navegação por índice só economiza tokens se o índice for completo: arquivo que o
    /// index.md da pasta não lista só é achado por busca. Era checagem manual da skill
    /// structure-audit (níveis 2 e 3) e do Modo 4 do @GameArchitect.
    /// </summary>
    [Fact]
    public void Every_Markdown_Folder_Has_A_Complete_Router()
    {
        var problems = new List<string>();
        foreach (var dir in MarkdownFiles().Select(Path.GetDirectoryName).Distinct())
        {
            var rel = Relative(dir!) + "/";
            if (!(rel.StartsWith("Desenvolvimento/Docs/") || rel.StartsWith("Design/")) || AssetFolderPrefixes.Any(rel.StartsWith))
                continue;

            var siblings = Directory.EnumerateFiles(dir!, "*.md").Select(Path.GetFileName)
                .Where(n => n != "index.md" && !RouterExempt.Contains(n!)).ToList();
            var indexPath = Path.Combine(dir!, "index.md");

            if (!File.Exists(indexPath))
            {
                if (siblings.Count > 1)
                    problems.Add($"{rel} tem {siblings.Count} arquivos .md e nenhum index.md");
                continue;
            }

            var index = File.ReadAllText(indexPath);
            problems.AddRange(siblings
                .Where(n => !index.Contains($"({n}", StringComparison.Ordinal) && !index.Contains($"`{n}`", StringComparison.Ordinal))
                .Select(n => $"{rel}{n} não aparece no index.md da pasta"));
        }

        Assert.True(problems.Count == 0, "Roteadores incompletos:\n" + string.Join("\n", problems));
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

    /// <summary>
    /// O catálogo saiu do AGENTS.md (que entra em toda sessão) para Tech/processos.md,
    /// lido sob demanda. Continua obrigatório listar toda skill.
    /// </summary>
    [Fact]
    public void Every_Skill_Is_Listed_In_Process_Catalog()
    {
        var catalog = File.ReadAllText(Path.Combine(UnityRoot, "Docs", "Tech", "processos.md"));
        var missing = Directory.EnumerateDirectories(Path.Combine(GitRoot, ".claude", "skills"))
            .Select(Path.GetFileName)
            .Where(name => !catalog.Contains($"`{name}`", StringComparison.Ordinal))
            .ToList();

        Assert.True(missing.Count == 0,
            "Skills sem linha no catálogo de Desenvolvimento/Docs/Tech/processos.md: " + string.Join(", ", missing));
    }
}
