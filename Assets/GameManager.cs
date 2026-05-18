using UnityEngine;
using UnityEngine.SceneManagement;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance { get; private set; }

    [SerializeField] private int maxLives = 1;

    public int Lives { get; private set; }
    public int Score { get; private set; }

    private GameObject mario;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void AutoCreate()
    {
        if (FindAnyObjectByType<GameManager>() != null) return;
        new GameObject("GameManager").AddComponent<GameManager>();
    }

    void Awake()
    {
        if (Instance != null) { Destroy(gameObject); return; }
        Instance = this;
        Lives = maxLives;
    }

    void Start()
    {
        mario = GameObject.FindWithTag("Player");
    }

    public void OnMarioDied()
    {
        Lives--;
        HUDManager.Instance?.UpdateLives(Lives);

        if (Lives <= 0)
            Invoke(nameof(ShowGameOver), 1.5f);
    }

    public void DoRespawn()
    {
        mario.GetComponent<MarioAnimationController>().Respawn(new Vector3(0.2f, 0.2f, 0.2f));
    }

    public void AddScore(int points)
    {
        Score += points;
        HUDManager.Instance?.UpdateScore(Score);
    }

    private void ShowGameOver()
    {
        HUDManager.Instance?.ShowGameOver();
    }

    public void RestartGame()
    {
        Time.timeScale = 1f;
        SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
    }
}
