using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class FinishLine : MonoBehaviour
{
    private GameObject canvasGO;
    private bool       triggered = false;

    void Start()
    {
        // Le collider du cube doit être en mode Trigger
        Collider col = GetComponent<Collider>();
        if (col != null) col.isTrigger = true;

        BuildUI();
    }

    void OnTriggerEnter(Collider other)
    {
        if (triggered) return;
        if (!other.CompareTag("Player")) return;

        triggered = true;
        canvasGO.SetActive(true);

        // Stoppe le temps (optionnel)
        Time.timeScale = 0f;
    }

    private void BuildUI()
    {
        // Canvas
        canvasGO = new GameObject("WinCanvas");
        Canvas canvas = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvasGO.AddComponent<CanvasScaler>();
        canvasGO.AddComponent<GraphicRaycaster>();

        // Fond semi-transparent
        GameObject panel = new GameObject("Panel");
        panel.transform.SetParent(canvasGO.transform, false);
        Image bg = panel.AddComponent<Image>();
        bg.color = new Color(0f, 0f, 0f, 0.55f);
        RectTransform panelRect = panel.GetComponent<RectTransform>();
        panelRect.anchorMin = Vector2.zero;
        panelRect.anchorMax = Vector2.one;
        panelRect.offsetMin = Vector2.zero;
        panelRect.offsetMax = Vector2.zero;

        Font font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");

        // Texte "Vous avez gagné !"
        GameObject textGO = new GameObject("WinText");
        textGO.transform.SetParent(panel.transform, false);
        Text txt = textGO.AddComponent<Text>();
        txt.text      = "Vous avez gagné !";
        txt.font      = font;
        txt.fontSize  = 72;
        txt.fontStyle = FontStyle.Bold;
        txt.color     = Color.yellow;
        txt.alignment = TextAnchor.MiddleCenter;
        RectTransform tr = textGO.GetComponent<RectTransform>();
        tr.anchorMin        = new Vector2(0f, 0.55f);
        tr.anchorMax        = new Vector2(1f, 0.85f);
        tr.offsetMin        = Vector2.zero;
        tr.offsetMax        = Vector2.zero;

        // Bouton Rejouer
        GameObject btnGO = new GameObject("ReplayButton");
        btnGO.transform.SetParent(panel.transform, false);
        Image btnImg = btnGO.AddComponent<Image>();
        btnImg.color = new Color(0.2f, 0.6f, 0.2f, 1f);
        Button btn = btnGO.AddComponent<Button>();
        btn.onClick.AddListener(() => { Time.timeScale = 1f; SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex); });
        RectTransform brt = btnGO.GetComponent<RectTransform>();
        brt.anchorMin        = new Vector2(0.35f, 0.35f);
        brt.anchorMax        = new Vector2(0.65f, 0.48f);
        brt.offsetMin        = Vector2.zero;
        brt.offsetMax        = Vector2.zero;

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

        canvasGO.SetActive(false);
    }
}
