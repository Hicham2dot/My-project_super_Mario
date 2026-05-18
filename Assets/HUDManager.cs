using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

public class HUDManager : MonoBehaviour
{
    public static HUDManager Instance { get; private set; }

    private Text livesText;
    private Text scoreText;
    private GameObject gameOverPanel;

    // Crée le HUDManager automatiquement au démarrage du jeu
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void AutoCreate()
    {
        if (FindAnyObjectByType<HUDManager>() != null) return;
        new GameObject("HUDManager").AddComponent<HUDManager>();
    }

    void Awake()
    {
        if (Instance != null) { Destroy(gameObject); return; }
        Instance = this;
        BuildHUD();
    }

    private void BuildHUD()
    {
        // EventSystem requis pour que les boutons reçoivent les clics
        if (FindAnyObjectByType<EventSystem>() == null)
        {
            GameObject es = new GameObject("EventSystem");
            es.AddComponent<EventSystem>();
            es.AddComponent<StandaloneInputModule>();
        }

        // Canvas principal
        GameObject canvasGO = new GameObject("HUDCanvas");
        Canvas canvas = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 10;
        canvasGO.AddComponent<CanvasScaler>();
        canvasGO.AddComponent<GraphicRaycaster>();

        Font font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");

        // --- Vies (haut gauche) ---
        livesText = CreateLabel(canvasGO.transform, "LivesText", "Vies: 3",
            new Vector2(0f, 1f), new Vector2(0f, 1f), new Vector2(10f, -10f), new Vector2(200f, 50f), font);

        // --- Score (haut droite) ---
        scoreText = CreateLabel(canvasGO.transform, "ScoreText", "Score: 0",
            new Vector2(1f, 1f), new Vector2(1f, 1f), new Vector2(-210f, -10f), new Vector2(200f, 50f), font);
        scoreText.alignment = TextAnchor.UpperRight;

        // --- Écran Game Over ---
        gameOverPanel = BuildGameOverPanel(canvasGO.transform, font);
        gameOverPanel.SetActive(false);
    }

    private Text CreateLabel(Transform parent, string name, string content,
        Vector2 anchorMin, Vector2 anchorMax, Vector2 anchoredPos, Vector2 size, Font font)
    {
        GameObject go = new GameObject(name);
        go.transform.SetParent(parent, false);
        Text txt = go.AddComponent<Text>();
        txt.text      = content;
        txt.font      = font;
        txt.fontSize  = 32;
        txt.fontStyle = FontStyle.Bold;
        txt.color     = Color.white;
        txt.alignment = TextAnchor.UpperLeft;
        RectTransform rt = go.GetComponent<RectTransform>();
        rt.anchorMin        = anchorMin;
        rt.anchorMax        = anchorMax;
        rt.anchoredPosition = anchoredPos;
        rt.sizeDelta        = size;
        return txt;
    }

    private GameObject BuildGameOverPanel(Transform parent, Font font)
    {
        GameObject panel = new GameObject("GameOverPanel");
        panel.transform.SetParent(parent, false);
        Image bg = panel.AddComponent<Image>();
        bg.color = new Color(0f, 0f, 0f, 0.7f);
        RectTransform rt = panel.GetComponent<RectTransform>();
        rt.anchorMin = Vector2.zero;
        rt.anchorMax = Vector2.one;
        rt.offsetMin = rt.offsetMax = Vector2.zero;

        // Texte Game Over
        GameObject textGO = new GameObject("GameOverText");
        textGO.transform.SetParent(panel.transform, false);
        Text txt = textGO.AddComponent<Text>();
        txt.text      = "GAME OVER";
        txt.font      = font;
        txt.fontSize  = 80;
        txt.fontStyle = FontStyle.Bold;
        txt.color     = Color.red;
        txt.alignment = TextAnchor.MiddleCenter;
        RectTransform trt = textGO.GetComponent<RectTransform>();
        trt.anchorMin = new Vector2(0f, 0.55f);
        trt.anchorMax = new Vector2(1f, 0.75f);
        trt.offsetMin = trt.offsetMax = Vector2.zero;

        // Bouton Rejouer
        GameObject btnGO = new GameObject("RestartButton");
        btnGO.transform.SetParent(panel.transform, false);
        Image btnImg = btnGO.AddComponent<Image>();
        btnImg.color = new Color(0.2f, 0.6f, 0.2f, 1f);
        Button btn = btnGO.AddComponent<Button>();
        btn.onClick.AddListener(() => GameManager.Instance.RestartGame());
        RectTransform brt = btnGO.GetComponent<RectTransform>();
        brt.anchorMin        = new Vector2(0.35f, 0.35f);
        brt.anchorMax        = new Vector2(0.65f, 0.48f);
        brt.offsetMin = brt.offsetMax = Vector2.zero;

        GameObject btnTxtGO = new GameObject("ButtonText");
        btnTxtGO.transform.SetParent(btnGO.transform, false);
        Text btnTxt = btnTxtGO.AddComponent<Text>();
        btnTxt.text      = "Rejouer";
        btnTxt.font      = font;
        btnTxt.fontSize  = 40;
        btnTxt.fontStyle = FontStyle.Bold;
        btnTxt.color     = Color.white;
        btnTxt.alignment = TextAnchor.MiddleCenter;
        RectTransform btrt = btnTxtGO.GetComponent<RectTransform>();
        btrt.anchorMin = Vector2.zero;
        btrt.anchorMax = Vector2.one;
        btrt.offsetMin = btrt.offsetMax = Vector2.zero;

        return panel;
    }

    public void UpdateLives(int lives) => livesText.text = "Vies: " + lives;
    public void UpdateScore(int score) => scoreText.text = "Score: " + score;
    public void ShowGameOver()
    {
        gameOverPanel.SetActive(true);
        Time.timeScale = 0f;
    }
}
