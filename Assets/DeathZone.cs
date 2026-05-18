using UnityEngine;

public class DeathZone : MonoBehaviour
{
    void Start()
    {
        Collider col = GetComponent<Collider>();
        if (col != null) col.isTrigger = true;
    }

    void OnTriggerEnter(Collider other)
    {
        if (!other.CompareTag("Player")) return;
        other.GetComponent<MarioAnimationController>()?.TakeDamage();
    }
}
