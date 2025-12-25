"""
Test du dashboard avec Playwright
"""
from playwright.sync_api import sync_playwright
import time

def test_dashboard():
    with sync_playwright() as p:
        # Lancer le navigateur
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("🌐 Navigation vers le dashboard...")
        page.goto("http://localhost:5174")

        # Attendre le chargement
        time.sleep(2)

        print("📸 Capture du dashboard...")
        page.screenshot(path="dashboard_screenshot.png", full_page=True)

        # Vérifier le titre
        title = page.title()
        print(f"📋 Titre de la page: {title}")

        # Vérifier que le contenu se charge
        content = page.content()
        print(f"📄 Taille du HTML: {len(content)} caractères")

        # Rechercher les éléments clés
        print("\n🔍 Éléments détectés:")

        # Chercher les KPI cards
        kpi_cards = page.query_selector_all(".rounded-lg")
        print(f"   - KPI Cards: {len(kpi_cards)} détectées")

        # Chercher les graphiques
        charts = page.query_selector_all("canvas")
        print(f"   - Graphiques (canvas): {len(charts)} détectés")

        # Vérifier les erreurs console
        print("\n🐛 Console du navigateur:")
        page.on("console", lambda msg: print(f"   [{msg.type()}] {msg.text()}"))

        time.sleep(3)

        print("\n✅ Test terminé!")
        print(f"📷 Screenshot sauvegardé: dashboard_screenshot.png")

        browser.close()

if __name__ == "__main__":
    test_dashboard()
