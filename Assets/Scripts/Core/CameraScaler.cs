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
        cam.assetsPPU = 16;
        cam.refResolutionX = 320;
        cam.refResolutionY = 180;
    }

    // Update is called once per frame
    void Update()
    {

    }
}
