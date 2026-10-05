using UnityEngine;
using UnityEngine.Rendering.Universal;

[RequireComponent(typeof(PixelPerfectCamera))]
public class CameraScaler : MonoBehaviour
{
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    private PixelPerfectCamera cam;

    void Start()
    {
        cam = GetComponent<PixelPerfectCamera>();
        // ADR-011: 960x540 / 48 PPU. 1 tile de 48px = 1 unidade.
        // O mundo visível segue 20 x 11,25 unidades, igual ao ADR-004 — só a
        // densidade dentro do enquadramento mudou. 960x540 escala x2 para 1080p.
        cam.assetsPPU = 48;
        cam.refResolutionX = 960;
        cam.refResolutionY = 540;
    }

    // Update is called once per frame
    void Update()
    {

    }
}
