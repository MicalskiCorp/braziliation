using System.Text.RegularExpressions;
using Xunit;

namespace Braziliation.Game.Tests;

/// <summary>
/// Tudo que um agente lê custa contexto. Em 2026-09 o @GameArchitect definia orçamentos de
/// tamanho no próprio prompt — e passava deles; o AGENTS.md entrava em toda sessão com
/// ~3,7 mil tokens; o @AgentArchitect lia ~34 mil tokens antes de trabalhar. Orçamento
/// escrito e não verificado não segura nada: estes testes são o orçamento.
///
/// Estimativa: bytes UTF-8 ÷ 4 — conservadora para português.
/// </summary>
public sealed class TokenBudgetTests
{
    private const int AgentPromptBudget = 5_000;
    private const int SessionContextBudget = 2_500;
    private const int RouterIndexBudget = 1_500;
    private const int DocumentBudget = 5_000;

    /// <summary>Arquivos que podem passar do teto geral. Cada um com o motivo.</summary>
    private static readonly Dictionary<string, string> DocumentExceptions = new()
    {
        ["Desenvolvimento/Docs/TODO-arquivo.md"] = "histórico congelado, fora do caminho de leitura dos agentes",
        ["Design/Criativo/Estados/SantaCatarina/cidades/Blumenau/index.md"] = "dívida registrada: dividir a ficha da cidade por seção",
        ["Design/GuiasDeArte/pipeline-ia-sprites.md"] = "dívida registrada: dividir o guia por rota",
    };

    /// <summary>`lotes.md` de context pack é log de geração: cresce por lote, é lido por trecho.</summary>
    private static readonly Regex GenerationLog = new(@"^Design/ArteFonte/IA/ContextPacks/[^/]+/lotes\.md$", RegexOptions.Compiled);

    /// <summary>Ficha de cidade usa index.md como conteúdo (template ModelCidade), não como roteador.</summary>
    private static readonly Regex CityFile = new(@"/cidades/[^/]+/index\.md$", RegexOptions.Compiled);

    private static string GitRoot => RepoRootFinder.FindGitRoot();
    private static string Relative(string path) => Path.GetRelativePath(GitRoot, path).Replace('\\', '/');
    private static long Tokens(string path) => new FileInfo(path).Length / 4;

    private static string Report(IEnumerable<string> items) => string.Join("\n", items);

    [Fact]
    public void Agent_Prompts_Fit_Budget()
    {
        var over = Directory.EnumerateFiles(Path.Combine(GitRoot, ".claude", "agents"), "*.md")
            .Where(f => Tokens(f) > AgentPromptBudget)
            .Select(f => $"{Relative(f)}: ~{Tokens(f)} tokens")
            .ToList();

        Assert.True(over.Count == 0,
            $"Prompt de agente acima de {AgentPromptBudget} tokens — mover detalhe para skill ou doc lido sob demanda:\n{Report(over)}");
    }

    [Fact]
    public void Session_Context_Fits_Budget()
    {
        var total = Tokens(Path.Combine(GitRoot, "CLAUDE.md")) + Tokens(Path.Combine(GitRoot, "AGENTS.md"));

        Assert.True(total <= SessionContextBudget,
            $"CLAUDE.md + AGENTS.md somam ~{total} tokens (teto {SessionContextBudget}) e entram em toda sessão. " +
            "Detalhe de processo vai para Desenvolvimento/Docs/Tech/processos.md.");
    }

    [Fact]
    public void Router_Indexes_Fit_Budget()
    {
        var over = DocsConsistencyTests.MarkdownFiles()
            .Where(f => Path.GetFileName(f) == "index.md")
            .Where(f => !CityFile.IsMatch(Relative(f)))
            .Where(f => Tokens(f) > RouterIndexBudget)
            .Select(f => $"{Relative(f)}: ~{Tokens(f)} tokens")
            .ToList();

        Assert.True(over.Count == 0,
            $"index.md roteador acima de {RouterIndexBudget} tokens — roteador lista e linka, o conteúdo vai para arquivo próprio:\n{Report(over)}");
    }

    [Fact]
    public void Markdown_Documents_Fit_Budget()
    {
        var over = DocsConsistencyTests.MarkdownFiles()
            .Select(f => (Path: f, Rel: Relative(f)))
            .Where(x => !DocumentExceptions.ContainsKey(x.Rel) && !GenerationLog.IsMatch(x.Rel))
            .Where(x => Tokens(x.Path) > DocumentBudget)
            .Select(x => $"{x.Rel}: ~{Tokens(x.Path)} tokens")
            .ToList();

        Assert.True(over.Count == 0,
            $"Documento acima de {DocumentBudget} tokens — dividir por seção com um index.md, " +
            $"ou registrar a exceção com motivo em {nameof(DocumentExceptions)}:\n{Report(over)}");
    }

    /// <summary>Exceção que deixou de ser necessária sai da lista — senão a lista só cresce.</summary>
    [Fact]
    public void Document_Exceptions_Are_Still_Needed()
    {
        var stale = DocumentExceptions.Keys
            .Where(rel => !File.Exists(Path.Combine(GitRoot, rel)) || Tokens(Path.Combine(GitRoot, rel)) <= DocumentBudget)
            .ToList();

        Assert.True(stale.Count == 0,
            "Exceções de orçamento que já não se aplicam (arquivo sumiu ou cabe no teto) — remover da lista: " +
            string.Join(", ", stale));
    }
}
