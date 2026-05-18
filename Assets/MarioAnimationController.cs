using System.Collections;
using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
[RequireComponent(typeof(CapsuleCollider))]
public class MarioAnimationController : MonoBehaviour
{
    [Header("Vitesses")]
    [SerializeField] private float walkSpeed = 3f;
    [SerializeField] private float runSpeed  = 6f;

    [Header("Saut")]
    [SerializeField] private float jumpForce          = 14f;
    [SerializeField] private float fallGravityMult    = 3f;
    [SerializeField] private float releaseGravityMult = 2f;

    [Header("Sol")]
    [SerializeField] private LayerMask groundMask;
    [SerializeField] private float groundCheckRadius = 0.45f;
    [SerializeField] private float groundCheckOffset = 0.1f;

    private Animator        animator;
    private Rigidbody       rb;
    private CapsuleCollider col;

    private Vector3    moveInput      = Vector3.zero;
    private float      currentSpeed   = 0f;
    private bool       jumpRequest    = false;
    private bool       isGrounded     = false;
    private bool       isDead         = false;
    private bool       holdJump       = false;
    private Vector3    lastFaceDir    = Vector3.forward;
    private Quaternion targetRotation = Quaternion.identity;
    private bool       rotationDirty  = false;

    // Position sauvegardée avant toute physique = vrai point de départ
    public Vector3 InitialPosition { get; private set; }

    void Awake()
    {
        InitialPosition = transform.position;
    }

    void Start()
    {
        rb  = GetComponent<Rigidbody>();
        col = GetComponent<CapsuleCollider>();

        animator = GetComponent<Animator>();
        if (animator == null) animator = GetComponentInChildren<Animator>();
        if (animator == null) animator = GetComponentInParent<Animator>();
        if (animator == null)
            Debug.LogError("[Mario] Animator introuvable sur " + gameObject.name);

        if (animator != null)
            animator.applyRootMotion = false;

        targetRotation = transform.rotation;

        rb.constraints            = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;
        rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
        rb.interpolation = RigidbodyInterpolation.Interpolate;

        PhysicsMaterial pm = new PhysicsMaterial("Mario_NoFriction")
        {
            dynamicFriction = 0f,
            staticFriction  = 0f,
            bounciness      = 0f,
            frictionCombine = PhysicsMaterialCombine.Minimum,
            bounceCombine   = PhysicsMaterialCombine.Minimum
        };
        col.material = pm;
        col.center = new Vector3(0f, col.height * 0.5f, 0f);
    }

    void Update()
    {
        if (isDead) return;

        bool right   = Input.GetKey(KeyCode.RightArrow);
        bool left    = Input.GetKey(KeyCode.LeftArrow);
        bool forward = Input.GetKey(KeyCode.UpArrow);
        bool back    = Input.GetKey(KeyCode.DownArrow);
        bool run     = Input.GetKey(KeyCode.Z);
        bool jump    = Input.GetKey(KeyCode.E);

        holdJump = jump;

        float dx = (right ? 1f : 0f) - (left    ? 1f : 0f);
        float dz = (forward ? 1f : 0f) - (back   ? 1f : 0f);
        Vector3 arrowDir = new Vector3(dx, 0f, dz).normalized;

        if (arrowDir != Vector3.zero)
        {
            UpdateFacing(arrowDir);
            currentSpeed = run ? runSpeed : walkSpeed;
            moveInput    = arrowDir;
        }
        else
        {
            currentSpeed = 0f;
            moveInput    = Vector3.zero;
        }

        if (jump && isGrounded)
            jumpRequest = true;

        UpdateAnimation();
    }

    void FixedUpdate()
    {
        if (isDead) return;

        rb.angularVelocity = Vector3.zero;

        if (rotationDirty)
        {
            rb.MoveRotation(targetRotation);
            rotationDirty = false;
        }

        CheckGrounded();

        if (moveInput == Vector3.zero)
        {
            rb.linearVelocity = new Vector3(0f, rb.linearVelocity.y, 0f);
            rb.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ
                           | RigidbodyConstraints.FreezePositionX | RigidbodyConstraints.FreezePositionZ;
        }
        else
        {
            rb.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;
            Vector3 hVel = moveInput * currentSpeed;
            rb.linearVelocity = new Vector3(hVel.x, rb.linearVelocity.y, hVel.z);
        }

        if (jumpRequest)
        {
            rb.linearVelocity = new Vector3(rb.linearVelocity.x, 0f, rb.linearVelocity.z);
            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
            jumpRequest = false;
        }

        if (rb.linearVelocity.y < 0f)
            rb.linearVelocity += Vector3.up * Physics.gravity.y * (fallGravityMult - 1f) * Time.fixedDeltaTime;
        else if (rb.linearVelocity.y > 0f && !holdJump)
            rb.linearVelocity += Vector3.up * Physics.gravity.y * (releaseGravityMult - 1f) * Time.fixedDeltaTime;
    }

    private void CheckGrounded()
    {
        Vector3 origin = transform.position + Vector3.up * (groundCheckRadius + 0.01f);
        isGrounded = Physics.SphereCast(
            origin, groundCheckRadius, Vector3.down, out _,
            groundCheckOffset + 0.01f, groundMask, QueryTriggerInteraction.Ignore);
    }

    private void UpdateAnimation()
    {
        string anim;
        if      (!isGrounded)              anim = "jump";
        else if (currentSpeed >= runSpeed) anim = "run";
        else if (currentSpeed > 0f)        anim = "walk";
        else                               anim = "idle";
        PlayAnimation(anim);
    }

    private void UpdateFacing(Vector3 dir)
    {
        if (dir == lastFaceDir) return;
        lastFaceDir    = dir;
        targetRotation = Quaternion.LookRotation(dir);
        rotationDirty  = true;
    }

    private void PlayAnimation(string animName)
    {
        if (animator == null) return;
        AnimatorStateInfo state = animator.GetCurrentAnimatorStateInfo(0);
        if (state.IsName(animName)) return;
        if (animator.IsInTransition(0) && animator.GetNextAnimatorStateInfo(0).IsName(animName)) return;
        animator.CrossFade(animName, 0f);
    }

    private IEnumerator DeathSequence()
    {
        if (isDead) yield break;
        isDead = true;

        // Déduire la vie immédiatement
        GameManager.Instance?.OnMarioDied();

        rb.linearVelocity = Vector3.zero;
        rb.isKinematic    = true;

        animator.CrossFade("die", 0.05f);
        yield return new WaitForSeconds(0.1f);

        while (true)
        {
            AnimatorStateInfo info = animator.GetCurrentAnimatorStateInfo(0);
            if (info.IsName("die") && info.normalizedTime >= 1f) break;
            yield return null;
        }

        if (GameManager.Instance != null && GameManager.Instance.Lives > 0)
            GameManager.Instance.DoRespawn();
    }

    public void TakeDamage()
    {
        StartCoroutine(DeathSequence());
    }
    public void Respawn(Vector3 position){
        isDead = false;
        transform.position = position;
        rb.isKinematic    = false;
        rb.linearVelocity = Vector3.zero;
        PlayAnimation("idle");
    }

}
