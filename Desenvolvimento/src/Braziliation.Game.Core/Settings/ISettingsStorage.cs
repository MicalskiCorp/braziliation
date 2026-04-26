namespace Braziliation.Settings;

/// <summary>Abstraction over the persistence layer for game settings.</summary>
public interface ISettingsStorage
{
    void Write(byte[] data);
    byte[]? Read();
}
