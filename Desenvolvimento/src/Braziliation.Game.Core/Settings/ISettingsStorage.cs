namespace Braziliation.Settings;

/// <summary>Abstração da camada de persistência para configurações do jogo.</summary>
public interface ISettingsStorage
{
    void Write(byte[] data);
    byte[]? Read();
}
