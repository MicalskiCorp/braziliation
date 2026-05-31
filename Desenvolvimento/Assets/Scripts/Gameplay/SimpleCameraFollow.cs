using UnityEngine;

namespace Braziliation.Gameplay
{
    /// <summary>
    /// Follow simples para câmera ortográfica 2D da demo.
    /// </summary>
    public sealed class SimpleCameraFollow : MonoBehaviour
    {
        [SerializeField] private Transform _target;
        [SerializeField] private Vector3 _offset = new Vector3(0f, 1f, -10f);
        [SerializeField] private float _smooth = 8f;

        public void SetTarget(Transform target)
        {
            _target = target;
        }

        private void LateUpdate()
        {
            if (_target == null)
                return;

            var desired = _target.position + _offset;
            transform.position = Vector3.Lerp(transform.position, desired, Time.deltaTime * _smooth);
        }
    }
}
