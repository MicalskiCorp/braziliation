namespace Braziliation.Storage;

/// <summary>
/// Implementação em sistema de arquivos de <see cref="IStorageProvider"/>.
/// Cada chave mapeia para um arquivo <c>.json</c> UTF-8 dentro do diretório base injetado.
/// O diretório é criado sob demanda na primeira gravação — sem uso de caminhos fixos no código.
/// Arquivos ausentes ou ilegíveis são tratados com segurança retornando <see langword="null"/>.
/// </summary>
/// <remarks>
/// Para suportar Steam Cloud no futuro, implemente <see cref="IStorageProvider"/>
/// com a API de Steam Remote Storage e injete essa implementação no lugar desta classe.
/// </remarks>
public sealed class FileStorageProvider : IStorageProvider
{
    private readonly string _basePath;

    /// <param name="basePath">
    /// Diretório que armazenará todos os arquivos <c>.json</c> gerenciados.
    /// Injetado no momento da construção — nunca fixo em código.
    /// </param>
    public FileStorageProvider(string basePath)
    {
        if (string.IsNullOrWhiteSpace(basePath)) throw new ArgumentException("Value cannot be null or whitespace.", nameof(basePath));
        _basePath = basePath;
    }

    /// <inheritdoc/>
    public void Save(string key, string data)
    {
        ValidateKey(key);
        if (data is null) throw new ArgumentNullException(nameof(data));
        Directory.CreateDirectory(_basePath);
        File.WriteAllText(FilePath(key), data, System.Text.Encoding.UTF8);
    }

    /// <inheritdoc/>
    /// <returns>
    /// Conteúdo do arquivo como string UTF-8, ou <see langword="null"/> quando o arquivo
    /// não existir ou não puder ser lido (ex.: bloqueado, corrompido).
    /// </returns>
    public string? Load(string key)
    {
        ValidateKey(key);
        var path = FilePath(key);
        if (!File.Exists(path))
            return null;

        try
        {
            return File.ReadAllText(path, System.Text.Encoding.UTF8);
        }
        catch (IOException)
        {
            return null;
        }
    }

    /// <inheritdoc/>
    public bool Exists(string key)
    {
        ValidateKey(key);
        return File.Exists(FilePath(key));
    }

    /// <inheritdoc/>
    public void Delete(string key)
    {
        ValidateKey(key);
        var path = FilePath(key);
        if (File.Exists(path))
            File.Delete(path);
    }

    // ── Auxiliares ────────────────────────────────────────────────────────────

    private string FilePath(string key) => Path.Combine(_basePath, key + ".json");

    private static void ValidateKey(string key)
    {
        if (string.IsNullOrWhiteSpace(key)) throw new ArgumentException("Value cannot be null or whitespace.", nameof(key));
        if (key.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0)
            throw new ArgumentException($"Key '{key}' contains invalid file-name characters.", nameof(key));
    }
}
