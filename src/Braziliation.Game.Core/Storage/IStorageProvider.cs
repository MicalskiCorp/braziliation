namespace Braziliation.Storage;

/// <summary>
/// Key/value string persistence abstraction for the save and settings systems.
/// Data is a JSON string, making it portable across local disk and future Steam Cloud.
/// Keys must be valid file-name tokens (no path separators or special characters).
/// Swap the implementation to change the backend without touching any service code.
/// </summary>
public interface IStorageProvider
{
    /// <summary>
    /// Persists <paramref name="data"/> under <paramref name="key"/>, overwriting any existing entry.
    /// </summary>
    void Save(string key, string data);

    /// <summary>
    /// Returns the string stored under <paramref name="key"/>,
    /// or <see langword="null"/> when the entry is absent or unreadable.
    /// </summary>
    string? Load(string key);

    /// <summary>Returns <see langword="true"/> when an entry for <paramref name="key"/> exists.</summary>
    bool Exists(string key);

    /// <summary>Removes the entry for <paramref name="key"/>. No-op if the entry does not exist.</summary>
    void Delete(string key);
}
