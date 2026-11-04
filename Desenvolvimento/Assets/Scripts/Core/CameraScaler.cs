using UnityEngine;
using UnityEngine.Rendering.Universal;

namespace Braziliation.Core
{
    [RequireComponent(typeof(PixelPerfectCamera))]
    public class CameraScaler : MonoBehaviour
    {
        private PixelPerfectCamera _cam;

        private void Awake()
        {
            _cam = GetComponent<PixelPerfectCamera>();
            // ADR-011: 960x540 / 48 PPU. 1 tile de 48px = 1 unidade.
            // O mundo visível segue 20 x 11,25 unidades, igual ao ADR-004 — só a
            // densidade dentro do enquadramento mudou. 960x540 escala x2 para 1080p.
            _cam.assetsPPU = 48;
            _cam.refResolutionX = 960;
            _cam.refResolutionY = 540;
        }
    }
}
