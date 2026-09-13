using System.Diagnostics;
using Xunit;

namespace Braziliation.Game.Tests;

/// <summary>
/// Nenhum código-fonte pode cair numa regra do <c>.gitignore</c>.
///
/// Motivo: a regra <c>Build/</c> (sem âncora, pensada para a saída de player build do
/// Unity) casava também com <c>src/Braziliation.Game.Core/Build/</c> e
/// <c>Assets/Scripts/Build/</c>. Oito arquivos de código e seus <c>.meta</c> ficaram
/// fora do git por meses, o commit publicado não compilava, e nada falhava — o arquivo
/// ignorado continuava existindo no disco de quem o criou.
/// </summary>
public sealed class GitIgnoreGuardTests
{
    private static readonly string[] SourceRoots =
    {
        "Desenvolvimento/src",
        "Desenvolvimento/Tests",
        "Desenvolvimento/Assets/Scripts",
        "Desenvolvimento/Assets/Editor",
    };

    private static readonly string[] SourceSuffixes = { ".cs", ".cs.meta", ".csproj" };

    [Fact]
    public void No_Source_File_Is_Matched_By_GitIgnore()
    {
        var gitRoot = RepoRootFinder.FindGitRoot();
        var files = SourceRoots
            .Select(root => Path.Combine(gitRoot, root))
            .Where(Directory.Exists)
            .SelectMany(dir => Directory.EnumerateFiles(dir, "*", SearchOption.AllDirectories))
            .Select(file => Path.GetRelativePath(gitRoot, file).Replace('\\', '/'))
            .Where(IsSource)
            .Where(path => !IsBuildOutput(path))
            .ToList();

        Assert.NotEmpty(files);

        var ignored = RunCheckIgnore(gitRoot, files);

        Assert.True(
            ignored.Count == 0,
            "Código-fonte coberto por regra do .gitignore (nunca vai para o repositório): " +
            string.Join(", ", ignored) +
            ". Ancore a regra culpada — `git check-ignore -v <arquivo>` mostra qual é.");
    }

    private static bool IsSource(string path)
        => SourceSuffixes.Any(suffix => path.EndsWith(suffix, StringComparison.OrdinalIgnoreCase));

    /// <summary>bin/ e obj/ são saída de compilação: esses sim devem ser ignorados.</summary>
    private static bool IsBuildOutput(string path)
        => path.Split('/').Any(segment =>
            segment.Equals("bin", StringComparison.OrdinalIgnoreCase) ||
            segment.Equals("obj", StringComparison.OrdinalIgnoreCase));

    /// <summary>
    /// <c>--no-index</c> faz o git avaliar só as regras, inclusive para arquivos já
    /// rastreados — um arquivo commitado que uma regra nova passaria a ignorar também
    /// é pego aqui.
    /// </summary>
    private static List<string> RunCheckIgnore(string gitRoot, IReadOnlyList<string> files)
    {
        var startInfo = new ProcessStartInfo("git", "check-ignore --no-index --stdin")
        {
            WorkingDirectory = gitRoot,
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
        };

        using var process = Process.Start(startInfo)
            ?? throw new InvalidOperationException("Não foi possível executar o git.");

        // "\n" explícito: WriteLine usaria "\r\n" no Windows, o git leria o caminho com
        // um '\r' no fim, e regras por extensão (*.log) deixariam de casar.
        foreach (var file in files)
            process.StandardInput.Write(file + "\n");
        process.StandardInput.Close();

        var output = process.StandardOutput.ReadToEnd();
        var error = process.StandardError.ReadToEnd();
        process.WaitForExit();

        // 0 = algum arquivo ignorado, 1 = nenhum ignorado, qualquer outro = erro.
        Assert.True(
            process.ExitCode is 0 or 1,
            $"git check-ignore falhou (código {process.ExitCode}): {error}");

        return output
            .Split('\n', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .ToList();
    }
}
