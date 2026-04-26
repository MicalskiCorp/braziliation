namespace Braziliation.Storage;

/// <summary>
/// File-system implementation of <see cref="IStorageProvider"/>.
/// Each key maps to a UTF-8 <c>.json</c> file inside the injected base directory.
/// The directory is created lazily on the first write — no hardcoded paths are used.
/// Missing and unreadable files are handled safely by returning <see langword="null"/>.
/// </summary>
/// <remarks>
/// To target Steam Cloud in the future, implement <see cref="IStorageProvider"/>
/// with the Steam Remote Storage API and inject it in place of this class.
/// </remarks>
public sealed class FileStorageProvider : IStorageProvider
{
    private readonly string _basePath;

    /// <param name="basePath">
    /// Directory that will hold all managed <c>.json</c> files.
    /// Injected at construction time — never hardcoded.
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
    /// The file contents as a UTF-8 string, or <see langword="null"/> when the file
    /// does not exist or cannot be read (e.g. locked, corrupted).
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

    // ── Helpers ───────────────────────────────────────────────────────────────

    private string FilePath(string key) => Path.Combine(_basePath, key + ".json");

    private static void ValidateKey(string key)
    {
        if (string.IsNullOrWhiteSpace(key)) throw new ArgumentException("Value cannot be null or whitespace.", nameof(key));
        if (key.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0)
            throw new ArgumentException($"Key '{key}' contains invalid file-name characters.", nameof(key));
    }
}
