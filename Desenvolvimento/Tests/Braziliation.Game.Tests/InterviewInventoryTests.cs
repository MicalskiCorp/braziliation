using System.Text.RegularExpressions;
using Xunit;

namespace Braziliation.Game.Tests;

/// <summary>
/// Em 2026-10-11 a curadoria da visita ao Teatro Carlos Gomes resumiu ~62 min de áudio direto em
/// texto de pesquisa e deixou 12 assuntos de fora — e nada acusou: assunto excluído por decisão e
/// assunto esquecido não deixavam rastro nenhum. O inventário em
/// <c>Design/Pesquisa/Entrevistas/Inventarios/</c> dá destino a cada bloco da transcrição; estes
/// testes conferem que nenhum bloco ficou sem linha e que o que o inventário diz estar na pesquisa
/// (✅) ou no TODO (🔎) está de fato lá.
/// </summary>
public sealed class InterviewInventoryTests
{
    private static string GitRoot => RepoRootFinder.FindGitRoot();

    private static readonly Regex BlockId = new(@"^([A-Z]\d+)\.(\d{2})$", RegexOptions.Compiled);

    [Fact]
    public void Every_Inventory_Covers_All_Blocks_And_Its_Keys_Are_In_The_Destination()
    {
        var dir = Path.Combine(GitRoot, "Design", "Pesquisa", "Entrevistas", "Inventarios");
        var inventories = Directory.Exists(dir)
            ? Directory.EnumerateFiles(dir, "*.md").Where(f => Path.GetFileName(f) != "index.md").ToList()
            : new List<string>();

        var problems = inventories
            .SelectMany(f => Problems(File.ReadAllText(f), ReadRepoFile)
                .Select(p => $"{Path.GetFileName(f)}: {p}"))
            .ToList();

        Assert.True(problems.Count == 0, "Inventário de entrevista com furos:\n" + string.Join("\n", problems));
    }

    /// <summary>
    /// Material chega picado e intercalado (a benzedeira, uma visita, a benzedeira de novo). Cada
    /// sessão pertence a um assunto registrado em <c>Entrevistas/Assuntos/</c>, que lista a sessão de
    /// volta — e uma mesma captura nunca é curada em dois inventários, que é como os assuntos se
    /// misturariam sem ninguém notar.
    /// </summary>
    [Fact]
    public void Every_Inventory_Belongs_To_One_Registered_Subject_And_No_Capture_Is_Shared()
    {
        var root = Path.Combine(GitRoot, "Design", "Pesquisa", "Entrevistas");
        var dir = Path.Combine(root, "Inventarios");
        if (!Directory.Exists(dir))
            return;

        var problems = new List<string>();
        var owner = new Dictionary<string, string>();
        foreach (var file in Directory.EnumerateFiles(dir, "*.md").Where(f => Path.GetFileName(f) != "index.md"))
        {
            var name = Path.GetFileName(file);
            var text = File.ReadAllText(file);

            var subject = Regex.Match(text, @"Assunto:\s*\[([^\]]+)\]\(\.\./Assuntos/([^)]+\.md)\)");
            if (!subject.Success)
                problems.Add($"{name}: falta a linha '> Assunto: [slug](../Assuntos/slug.md)'");
            else
            {
                var page = Path.Combine(root, "Assuntos", subject.Groups[2].Value);
                if (!File.Exists(page))
                    problems.Add($"{name}: página de assunto {subject.Groups[2].Value} não existe");
                else if (!File.ReadAllText(page).Contains(name, StringComparison.Ordinal))
                    problems.Add($"{name}: a página {subject.Groups[2].Value} não lista esta sessão");
                if (!name.EndsWith($"-{subject.Groups[1].Value}.md", StringComparison.Ordinal))
                    problems.Add($"{name}: o nome do arquivo deve terminar com o slug do assunto ({subject.Groups[1].Value})");
            }

            foreach (var cells in TableRows(text, "Trechos").Where(c => c.Length >= 2))
            {
                var folder = cells[1].Trim('`');
                if (owner.TryGetValue(folder, out var other))
                    problems.Add($"captura {folder} aparece em {other} e em {name} — uma captura é de um assunto só");
                else
                    owner[folder] = name;
            }
        }

        Assert.True(problems.Count == 0, "Assuntos das entrevistas misturados ou sem registro:\n" + string.Join("\n", problems));
    }

    /// <summary>
    /// O assunto de uma captura é detectado pelo conteúdo, comparado às palavras-chave de cada página
    /// (`curadoria.py triagem`). Página sem palavras-chave nunca é sugerida — o material do assunto
    /// cairia como "assunto novo" e ganharia uma segunda página.
    /// </summary>
    [Fact]
    public void Every_Subject_Page_Has_Keywords_For_Detection()
    {
        var dir = Path.Combine(GitRoot, "Design", "Pesquisa", "Entrevistas", "Assuntos");
        if (!Directory.Exists(dir))
            return;

        var missing = Directory.EnumerateFiles(dir, "*.md")
            .Where(f => Path.GetFileName(f) != "index.md")
            .Where(f => !Regex.IsMatch(File.ReadAllText(f), @"Palavras-chave:[^;\n]*\S[^;\n]*;[^;\n]*\S"))
            .Select(Path.GetFileName)
            .ToList();

        Assert.True(missing.Count == 0,
            "Página de assunto sem '> Palavras-chave: a; b; …' (pelo menos duas):\n" + string.Join("\n", missing));
    }

    /// <summary>
    /// A fala de quem foi entrevistado vale pelos trejeitos ("não te arcança", "nas onda do mar",
    /// "creio em cruz") — é a voz dos personagens. Em 2026-10-12 a primeira revisão da benzedeira
    /// normalizou a reza para o português padrão. Toda pesquisa com tabela "Trejeitos da fala" tem o
    /// texto acima dela conferido: a forma dela precisa estar lá, e a forma comum não pode aparecer —
    /// uma "correção" de uma única ocorrência já falha.
    /// </summary>
    [Fact]
    public void Speech_Mannerisms_Are_Not_Normalized()
    {
        var problems = new List<string>();
        foreach (var file in Directory.EnumerateFiles(Path.Combine(GitRoot, "Design", "Pesquisa"), "*.md", SearchOption.AllDirectories))
        {
            var text = File.ReadAllText(file);
            var table = text.IndexOf("## Trejeitos da fala", StringComparison.Ordinal);
            if (table < 0)
                continue;
            var speech = Regex.Replace(text[..table], @"\s+", " ");
            var name = Path.GetFileName(file);
            var rows = TableRows(text[table..], "Trejeitos da fala (não corrigir)").ToList();
            if (rows.Count == 0)
                problems.Add($"{name}: tabela 'Trejeitos da fala (não corrigir)' vazia ou ilegível");
            foreach (var cells in rows)
            {
                if (cells.Length < 4)
                {
                    problems.Add($"{name}: linha de trejeito sem a coluna 'Não pode aparecer na fala': {cells[0]}");
                    continue;
                }
                var theirs = cells[0];
                if (!speech.Contains(theirs, StringComparison.OrdinalIgnoreCase))
                    problems.Add($"{name}: o trejeito '{theirs}' sumiu da fala");
                // A última coluna traz o fragmento mínimo que denuncia a normalização ("alcan" pega
                // "alcança", "alcancem" e "alcançarão"); a frase canônica inteira deixaria escapar
                // uma correção parcial.
                foreach (var fragment in cells[3].Split(';').Select(f => f.Trim()).Where(f => f.Length > 0 && f != "—"))
                    if (speech.Contains(fragment, StringComparison.OrdinalIgnoreCase))
                        problems.Add($"{name}: a fala foi normalizada — aparece '{fragment}' (ela diz '{theirs}')");
            }
        }

        Assert.True(problems.Count == 0, "Trejeitos da fala corrigidos:\n" + string.Join("\n", problems.Distinct()));
    }

    [Fact]
    public void A_Block_Without_A_Row_Is_Reported()
    {
        var inventory = Inventory(blocks: 3, rows: "| 1 | A1.01, A1.03 | Assunto | — | motivo | ⛔ |");

        Assert.Contains(Problems(inventory, _ => ""), p => p.Contains("A1.02"));
    }

    [Fact]
    public void A_Key_Missing_From_The_Destination_Is_Reported()
    {
        var inventory = Inventory(blocks: 1, rows: "| 1 | A1.01 | Assunto | palco giratório; túnel | V | ✅ |");

        var problems = Problems(inventory, _ => "Texto da pesquisa sobre o palco giratório.");

        Assert.Contains(problems, p => p.Contains("túnel"));
        Assert.DoesNotContain(problems, p => p.Contains("palco giratório"));
    }

    [Fact]
    public void An_Exclusion_Without_A_Reason_Is_Reported()
    {
        var inventory = Inventory(blocks: 1, rows: "| 1 | A1.01 | Assunto | — |  | ⛔ |");

        Assert.Contains(Problems(inventory, _ => ""), p => p.Contains("sem motivo"));
    }

    private static string Inventory(int blocks, string rows) =>
        "## Trechos\n\n| Trecho | Pasta | Blocos |\n|---|---|---|\n" +
        $"| A1 | `pasta` | {blocks} |\n\n" +
        "## Destinos\n\n| Sigla | Arquivo |\n|---|---|\n| V | `pesquisa.md` |\n\n" +
        "## Assuntos\n\n| # | Blocos | Assunto | Chaves | Destino | Status |\n|---|---|---|---|---|---|\n" +
        rows + "\n";

    private static string? ReadRepoFile(string relativePath)
    {
        var path = Path.Combine(GitRoot, relativePath.Replace('/', Path.DirectorySeparatorChar));
        return File.Exists(path) ? File.ReadAllText(path) : null;
    }

    /// <summary>Problemas de um inventário. <paramref name="readFile"/> devolve o texto do destino ou null.</summary>
    internal static List<string> Problems(string inventory, Func<string, string?> readFile)
    {
        var problems = new List<string>();

        var expected = new List<string>();
        foreach (var cells in TableRows(inventory, "Trechos"))
        {
            if (cells.Length < 3 || !int.TryParse(cells[2], out var count))
            {
                problems.Add($"linha de trecho ilegível: {string.Join(" | ", cells)}");
                continue;
            }
            expected.AddRange(Enumerable.Range(1, count).Select(i => $"{cells[0]}.{i:00}"));
        }
        if (expected.Count == 0)
            problems.Add("nenhum trecho declarado na tabela Trechos");

        var destinations = TableRows(inventory, "Destinos")
            .Where(c => c.Length >= 2)
            .ToDictionary(c => c[0], c => c[1].Trim('`'));

        var covered = new HashSet<string>();
        foreach (var cells in TableRows(inventory, "Assuntos"))
        {
            if (cells.Length < 6)
            {
                problems.Add($"linha de assunto ilegível: {string.Join(" | ", cells)}");
                continue;
            }
            var (row, blocks, keys, destination, status) = (cells[0], cells[1], cells[3], cells[4], cells[5]);

            foreach (var id in ExpandBlocks(blocks))
            {
                if (!expected.Contains(id))
                    problems.Add($"linha {row}: bloco {id} não existe na tabela Trechos");
                covered.Add(id);
            }

            switch (status)
            {
                case "⛔":
                    if (string.IsNullOrWhiteSpace(destination))
                        problems.Add($"linha {row}: ⛔ sem motivo na coluna Destino");
                    break;
                case "✅":
                case "🔎":
                    if (!destinations.TryGetValue(destination, out var file))
                    {
                        problems.Add($"linha {row}: destino '{destination}' não está na tabela Destinos");
                        break;
                    }
                    var text = readFile(file);
                    if (text == null)
                    {
                        problems.Add($"linha {row}: arquivo de destino {file} não existe");
                        break;
                    }
                    var keyList = keys.Split(';').Select(k => k.Trim()).Where(k => k.Length > 0 && k != "—").ToList();
                    if (keyList.Count == 0)
                        problems.Add($"linha {row}: {status} sem chaves para conferir");
                    problems.AddRange(keyList
                        .Where(k => !text.Contains(k, StringComparison.OrdinalIgnoreCase))
                        .Select(k => $"linha {row}: chave '{k}' não aparece em {file}"));
                    break;
                default:
                    problems.Add($"linha {row}: status '{status}' — use ✅, 🔎 ou ⛔");
                    break;
            }
        }

        problems.AddRange(expected.Where(id => !covered.Contains(id))
            .Select(id => $"bloco {id} sem nenhuma linha no inventário"));
        return problems;
    }

    /// <summary>"A1.01, A1.03–A1.05" → A1.01, A1.03, A1.04, A1.05.</summary>
    private static IEnumerable<string> ExpandBlocks(string cell)
    {
        foreach (var part in cell.Split(',').Select(p => p.Trim()).Where(p => p.Length > 0))
        {
            var ends = part.Split('–', '-').Select(e => e.Trim()).ToArray();
            var first = BlockId.Match(ends[0]);
            var last = BlockId.Match(ends[^1]);
            if (!first.Success || !last.Success || first.Groups[1].Value != last.Groups[1].Value)
            {
                yield return part;
                continue;
            }
            for (var i = int.Parse(first.Groups[2].Value); i <= int.Parse(last.Groups[2].Value); i++)
                yield return $"{first.Groups[1].Value}.{i:00}";
        }
    }

    /// <summary>Linhas de dados da tabela logo abaixo de "## {section}", já sem cabeçalho e separador.</summary>
    private static IEnumerable<string[]> TableRows(string markdown, string section)
    {
        var lines = markdown.Split('\n').Select(l => l.TrimEnd('\r')).ToList();
        var start = lines.FindIndex(l => l.Trim() == $"## {section}");
        if (start < 0)
            yield break;

        var table = lines.Skip(start + 1)
            .SkipWhile(l => !l.TrimStart().StartsWith('|'))
            .TakeWhile(l => l.TrimStart().StartsWith('|'))
            .Skip(2);
        foreach (var line in table)
            yield return line.Trim().Trim('|').Split('|').Select(c => c.Trim()).ToArray();
    }
}
