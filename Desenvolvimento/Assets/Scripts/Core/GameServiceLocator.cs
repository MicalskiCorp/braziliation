using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using Braziliation.Crafting;
using Braziliation.SaveSystem;
using Braziliation.Settings;
using Braziliation.Storage;

namespace Braziliation.Core
{
    /// <summary>
    /// Raiz de composição de todos os serviços do jogo.
    /// Cria <see cref="SaveGameService"/> e <see cref="SettingsService"/> com <see cref="FileStorageProvider"/>
    /// apontando para <see cref="Application.persistentDataPath"/>.
    ///
    /// Pré-requisitos:
    ///   - Adicionar este componente a um GameObject na primeira cena (ex: Bootstrap ou MainMenu).
    ///   - A DLL <see cref="Braziliation.Game.Core"/> deve estar em Assets/Plugins/Braziliation/.
    ///   - Todos os demais MonoBehaviours obtêm serviços via <see cref="Instance"/> no Awake().
    ///
    /// Demais serviços registrados conforme cada sistema é integrado
    /// </summary>
    [DefaultExecutionOrder(-100)]   // must run before any script that calls Instance in Awake()
    public sealed class GameServiceLocator : MonoBehaviour
    {
        public static GameServiceLocator Instance { get; private set; }

        [Header("Serviços")]
        [Tooltip("Se verdadeiro, instancia e registra o CraftingService no Awake.")]
        [SerializeField] private bool initializeCraftingService = true;

        // Propriedades tipadas para serviços sempre presentes
        public SaveGameService SaveGameService { get; private set; }
        public SettingsService SettingsService { get; private set; }

        // Registro genérico para demais serviços
        private readonly Dictionary<Type, object> _services = new Dictionary<Type, object>();

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

            if (initializeCraftingService)
                Register(new CraftingService());
        }

        /// <summary>
        /// Registra um serviço pelo seu tipo. Substitui o serviço anterior se já existir.
        /// </summary>
        public void Register<T>(T service) where T : class
        {
            _services[typeof(T)] = service;
        }

        /// <summary>
        /// Resolve um serviço registrado pelo seu tipo.
        /// Retorna null e loga aviso se o serviço não estiver registrado.
        /// </summary>
        public T Resolve<T>() where T : class
        {
            if (_services.TryGetValue(typeof(T), out var service))
                return service as T;

            Debug.LogWarning($"[GameServiceLocator] Serviço '{typeof(T).Name}' não registrado.");
            return null;
        }
    }
}
