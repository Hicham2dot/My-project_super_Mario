using System.Collections;
using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
[RequireComponent(typeof(CapsuleCollider))]
public class GoombaController : MonoBehaviour
{
    [Header("Ground assigné")]
    [Tooltip("Faites glisser ici le Ground sur lequel ce Goomba patrouille")]
    [SerializeField] private GameObject assignedGround;

    [Header("Patrouille")]
    [SerializeField] private float moveSpeed        = 2f;
    [SerializeField] private float dirChangeMinTime = 2f;
    [SerializeField] private float dirChangeMaxTime = 5f;

    [Header("Détection Mario")]
    [SerializeField] private float stomDamageY = -0.5f;

    [Header("Noms des animations")]
    [SerializeField] private string animWalk  = "walk";
    [SerializeField] private string animDeath = "death";

    // ── références ────────────────────────────────────────────────
    private Animator         animator;
    private Rigidbody        rb;
    private CapsuleCollider  col;

    // ── limites du Ground (X et Z) ────────────────────────────────
    private float boundMinX, boundMaxX;
    private float boundMinZ, boundMaxZ;

    // ── état interne ──────────────────────────────────────────────
    private Vector3 moveDir     = Vector3.zero;
    private Vector3 targetPos   = Vector3.zero;
    private bool    isDead      = false;
    private string  currentAnim = "";
    private bool    redirectNeeded = false; // signale à PatrolLoop de choisir une nouvelle cible

    // ─────────────────────────────────────────────────────────────
    void Start()
    {
        rb  = GetComponent<Rigidbody>();
        col = GetComponent<CapsuleCollider>();
        animator = GetComponent<Animator>();
        if (animator == null) animator = GetComponentInChildren<Animator>();

        rb.freezeRotation        = true;
        rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
        rb.constraints = RigidbodyConstraints.FreezeRotationX
                       | RigidbodyConstraints.FreezeRotationY
                       | RigidbodyConstraints.FreezeRotationZ;

        ComputeGroundBounds();
        PickNewTarget();
        StartCoroutine(PatrolLoop());
        PlayAnim(animWalk);
    }

    private void ComputeGroundBounds()
    {
        if (assignedGround == null)
        {
            boundMinX = transform.position.x - 4f;
            boundMaxX = transform.position.x + 4f;
            boundMinZ = transform.position.z - 4f;
            boundMaxZ = transform.position.z + 4f;
            Debug.LogWarning("[Goomba] Aucun Ground assigné sur " + gameObject.name);
            return;
        }

        Collider c = assignedGround.GetComponent<Collider>();
        if (c != null)
        {
            boundMinX = c.bounds.min.x;
            boundMaxX = c.bounds.max.x;
            boundMinZ = c.bounds.min.z;
            boundMaxZ = c.bounds.max.z;
            return;
        }

        Renderer rend = assignedGround.GetComponent<Renderer>();
        if (rend != null)
        {
            boundMinX = rend.bounds.min.x;
            boundMaxX = rend.bounds.max.x;
            boundMinZ = rend.bounds.min.z;
            boundMaxZ = rend.bounds.max.z;
            return;
        }

        boundMinX = assignedGround.transform.position.x - 4f;
        boundMaxX = assignedGround.transform.position.x + 4f;
        boundMinZ = assignedGround.transform.position.z - 4f;
        boundMaxZ = assignedGround.transform.position.z + 4f;
    }

    void FixedUpdate()
    {
        if (isDead) return;

        rb.angularVelocity = Vector3.zero;

        // Détection de bord : rayon vers le bas devant le Goomba.
        // S'il n'y a plus de sol devant lui, on l'arrête et on demande une nouvelle cible.
        if (moveDir != Vector3.zero && IsNearEdge())
        {
            moveDir         = Vector3.zero;
            redirectNeeded  = true;
            rb.linearVelocity = new Vector3(0f, rb.linearVelocity.y, 0f);
            return;
        }

        rb.linearVelocity = new Vector3(moveDir.x * moveSpeed, rb.linearVelocity.y, moveDir.z * moveSpeed);

        if (moveDir != Vector3.zero)
            rb.MoveRotation(Quaternion.LookRotation(moveDir));
    }

    // Vérifie si le sol disparaît juste devant le Goomba
    private bool IsNearEdge()
    {
        // Utilise les bounds monde pour la distance de projection
        float stepAhead = Mathf.Max(col.bounds.extents.x, col.bounds.extents.z, 0.2f) + 0.15f;
        Vector3 checkPos = transform.position + moveDir * stepAhead + Vector3.up * 0.2f;
        return !Physics.Raycast(checkPos, Vector3.down, 1.0f, ~0, QueryTriggerInteraction.Ignore);
    }

    private IEnumerator PatrolLoop()
    {
        while (!isDead)
        {
            redirectNeeded = false;
            float elapsed  = 0f;

            // Marche vers la cible, avec timeout pour les cas de blocage
            while (!isDead)
            {
                if (redirectNeeded) break;

                float dist = Vector2.Distance(
                    new Vector2(transform.position.x, transform.position.z),
                    new Vector2(targetPos.x, targetPos.z));
                if (dist <= 0.3f) break;

                elapsed += Time.fixedDeltaTime;
                if (elapsed > 6f) break; // timeout : bloqué par un obstacle → nouvelle cible

                yield return new WaitForFixedUpdate();
            }

            if (isDead) yield break;

            // Pause sur place
            moveDir = Vector3.zero;
            rb.linearVelocity = new Vector3(0f, rb.linearVelocity.y, 0f);

            // Pas de pause si on a redirigé (bord ou blocage) : rechoisir immédiatement
            if (!redirectNeeded)
            {
                float pause = Random.Range(dirChangeMinTime, dirChangeMaxTime);
                yield return new WaitForSeconds(pause);
            }

            if (!isDead)
            {
                PickNewTarget();
                PlayAnim(animWalk);
            }
        }
    }

    private void PickNewTarget()
    {
        float tx = Random.Range(boundMinX + 0.5f, boundMaxX - 0.5f);
        float tz = Random.Range(boundMinZ + 0.5f, boundMaxZ - 0.5f);
        targetPos = new Vector3(tx, transform.position.y, tz);

        Vector3 dir = new Vector3(tx - transform.position.x, 0f, tz - transform.position.z);
        moveDir = dir.magnitude > 0.01f ? dir.normalized : Vector3.forward;
    }

    // ── Collision avec Mario ──────────────────────────────────────
    void OnCollisionEnter(Collision col)
    {
        if (isDead) return;
        if (!col.gameObject.CompareTag("Player")) return;

        Rigidbody marioRb = col.gameObject.GetComponent<Rigidbody>();
        float marioVY = marioRb != null ? marioRb.linearVelocity.y : 0f;

        if (marioVY <= stomDamageY)
        {
            StartCoroutine(Die());
            if (marioRb != null)
                marioRb.linearVelocity = new Vector3(
                    marioRb.linearVelocity.x, 6f, marioRb.linearVelocity.z);
        }
        else
        {
            col.gameObject.SendMessage("TakeDamage", SendMessageOptions.DontRequireReceiver);
        }
    }

    // ── Séquence de mort ──────────────────────────────────────────
    private IEnumerator Die()
    {
        isDead  = true;
        moveDir = Vector3.zero;

        rb.linearVelocity = Vector3.zero;
        rb.isKinematic    = true;

        PlayAnim(animDeath);

        yield return new WaitForSeconds(0.1f);
        if (animator != null)
        {
            while (true)
            {
                AnimatorStateInfo info = animator.GetCurrentAnimatorStateInfo(0);
                if (info.IsName(animDeath) && info.normalizedTime >= 1f) break;
                yield return null;
            }
        }
        else
        {
            yield return new WaitForSeconds(0.5f);
        }

        Destroy(gameObject);
    }

    private void PlayAnim(string animName)
    {
        if (animator == null || currentAnim == animName) return;
        currentAnim = animName;
        animator.CrossFade(animName, 0.1f);
    }

    void OnDrawGizmosSelected()
    {
        if (!Application.isPlaying) return;
        Gizmos.color = Color.yellow;
        float y = transform.position.y;
        Gizmos.DrawLine(new Vector3(boundMinX, y, boundMinZ), new Vector3(boundMaxX, y, boundMinZ));
        Gizmos.DrawLine(new Vector3(boundMaxX, y, boundMinZ), new Vector3(boundMaxX, y, boundMaxZ));
        Gizmos.DrawLine(new Vector3(boundMaxX, y, boundMaxZ), new Vector3(boundMinX, y, boundMaxZ));
        Gizmos.DrawLine(new Vector3(boundMinX, y, boundMaxZ), new Vector3(boundMinX, y, boundMinZ));
        Gizmos.color = Color.red;
        Gizmos.DrawSphere(new Vector3(targetPos.x, y, targetPos.z), 0.2f);
    }
}
