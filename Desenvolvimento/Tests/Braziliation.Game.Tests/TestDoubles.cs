using Braziliation.SaveSystem;
using Braziliation.Settings;

namespace Braziliation.Game.Tests;

/// <summary>
/// In-memory implementation of <see cref="ISaveStorage"/> for use in unit tests.
/// Each instance is isolated; create a new one per test.
/// </summary>
internal sealed class InMemorySaveStorage : ISaveStorage
{
    private readonly Dictionary<int, byte[]> _slots = new();

    public void Write(int slotIndex, byte[] data) => _slots[slotIndex] = data;
    public byte[]? Read(int slotIndex) => _slots.TryGetValue(slotIndex, out var data) ? data : null;
    public bool Exists(int slotIndex) => _slots.ContainsKey(slotIndex);
    public void Delete(int slotIndex) => _slots.Remove(slotIndex);
}

/// <summary>
/// In-memory implementation of <see cref="ISettingsStorage"/> for use in unit tests.
/// </summary>
internal sealed class InMemorySettingsStorage : ISettingsStorage
{
    private byte[]? _data;

    public void Write(byte[] data) => _data = data;
    public byte[]? Read() => _data;
}
