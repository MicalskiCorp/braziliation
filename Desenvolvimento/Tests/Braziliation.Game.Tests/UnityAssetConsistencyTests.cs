using System.Text.Json;
using System.Text.RegularExpressions;
using Xunit;

namespace Braziliation.Game.Tests;

/// <summary>
/// Scripts Unity referenciam assets por nome (layers, ações de input, caminhos de
/// Resources, cenas). Um nome errado compila e só falha em runtime — e o CI não abre o
/// Unity. Estes testes leem os scripts e os assets como texto e travam que batem.
/// Complementam os testes EditMode (Assets/Tests/EditMode/), que verificam o mesmo de
/// dentro do Unity via skill unity-validar.
/// </summary>
public sealed class UnityAssetConsistencyTests
{
    private static string UnityRoot => RepoRootFinder.FindRepositoryRoot();

    private static string ReadUnity(string relativePath)
        => File.ReadAllText(Path.Combine(UnityRoot, relativePath));

    [Fact]
    public void Every_GameLayers_Name_Exists_In_TagManager()
    {
        var names = Regex.Matches(
                ReadUnity("Assets/Scripts/Core/GameLayers.cs"),
                @"const\s+string\s+\w+Name\s*=\s*""([^""]+)""")
            .Select(m => m.Groups[1].Value)
            .ToList();
        Assert.NotEmpty(names);

        var tagManager = ReadUnity("ProjectSettings/TagManager.asset");
        var start = tagManager.IndexOf("layers:", StringComparison.Ordinal);
        var end = tagManager.IndexOf("m_SortingLayers", start, StringComparison.Ordinal);
        Assert.True(start >= 0 && end > start, "Bloco 'layers:' não encontrado no TagManager.asset.");

        var layers = Regex.Matches(tagManager[start..end], @"^\s*-\s*(.*)$", RegexOptions.Multiline)
            .Select(m => m.Groups[1].Value.Trim())
            .ToHashSet();

        foreach (var name in names)
            Assert.True(layers.Contains(name), $"GameLayers usa a layer '{name}', ausente em ProjectSettings/TagManager.asset.");
    }

    [Fact]
    public void Every_GameInput_Action_Exists_In_Project_Wide_Asset()
    {
        var gameInput = ReadUnity("Assets/Scripts/Core/GameInput.cs");
        var map = Regex.Match(gameInput, @"const\s+string\s+Map\s*=\s*""(\w+)""").Groups[1].Value;
        var actions = Regex.Matches(gameInput, @"Resolve\(ref\s+\w+,\s*""(\w+)""\)")
            .Select(m => m.Groups[1].Value)
            .ToList();
        Assert.False(string.IsNullOrEmpty(map), "Constante Map não encontrada em GameInput.cs.");
        Assert.NotEmpty(actions);

        using var asset = JsonDocument.Parse(ReadUnity("Assets/InputSystem_Actions.inputactions"));
        var mapElement = asset.RootElement.GetProperty("maps").EnumerateArray()
            .FirstOrDefault(m => m.GetProperty("name").GetString() == map);
        Assert.True(mapElement.ValueKind == JsonValueKind.Object, $"Action map '{map}' ausente em InputSystem_Actions.inputactions.");

        var declared = mapElement.GetProperty("actions").EnumerateArray()
            .Select(a => a.GetProperty("name").GetString())
            .ToHashSet();

        foreach (var action in actions)
            Assert.True(declared.Contains(action), $"GameInput lê '{map}/{action}', que não existe no action asset.");
    }

    [Fact]
    public void Every_DemoSceneVisuals_Resource_Path_Exists()
    {
        var paths = Regex.Matches(
                ReadUnity("Assets/Scripts/Gameplay/DemoSceneVisuals.cs"),
                @"const\s+string\s+\w+Path\s*=\s*""([^""]+)""")
            .Select(m => m.Groups[1].Value)
            .ToList();
        Assert.NotEmpty(paths);

        var resourceRoots = Directory.EnumerateDirectories(Path.Combine(UnityRoot, "Assets"), "Resources", SearchOption.AllDirectories)
            .ToList();

        foreach (var path in paths)
        {
            var found = resourceRoots.Any(root => File.Exists(Path.Combine(root, path + ".png")));
            Assert.True(found, $"DemoSceneVisuals carrega Resources '{path}', mas não há '{path}.png' em nenhuma pasta Resources/.");
        }
    }

    [Fact]
    public void Every_Scene_In_Build_Settings_Exists()
    {
        var scenes = Regex.Matches(ReadUnity("ProjectSettings/EditorBuildSettings.asset"), @"path:\s*(Assets/\S+\.unity)")
            .Select(m => m.Groups[1].Value)
            .ToList();
        Assert.NotEmpty(scenes);

        foreach (var scene in scenes)
            Assert.True(File.Exists(Path.Combine(UnityRoot, scene)), $"Cena na Build Settings não existe: {scene}");
    }
}
