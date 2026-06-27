namespace Braziliation.SaveSystem;

/// <summary>Abstração da camada de persistência por slot para dados de save.</summary>
public interface ISaveStorage
{
    void Write(int slotIndex, byte[] data);
    byte[]? Read(int slotIndex);
    bool Exists(int slotIndex);
    void Delete(int slotIndex);
}
