using System.IO;
using UnityEngine;
using Braziliation.SaveSystem;
using Braziliation.Settings;
using Braziliation.Storage;

namespace Braziliation.Core
{
    /// <summary>
    /// Composition root for all game services.
    /// Creates <see cref="SaveGameService"/> and <see cref="SettingsService"/> backed by
    /// <see cref="FileStorageProvider"/> pointing at <see cref="Application.persistentDataPath"/>.
    ///
    /// Requirements:
    ///   - Place this component on a GameObject in the first scene (e.g. Bootstrap or MainMenu).
    ///   - <see cref="Braziliation.Game.Core"/> DLL must be present in Assets/Plugins/Braziliation/.
    ///   - All other MonoBehaviours obtain services via <see cref="Instance"/> in Awake().
    /// </summary>
    public sealed class GameServiceLocator : MonoBehaviour
    {
        public static GameServiceLocator Instance { get; private set; }

        public SaveGameService SaveGameService { get; private set; }
        public SettingsService SettingsService { get; private set; }

        private void Awake()
        {
            if (Instance != null)
            {
                Destroy(gameObject);
                return;
            }

            Instance = this;
            DontDestroyOnLoad(gameObject);
            BuildServices();
        }

        private void BuildServices()
        {
            var saveProvider   = new FileStorageProvider(Path.Combine(Application.persistentDataPath, "saves"));
            var configProvider = new FileStorageProvider(Path.Combine(Application.persistentDataPath, "config"));

            SaveGameService = new SaveGameService(new StorageProviderSaveAdapter(saveProvider));
            SettingsService = new SettingsService(new StorageProviderSettingsAdapter(configProvider));
        }
    }
}
