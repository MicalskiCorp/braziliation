using System.Collections.Generic;
using UnityEngine;
using Braziliation.Crafting;

namespace Braziliation.Core
{
    /// <summary>
    /// Inventário do jogador — armazena componentes e itens coletados no mundo.
    /// TODO: implementar lógica completa de inventário (limites de capacidade, categorias, UI).
    /// </summary>
    public sealed class PlayerInventory : MonoBehaviour
    {
        private readonly List<ItemComponent> _itens = new List<ItemComponent>();

        /// <summary>
        /// Adiciona um item ao inventário.
        /// </summary>
        public void AddItem(ItemComponent item)
        {
            if (item == null) return;
            _itens.Add(item);
        }

        /// <summary>
        /// Verifica se o inventário contém um item com o ID informado.
        /// </summary>
        public bool HasItem(string itemId)
        {
            return _itens.Exists(i => i.Id == itemId);
        }

        /// <summary>
        /// Remove um item do inventário pelo ID. Retorna verdadeiro se removido com sucesso.
        /// </summary>
        public bool RemoveItem(string itemId)
        {
            var item = _itens.Find(i => i.Id == itemId);
            if (item == null) return false;
            _itens.Remove(item);
            return true;
        }

        /// <summary>
        /// Retorna o primeiro item com o ID informado, ou null se não encontrado.
        /// </summary>
        public ItemComponent GetItem(string itemId)
        {
            return _itens.Find(i => i.Id == itemId);
        }

        /// <summary>
        /// Retorna todos os itens do inventário como lista somente-leitura.
        /// </summary>
        public IReadOnlyList<ItemComponent> GetAll() => _itens.AsReadOnly();
    }
}
