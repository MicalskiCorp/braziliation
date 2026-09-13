using System.Text.Json;
using Xunit;

namespace Braziliation.Game.Tests;

/// <summary>
/// Convenções que viviam só em prompt de agente e em checklist de auditoria
/// (skills validar-todos e structure-audit). Viraram teste para não depender de
/// alguém rodar a auditoria — e para a auditoria não gastar tokens com o que é mecânico.
/// </summary>
public sealed class ConventionGuardTests
{
    private static string UnityRoot => RepoRootFinder.FindRepositoryRoot();
    private static string GitRoot => RepoRootFinder.FindGitRoot();

    /// <summary>"Todo serviço (*Service.cs) deve ter arquivo de teste dedicado" — validar-todos, passo C.</summary>
    [Fact]
    public void Every_Core_Service_Has_A_Dedicated_Test_File()
    {
        var tests = Directory.EnumerateFiles(Path.Combine(UnityRoot, "Tests", "Braziliation.Game.Tests"), "*.cs")
            .Select(Path.GetFileNameWithoutExtension)
            .ToHashSet(StringComparer.Ordinal);

        var missing = Directory.EnumerateFiles(Path.Combine(UnityRoot, "src", "Braziliation.Game.Core"), "*Service.cs", SearchOption.AllDirectories)
            .Where(f => !f.Split(Path.DirectorySeparatorChar).Any(p => p is "bin" or "obj"))
            .Select(Path.GetFileNameWithoutExtension)
            .Where(name => !tests.Contains($"{name}Tests"))
            .ToList();

        Assert.True(missing.Count == 0, "Serviços sem {Nome}Tests.cs: " + string.Join(", ", missing));
    }

    /// <summary>"Paletas JSON com status definido" — structure-audit, nível 2.</summary>
    [Fact]
    public void Every_Region_Palette_Declares_A_Status()
    {
        var dir = Path.Combine(GitRoot, "Design", "ArteConceitual", "Paletas");
        var missing = Directory.EnumerateFiles(dir, "*.json")
            .Where(f => Path.GetFileName(f) != "regras-assets.json") // regras do gate, não é paleta
            .Where(f =>
            {
                using var doc = JsonDocument.Parse(File.ReadAllText(f));
                return !doc.RootElement.TryGetProperty("status", out var s)
                       || s.ValueKind != JsonValueKind.String
                       || string.IsNullOrWhiteSpace(s.GetString());
            })
            .Select(Path.GetFileName)
            .ToList();

        Assert.True(missing.Count == 0,
            "Paletas sem \"status\" (proposta-inicial | aprovada): " + string.Join(", ", missing));
    }
}
