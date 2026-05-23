using System.Collections.Generic;

namespace Braziliation.Core
{
    /// <summary>
    /// Interface para componentes que recebem e aplicam stats derivados da build do personagem.
    /// Implementada pelo PlayerController (ou similar) para aceitar os stats calculados pelo PlayerBuildController.
    /// </summary>
    public interface IStatReceiver
    {
        /// <summary>
        /// Recebe um dicionário de stats agregados e os aplica ao componente.
        /// Chave: nome do stat (ex: "attack", "defense", "speed"). Valor: magnitude total.
        /// </summary>
        void ApplyStats(Dictionary<string, float> stats);
    }
}
