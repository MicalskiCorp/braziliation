using UnityEngine;
using Braziliation.Build;
using Braziliation.Core;

namespace Braziliation.Build
{
    /// <summary>
    /// Ponto central de inicialização da camada de Build.
    /// Cria e registra o BuildState no GameServiceLocator e fornece referência ao PlayerBuildController.
    ///
    /// Deve existir na mesma cena (ou hierarquia) que o GameServiceLocator.
    /// </summary>
    public sealed class BuildServiceBinder : MonoBehaviour
    {
        [Header("Referências")]
        [Tooltip("PlayerBuildController da cena — receberá o BuildState criado aqui.")]
        [SerializeField] private PlayerBuildController _buildController;

        public void SetBuildController(PlayerBuildController buildController)
        {
            _buildController = buildController;
        }

        private void Awake()
        {
            var locator = GameServiceLocator.Instance;
            if (locator == null)
            {
                Debug.LogError("[BuildServiceBinder] GameServiceLocator não encontrado. " +
                               "Adicione-o à cena antes do BuildServiceBinder.");
                return;
            }

            // Cria o estado inicial da build e registra no ServiceLocator
            var buildState = new BuildState();
            locator.Register(buildState);

            // Injeta o BuildState no PlayerBuildController se a referência estiver vinculada
            if (_buildController != null)
                _buildController.SetBuildState(buildState);
            else
                Debug.LogWarning("[BuildServiceBinder] PlayerBuildController não vinculado no Inspector.");
        }
    }
}
