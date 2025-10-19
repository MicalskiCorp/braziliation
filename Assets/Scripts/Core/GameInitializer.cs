using UnityEngine;

namespace Braziliation.Core
{
    public class GameInitializer : MonoBehaviour
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        static void Initialize()
        {
            Debug.Log("Braziliation Engine – Inicialização iniciada...");
            Application.targetFrameRate = 60;
            QualitySettings.vSyncCount = 0;
        }
    }
}