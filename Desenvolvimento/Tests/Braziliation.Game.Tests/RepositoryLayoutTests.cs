using System.Text.RegularExpressions;
using Xunit;

namespace Braziliation.Game.Tests;

/// <summary>
/// Testes sem Unity: validam o layout do repositório e artefatos que o CI/GitHub dependem.
/// </summary>
public sealed class RepositoryLayoutTests
{
    [Fact]
    public void UnityProjectVersion_File_Exists_And_Matches_Unity6()
    {
        var root = RepoRootFinder.FindRepositoryRoot();
        var path = Path.Combine(root, "ProjectSettings", "ProjectVersion.txt");
        Assert.True(File.Exists(path), $"Esperado: {path}");

        var content = File.ReadAllText(path);
        Assert.Contains("m_EditorVersion:", content);

        var match = Regex.Match(content, @"m_EditorVersion:\s*(\S+)");
        Assert.True(match.Success, "Não foi possível ler m_EditorVersion no ProjectVersion.txt");
        var version = match.Groups[1].Value;
        Assert.True(
            version.StartsWith("6000", StringComparison.Ordinal)
            || version.StartsWith("6.", StringComparison.Ordinal),
            $"Versão do editor deveria ser Unity 6 (6000.x); obtido: {version}");
    }

    [Fact]
    public void Asset_GameScripts_GameInitializer_Exists()
    {
        var root = RepoRootFinder.FindRepositoryRoot();
        var path = Path.Combine(root, "Assets", "Scripts", "Core", "GameInitializer.cs");
        Assert.True(File.Exists(path), "GameInitializer.cs deve existir para o jogo compilar no Unity");
    }

    [Fact]
    public void Unity_Game_Solution_References_Assembly_CSharp()
    {
        var root = RepoRootFinder.FindRepositoryRoot();
        var path = Path.Combine(root, "Braziliation.slnx");
        Assert.True(File.Exists(path), $"Esperado solução principal em: {path}");

        var text = File.ReadAllText(path);
        Assert.Contains("Assembly-CSharp.csproj", text);
    }

    [Fact]
    public void CiTestProject_Lives_Under_Tests()
    {
        var root = RepoRootFinder.FindRepositoryRoot();
        var path = Path.Combine(root, "Tests", "Braziliation.Game.Tests", "Braziliation.Game.Tests.csproj");
        Assert.True(File.Exists(path),
            "O projeto de testes deve estar em Tests/Braziliation.Game.Tests/.");
    }

    [Fact]
    public void CoreLibrary_Lives_Under_Src()
    {
        var root = RepoRootFinder.FindRepositoryRoot();
        var path = Path.Combine(root, "src", "Braziliation.Game.Core", "Braziliation.Game.Core.csproj");
        Assert.True(File.Exists(path),
            "A biblioteca de produção deve estar em src/Braziliation.Game.Core/.");
    }

    // ── Guardas de regressão do CI ────────────────────────────────────────────
    // Motivo: o CI resolvia o projeto de teste por uma lista de CANDIDATES com
    // fallback e escolhia Desenvolvimento/dotnet-tests/ — um conjunto obsoleto de
    // 4 arquivos. Crafting, Build, HybridSynergy, EnemyBrain e Settings ficaram
    // sem cobertura em CI sem que nada falhasse. Estes testes travam isso.

    [Theory]
    [InlineData(".github/workflows/ci.yml")]
    [InlineData(".gitlab-ci.yml")]
    public void CiConfig_Targets_The_Real_Test_Project(string relativePath)
    {
        var path = Path.Combine(RepoRootFinder.FindGitRoot(), relativePath);
        Assert.True(File.Exists(path), $"Config de CI ausente: {path}");

        var text = File.ReadAllText(path);
        Assert.Contains(
            "Desenvolvimento/Tests/Braziliation.Game.Tests/Braziliation.Game.Tests.csproj",
            text);
    }

    [Theory]
    [InlineData(".github/workflows/ci.yml")]
    [InlineData(".gitlab-ci.yml")]
    public void CiConfig_Does_Not_Reference_Retired_DotnetTests_Folder(string relativePath)
    {
        var path = Path.Combine(RepoRootFinder.FindGitRoot(), relativePath);
        var text = File.ReadAllText(path);
        Assert.DoesNotContain("dotnet-tests", text);
    }
}
