using Braziliation.Core;
using UnityEngine;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Fonte única da aparência e da geometria dos objetos da cena de demo.
    /// Usada pelo <see cref="DemoSceneBootstrap"/> (runtime) e pelo
    /// DemoSceneBuilderEditor (cena fixa) para que os dois nunca divirjam,
    /// e espelhada em Assets/Scenes/DemoGameplay.unity.
    ///
    /// Os sprites são placeholders CC0 (Gothicvania, de ansimuz) em
    /// Assets/Art/ThirdParty/Gothicvania/ — ver SOURCES.txt daquela pasta e
    /// Desenvolvimento/CREDITS.md. Se algum asset não for encontrado, cada
    /// método cai no quadrado branco colorido usado antes: a demo continua
    /// jogável mesmo sem a arte de terceiros no disco.
    ///
    /// Convenção de pivot: personagens e inimigos têm pivot no centro-inferior,
    /// então transform.position é o pé do personagem e o collider é deslocado
    /// para cima via offset. Por isso os spawns ficam exatamente em
    /// <see cref="GroundSurfaceY"/> — nascer acima disso faz o personagem
    /// aparecer flutuando e cair no primeiro frame.
    /// </summary>
    public static class DemoSceneVisuals
    {
        // Sprites estáticos (caminhos relativos à pasta Resources do pacote de terceiros)
        public const string PlayerSpritePath = "Demo/chr_placeholder_heroi_idle";
        public const string EnemySpritePath = "Demo/enm_placeholder_cao_idle";
        public const string GroundSpritePath = "Demo/env_placeholder_chao_tile";
        public const string BackgroundSpritePath = "Demo/env_placeholder_fundo_castelo";

        // Spritesheets de animação (fatiados pelo SheetAutoSlicer na importação)
        public const string PlayerIdleSheetPath = "Demo/Sheets/chr_placeholder_heroi_idle_sheet";
        public const string PlayerRunSheetPath = "Demo/Sheets/chr_placeholder_heroi_run_sheet";
        public const string EnemyIdleSheetPath = "Demo/Sheets/enm_placeholder_cao_idle_sheet";
        public const string EnemyWalkSheetPath = "Demo/Sheets/enm_placeholder_cao_walk_sheet";

        // Cores usadas quando o sprite não é encontrado (aparência anterior à arte)
        public static readonly Color PlayerFallbackColor = new Color(0.15f, 0.75f, 0.95f, 1f);
        public static readonly Color EnemyFallbackColor = new Color(0.95f, 0.3f, 0.25f, 1f);
        public static readonly Color GroundFallbackColor = new Color(0.18f, 0.22f, 0.28f, 1f);

        // Geometria de colisão. Pé do personagem em y=0 local; o collider sobe pelo offset.
        public static readonly Vector2 PlayerColliderSize = new Vector2(0.9f, 2.4f);
        public static readonly Vector2 PlayerColliderOffset = new Vector2(0f, 1.2f);
        public static readonly Vector2 EnemyColliderSize = new Vector2(2.5f, 1.4f);
        public static readonly Vector2 EnemyColliderOffset = new Vector2(0f, 0.7f);

        /// <summary>Y da superfície de caminhada. O collider desce a partir daí.</summary>
        public const float GroundSurfaceY = -1f;
        public static readonly Vector2 GroundColliderSize = new Vector2(24f, 1f);
        public static readonly Vector2 GroundColliderOffset = new Vector2(0f, -0.5f);

        /// <summary>Área desenhada do chão (drawMode Tiled, pivot no topo do tile).</summary>
        public static readonly Vector2 GroundVisualSize = new Vector2(24f, 2f);

        /// <summary>Metade da largura do chão: as paredes ficam nessas pontas.</summary>
        public const float GroundHalfWidth = 12f;

        public static readonly Vector2 WallSize = new Vector2(1f, 8f);

        /// <summary>Abaixo disso, o <see cref="FallRespawn"/> devolve o objeto ao spawn.</summary>
        public const float KillY = -12f;

        // Spawns no nível do chão — sem isso os personagens nascem no ar.
        public static readonly Vector2 PlayerSpawn = new Vector2(-3f, GroundSurfaceY);
        public static readonly Vector2 EnemySpawn = new Vector2(3f, GroundSurfaceY);

        public const int BackgroundSortingOrder = -100;
        public const int GroundSortingOrder = -10;
        public const int CharacterSortingOrder = 0;

        /// <summary>A arte do cão do pacote Gothicvania é desenhada olhando para a esquerda.</summary>
        public const bool EnemySpriteFacesRight = false;

        public static bool TryLoadSprite(string resourcePath, out Sprite sprite)
        {
            sprite = Resources.Load<Sprite>(resourcePath);
            return sprite != null;
        }

        /// <summary>Quadrado branco 1x1 do Unity, usado como fallback sem arte.</summary>
        public static Sprite CreateSquareSprite()
        {
            var texture = Texture2D.whiteTexture;
            return Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f), 100f);
        }

        public static SpriteRenderer ApplyCharacterSprite(GameObject target, string resourcePath, Color fallbackColor)
        {
            var renderer = target.GetComponent<SpriteRenderer>();
            if (renderer == null)
                renderer = target.AddComponent<SpriteRenderer>();

            renderer.sortingOrder = CharacterSortingOrder;

            if (TryLoadSprite(resourcePath, out var sprite))
            {
                renderer.sprite = sprite;
                renderer.color = Color.white;
            }
            else
            {
                renderer.sprite = CreateSquareSprite();
                renderer.color = fallbackColor;
            }

            return renderer;
        }

        /// <summary>
        /// Registra os clipes de animação do jogador. O <see cref="SpriteSheetAnimator"/>
        /// carrega os quadros do spritesheet fatiado; sem os sheets no disco ele
        /// simplesmente não troca de quadro.
        /// </summary>
        public static void ConfigurePlayerAnimation(GameObject player)
        {
            var animator = player.GetComponent<SpriteSheetAnimator>();
            if (animator == null)
                animator = player.AddComponent<SpriteSheetAnimator>();

            animator.AddClip("idle", PlayerIdleSheetPath, 6f);
            animator.AddClip("run", PlayerRunSheetPath, 12f);

            if (player.GetComponent<PlayerSpriteAnimation>() == null)
                player.AddComponent<PlayerSpriteAnimation>();
        }

        public static void ConfigureEnemyAnimation(GameObject enemy)
        {
            var animator = enemy.GetComponent<SpriteSheetAnimator>();
            if (animator == null)
                animator = enemy.AddComponent<SpriteSheetAnimator>();

            animator.AddClip("idle", EnemyIdleSheetPath, 6f);
            animator.AddClip("walk", EnemyWalkSheetPath, 10f);

            if (enemy.GetComponent<EnemySpriteAnimation>() == null)
                enemy.AddComponent<EnemySpriteAnimation>();
        }

        /// <summary>
        /// Posiciona o chão, dimensiona o collider e desenha o tile repetido.
        /// A superfície fica em <see cref="GroundSurfaceY"/> com ou sem sprite,
        /// então o comportamento físico independe da arte estar presente.
        /// </summary>
        public static void ConfigureGround(GameObject ground)
        {
            ground.transform.position = new Vector3(0f, GroundSurfaceY, 0f);
            ground.transform.localScale = Vector3.one;
            GameLayers.Apply(ground, GameLayers.GroundName);

            var collider = ground.GetComponent<BoxCollider2D>();
            if (collider == null)
                collider = ground.AddComponent<BoxCollider2D>();
            collider.size = GroundColliderSize;
            collider.offset = GroundColliderOffset;

            var renderer = ground.GetComponent<SpriteRenderer>();
            if (renderer == null)
                renderer = ground.AddComponent<SpriteRenderer>();
            renderer.sortingOrder = GroundSortingOrder;

            if (TryLoadSprite(GroundSpritePath, out var sprite))
            {
                renderer.sprite = sprite;
                renderer.color = Color.white;
                // O tile tem pivot no topo, então o desenho cresce para baixo a
                // partir da superfície e acompanha qualquer largura de collider.
                renderer.drawMode = SpriteDrawMode.Tiled;
                renderer.size = GroundVisualSize;
            }
            else
            {
                renderer.sprite = CreateSquareSprite();
                renderer.color = GroundFallbackColor;
            }
        }

        /// <summary>
        /// Paredes invisíveis nas pontas do chão. Sem elas dá para andar para fora do
        /// mapa e cair no vazio. Ficam na camada Ground para que o sensor de parede
        /// dos inimigos também as enxergue e faça o inimigo virar.
        /// </summary>
        public static GameObject[] CreateBounds(Transform parent)
        {
            var walls = new GameObject[2];
            var index = 0;

            foreach (var side in new[] { -1f, 1f })
            {
                var wall = new GameObject(side < 0f ? "Bound_Left" : "Bound_Right");
                if (parent != null)
                    wall.transform.SetParent(parent);

                wall.transform.position = new Vector3(
                    side * (GroundHalfWidth + WallSize.x * 0.5f),
                    GroundSurfaceY + WallSize.y * 0.5f,
                    0f);

                GameLayers.Apply(wall, GameLayers.GroundName);

                var collider = wall.AddComponent<BoxCollider2D>();
                collider.size = WallSize;

                walls[index++] = wall;
            }

            return walls;
        }

        /// <summary>Cria o fundo estático da demo. Devolve null se não houver sprite.</summary>
        public static GameObject CreateBackground(Transform parent, Vector3 position)
        {
            if (!TryLoadSprite(BackgroundSpritePath, out var sprite))
                return null;

            var background = new GameObject("Background_Demo");
            if (parent != null)
                background.transform.SetParent(parent);
            background.transform.position = position;

            var renderer = background.AddComponent<SpriteRenderer>();
            renderer.sprite = sprite;
            renderer.sortingOrder = BackgroundSortingOrder;

            return background;
        }
    }
}
