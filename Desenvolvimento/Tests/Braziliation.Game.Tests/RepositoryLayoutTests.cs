using System.Text.RegularExpressions;
using NUnit.Framework;

namespace Braziliation.Game.Tests;

/// <summary>
/// Testes sem Unity: validam o layout do repositório e artefatos que o CI/GitHub dependem.
/// </summary>
[TestFixture]
public sealed class RepositoryLayoutTests
{
    [Test]
    public void UnityProjectVersion_File_Exists_And_Matches_Unity6()
    {
        var root = RepoRootFinder.FindRepositoryRoot();
        var path = Path.Combine(root, "ProjectSettings", "ProjectVersion.txt");
        Assert.That(File.Exists(path), Is.True, $"Esperado: {path}");

        var content = File.ReadAllText(path);
        Assert.That(content, Does.Contain("m_EditorVersion:"));

        var match = Regex.Match(content, @"m_EditorVersion:\s*(\S+)");
        Assert.That(match.Success, Is.True, "Não foi possível ler m_EditorVersion no ProjectVersion.txt");
        var version = match.Groups[1].Value;
        Assert.That(
            version.StartsWith("6000", StringComparison.Ordinal)
            || version.StartsWith("6.", StringComparison.Ordinal),
            Is.True,
            $"Versão do editor deveria ser Unity 6 (6000.x); obtido: {version}");
    }

    [Test]
    public void Asset_GameScripts_GameInitializer_Exists()
    {
        var root = RepoRootFinder.FindRepositoryRoot();
        var path = Path.Combine(root, "Assets", "Scripts", "Core", "GameInitializer.cs");
        Assert.That(File.Exists(path), Is.True, "GameInitializer.cs deve existir para o jogo compilar no Unity");
    }

    [Test]
    public void Unity_Game_Solution_References_Assembly_CSharp()
    {
        var root = RepoRootFinder.FindRepositoryRoot();
        var path = Path.Combine(root, "Braziliation.slnx");
        Assert.That(File.Exists(path), Is.True, $"Esperado solução principal em: {path}");

        var text = File.ReadAllText(path);
        Assert.That(text, Does.Contain("Assembly-CSharp.csproj"),
            "Braziliation.slnx deve referenciar Assembly-CSharp.csproj (Unity)");
    }

    [Test]
    public void CiTestProject_Lives_Under_Tests()
    {
        var root = RepoRootFinder.FindRepositoryRoot();
        var path = Path.Combine(root, "Tests", "Braziliation.Game.Tests", "Braziliation.Game.Tests.csproj");
        Assert.That(File.Exists(path), Is.True,
            "O projeto de testes deve estar em Tests/Braziliation.Game.Tests/.");
    }

    [Test]
    public void CoreLibrary_Lives_Under_Src()
    {
        var root = RepoRootFinder.FindRepositoryRoot();
        var path = Path.Combine(root, "src", "Braziliation.Game.Core", "Braziliation.Game.Core.csproj");
        Assert.That(File.Exists(path), Is.True,
            "A biblioteca de produção deve estar em src/Braziliation.Game.Core/.");
    }
}
