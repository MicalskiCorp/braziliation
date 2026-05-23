namespace Braziliation.Core
{
    /// <summary>
    /// Interface para objetos interagíveis no mundo do jogo.
    /// Implementada por interagíveis como totens, NPCs, portas e ativadores.
    /// </summary>
    public interface IInteractable
    {
        /// <summary>
        /// Executado quando o jogador interage com este objeto.
        /// </summary>
        void Interact();
    }
}
