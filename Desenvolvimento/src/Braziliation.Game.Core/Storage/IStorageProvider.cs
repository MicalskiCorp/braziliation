namespace Braziliation.Storage;

/// <summary>
/// Abstração de persistência chave/valor em string para os sistemas de save e settings.
/// Os dados são strings JSON, mantendo portabilidade entre disco local e futuro Steam Cloud.
/// As chaves devem ser tokens válidos para nome de arquivo (sem separadores de caminho ou caracteres especiais).
/// Trocar a implementação muda o backend sem alterar o código dos serviços.
/// </summary>
public interface IStorageProvider
{
    /// <summary>
    /// Persiste <paramref name="data"/> em <paramref name="key"/>, sobrescrevendo qualquer entrada existente.
    /// </summary>
    void Save(string key, string data);

    /// <summary>
    /// Retorna a string armazenada em <paramref name="key"/>,
    /// ou <see langword="null"/> quando a entrada estiver ausente ou ilegível.
    /// </summary>
    string? Load(string key);

    /// <summary>Retorna <see langword="true"/> quando existe uma entrada para <paramref name="key"/>.</summary>
    bool Exists(string key);

    /// <summary>Remove a entrada de <paramref name="key"/>. Não faz nada se a entrada não existir.</summary>
    void Delete(string key);
}
