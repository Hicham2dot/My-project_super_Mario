using UnityEngine;
using Unity.Cinemachine;

/// <summary>
/// Attachez ce script à un GameObject vide "CameraRig".
/// Assignez le Transform de Mario dans l'Inspector, puis cliquez
/// sur "Créer Caméra Cinemachine" via le bouton contextuel (ou au démarrage).
/// </summary>
public class MarioCameraSetup : MonoBehaviour
{
    [Header("Cible")]
    [Tooltip("Faites glisser l'objet Mario ici")]
    public Transform marioTransform;

    [Header("Paramètres caméra")]
    [SerializeField] private float followDistance  = 18f;
    [SerializeField] private float followHeight    = 12f;
    [SerializeField] private float followDamping   = 2f;  // lissage du suivi
    [SerializeField] private float verticalOffset  = 1.5f; // regard vers le centre de Mario
    [SerializeField] private float fieldOfView     = 60f;  // angle de vue (plus grand = plus large)

    void Start()
    {
        if (marioTransform == null)
        {
            // Tentative de trouver Mario automatiquement par son tag
            GameObject mario = GameObject.FindWithTag("Player");
            if (mario != null)
                marioTransform = mario.transform;
            else
            {
                Debug.LogWarning("[MarioCameraSetup] Aucune cible trouvée. " +
                                 "Assignez marioTransform dans l'Inspector, " +
                                 "ou ajoutez le tag 'Player' à Mario.");
                return;
            }
        }

        SetupCinemachineCamera();
    }

    private void SetupCinemachineCamera()
    {
        // ── Cherche ou crée la CinemachineCamera ──────────────────
        CinemachineCamera vcam = GetComponentInChildren<CinemachineCamera>();
        if (vcam == null)
        {
            GameObject vcamGO = new GameObject("VirtualCamera_Mario");
            vcamGO.transform.SetParent(transform);
            vcam = vcamGO.AddComponent<CinemachineCamera>();
        }

        // ── Cibles ────────────────────────────────────────────────
        vcam.Follow = marioTransform;
        vcam.LookAt = GetOrCreateLookTarget();

        // ── Composant de suivi (3rd person) ───────────────────────
        CinemachineFollow follow = vcam.gameObject.GetComponent<CinemachineFollow>();
        if (follow == null)
            follow = vcam.gameObject.AddComponent<CinemachineFollow>();

        follow.FollowOffset = new Vector3(0f, followHeight, -followDistance);

        // Angle de vue plus large pour voir plus de niveau
        vcam.Lens.FieldOfView = fieldOfView;

        // Amortissement (damping) pour un mouvement fluide
        var trackerSettings = follow.TrackerSettings;
        trackerSettings.PositionDamping = new Vector3(followDamping, followDamping, followDamping);
        follow.TrackerSettings = trackerSettings;

        // ── Composant de visée ────────────────────────────────────
        CinemachineRotationComposer composer = vcam.gameObject.GetComponent<CinemachineRotationComposer>();
        if (composer == null)
            composer = vcam.gameObject.AddComponent<CinemachineRotationComposer>();

        // Cible légèrement au-dessus des pieds pour un meilleur cadrage
        var composition = composer.Composition;
        composition.ScreenPosition = new Vector2(0f, 0.1f);
        composer.Composition = composition;

        Debug.Log("[MarioCameraSetup] Caméra Cinemachine configurée avec succès !");
    }

    // Crée un point de regard légèrement au-dessus de Mario
    private Transform GetOrCreateLookTarget()
    {
        Transform existing = marioTransform.Find("CameraLookTarget");
        if (existing != null) return existing;

        GameObject target = new GameObject("CameraLookTarget");
        target.transform.SetParent(marioTransform);
        target.transform.localPosition = new Vector3(0f, verticalOffset, 0f);
        return target.transform;
    }
}
