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

        throw new InvalidOperationException(
            "Não foi possível localizar a raiz do repositório (ProjectSettings/ProjectVersion.txt).");
    }

    /// <summary>
    /// Raiz do repositório git — um nível acima da raiz do projeto Unity
    /// (<c>Desenvolvimento/</c>). É onde vivem .github/, .claude/ e Design/.
    /// </summary>
    internal static string FindGitRoot()
    {
        var unityRoot = new DirectoryInfo(FindRepositoryRoot());
        var parent = unityRoot.Parent
            ?? throw new InvalidOperationException(
                $"Raiz do projeto Unity '{unityRoot.FullName}' não tem diretório pai.");
        return parent.FullName;
    }
}
