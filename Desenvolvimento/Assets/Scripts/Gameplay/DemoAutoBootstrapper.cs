using UnityEngine;
using UnityEngine.SceneManagement;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Garante que a cena tenha um bootstrap de demo para rodar sem setup manual.
    /// Não cria bootstrap em cenas de menu.
    /// </summary>
    public static class DemoAutoBootstrapper
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void EnsureBootstrapExists()
        {
            var sceneName = SceneManager.GetActiveScene().name;
            if (sceneName.ToLowerInvariant().Contains("menu"))
                return;

            if (sceneName == "DemoGameplay")
                return;

            // Quando a cena fixa de demo estiver presente no projeto, ela deve prevalecer
            // sobre o bootstrap automático.
            if (GameObject.Find("DemoFixedSceneRoot") != null)
                return;

            if (Object.FindAnyObjectByType<DemoSceneBootstrap>() != null)
                return;

            var bootstrapObj = new GameObject("DemoSceneBootstrap_Auto");
            bootstrapObj.AddComponent<DemoSceneBootstrap>();
        }
    }
}
