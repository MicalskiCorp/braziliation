using NUnit.Framework;

namespace Braziliation.Game.Tests;

internal static class RepoRootFinder
{
    /// <summary>
    /// Sobe a partir do diretório de saída dos testes até achar a pasta que contém
    /// <c>ProjectSettings/ProjectVersion.txt</c> (raiz do projeto Unity).
    /// </summary>
    internal static string FindRepositoryRoot()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null)
        {
            var marker = Path.Combine(dir.FullName, "ProjectSettings", "ProjectVersion.txt");
            if (File.Exists(marker))
                return dir.FullName;
            dir = dir.Parent;
        }

        Assert.Fail(
            "Não foi possível localizar a raiz do repositório (ProjectSettings/ProjectVersion.txt).");
        throw new InvalidOperationException("Unreachable");
    }
}
