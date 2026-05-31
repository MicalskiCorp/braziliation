namespace Braziliation.Core
{
    /// <summary>
    /// Contrato para componentes que podem receber dano.
    /// </summary>
    public interface IDamageable
    {
        /// <summary>
        /// Aplica dano bruto ao alvo.
        /// </summary>
        /// <param name="amount">Quantidade de dano.</param>
        void TakeDamage(float amount);
    }
}
