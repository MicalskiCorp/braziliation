namespace Braziliation.SaveSystem;

/// <summary>Abstraction over the per-slot persistence layer for save data.</summary>
public interface ISaveStorage
{
    void Write(int slotIndex, byte[] data);
    byte[]? Read(int slotIndex);
    bool Exists(int slotIndex);
    void Delete(int slotIndex);
}
