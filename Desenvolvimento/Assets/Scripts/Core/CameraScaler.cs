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
        // ADR-004: 640x360 / 32 PPU (Blasphemous-like). 1 tile 32px = 1 unidade.
        cam.assetsPPU = 32;
        cam.refResolutionX = 640;
        cam.refResolutionY = 360;
    }

    // Update is called once per frame
    void Update()
    {

    }
}
