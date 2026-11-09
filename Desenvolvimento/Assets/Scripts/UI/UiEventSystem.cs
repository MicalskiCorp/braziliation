using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;

namespace Braziliation.UI
{
    /// <summary>
    /// Garante um <see cref="EventSystem"/> com <see cref="InputSystemUIInputModule"/> na cena, o mesmo par
    /// da <c>MainMenu.unity</c>. Sem ele, <c>EventSystem.current</c> é null e todo painel que foca um
    /// elemento ao abrir (<c>SetSelectedGameObject</c>, navegação por controle e Steam Input) lança
    /// <c>NullReferenceException</c>.
    /// </summary>
    public static class UiEventSystem
    {
        public const string ObjectName = "EventSystem";

        /// <summary>
        /// Cria o par se a cena ainda não tiver um <see cref="EventSystem"/>. Devolve o objeto criado, ou
        /// null quando já existia, para quem chama no Editor registrar o Undo.
        /// </summary>
        public static GameObject Ensure()
        {
            if (Object.FindAnyObjectByType<EventSystem>() != null)
                return null;

            var go = new GameObject(ObjectName);
            go.AddComponent<EventSystem>();
            go.AddComponent<InputSystemUIInputModule>();
            return go;
        }
    }
}
