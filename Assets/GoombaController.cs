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
    private Animator  animator;
    private Rigidbody rb;

    // ── limites du Ground (X et Z) ────────────────────────────────
    private float boundMinX, boundMaxX;
    private float boundMinZ, boundMaxZ;

    // ── état interne ──────────────────────────────────────────────
    private Vector3 moveDir    = Vector3.zero;
    private Vector3 targetPos  = Vector3.zero;
    private bool    isDead     = false;
    private string  currentAnim = "";

    // ─────────────────────────────────────────────────────────────
    void Start()
    {
        rb       = GetComponent<Rigidbody>();
        animator = GetComponent<Animator>();
        if (animator == null) animator = GetComponentInChildren<Animator>();

        rb.freezeRotation = true;
        rb.constraints    = RigidbodyConstraints.FreezeRotationX
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

        Collider col = assignedGround.GetComponent<Collider>();
        if (col != null)
        {
            boundMinX = col.bounds.min.x;
            boundMaxX = col.bounds.max.x;
            boundMinZ = col.bounds.min.z;
            boundMaxZ = col.bounds.max.z;
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
        rb.linearVelocity  = new Vector3(moveDir.x * moveSpeed, rb.linearVelocity.y, moveDir.z * moveSpeed);

        if (moveDir != Vector3.zero)
            rb.MoveRotation(Quaternion.LookRotation(moveDir));
    }

    // Choisit un point 2D (X, Z) aléatoire dans les limites du Ground
    private void PickNewTarget()
    {
        float tx = Random.Range(boundMinX + 0.3f, boundMaxX - 0.3f);
        float tz = Random.Range(boundMinZ + 0.3f, boundMaxZ - 0.3f);
        targetPos = new Vector3(tx, transform.position.y, tz);

        Vector3 dir = new Vector3(tx - transform.position.x, 0f, tz - transform.position.z);
        moveDir = dir.magnitude > 0.01f ? dir.normalized : Vector3.forward;
    }

    private IEnumerator PatrolLoop()
    {
        while (!isDead)
        {
            // Marche vers la cible (distance 2D horizontale)
            while (!isDead)
            {
                float dist = Vector2.Distance(
                    new Vector2(transform.position.x, transform.position.z),
                    new Vector2(targetPos.x, targetPos.z));
                if (dist <= 0.2f) break;
                yield return new WaitForFixedUpdate();
            }

            if (isDead) yield break;

            // Pause sur place
            moveDir = Vector3.zero;
            rb.linearVelocity = new Vector3(0f, rb.linearVelocity.y, 0f);
            float pause = Random.Range(dirChangeMinTime, dirChangeMaxTime);
            yield return new WaitForSeconds(pause);

            if (!isDead)
                PickNewTarget();
        }
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

    // ── Gizmo : visualise les limites du Ground ───────────────────
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
