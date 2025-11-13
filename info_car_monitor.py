from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import smtplib
from email.message import EmailMessage
import time

# -----------------------------
# Funkcja wysyłająca mail
# -----------------------------
def send_email(subject, body):
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")  # tutaj hasło aplikacji Gmail
    EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASS)
            server.send_message(msg)
        print("✅ Wysłano maila")
    except Exception as e:
        print("❌ Błąd wysyłki maila:", e)

# -----------------------------
# Funkcja główna
# -----------------------------
def check_info_car():
    INFOCAR_EMAIL = os.getenv("INFOCAR_EMAIL")
    INFOCAR_PASS = os.getenv("INFOCAR_PASS")

    # -----------------------------
    # Konfiguracja Selenium
    # -----------------------------
    opts = Options()
    opts.binary_location = "/usr/bin/chromium-browser"  # dla GitHub Actions
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=opts)

    try:
        # 1. Otwórz stronę z terminami
        driver.get("https://info-car.pl/new/prawo-jazdy/sprawdz-wolny-termin")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print("✅ Strona główna załadowana")

        # 2. Kliknij "Akceptuj cookies" jeśli istnieje
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Akceptuj')]"))
            ).click()
            print("✅ Kliknięto 'Akceptuj cookies'")
        except:
            print("ℹ️ Brak banera cookies - pomijam")

        # 3. Kliknij "Zaloguj"
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Zaloguj"))
        ).click()
        print("✅ Kliknięto 'Zaloguj'")

        # 4. Poczekaj na stronę logowania
        WebDriverWait(driver, 10).until(EC.url_contains("oauth2/login"))
        print("✅ Przeniesiono na stronę logowania")

        # 5. Wprowadź dane logowania
        driver.find_element(By.ID, "username").send_keys(INFOCAR_EMAIL)
        driver.find_element(By.ID, "password").send_keys(INFOCAR_PASS)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Zaloguj')]").click()
        print("✅ Dane logowania wysłane, kliknięto 'Zaloguj'")

        # 6. Poczekaj na stronę wyboru WORD i kategorii
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "wordSelector"))
        )

        # 7. Wybierz WORD Katowice
        driver.find_element(By.XPATH, "//option[contains(text(), 'Katowice')]").click()
        time.sleep(1)

        # 8. Wybierz kategorię C
        driver.find_element(By.XPATH, "//option[contains(text(), 'C')]").click()
        time.sleep(1)

        # 9. Wybierz egzamin praktyczny
        driver.find_element(By.XPATH, "//option[contains(text(), 'Praktyka')]").click()
        time.sleep(1)

        # 10. Sprawdź dostępność terminów
        # Zakładamy, że terminów jest lista w tabeli lub divach z określoną klasą
        try:
            wolne_terminy = driver.find_elements(By.XPATH, "//div[contains(@class, 'termin')]")
            if wolne_terminy:
                send_email("✅ Info-Car: Wolny termin!", f"Znaleziono termin! Liczba: {len(wolne_terminy)}")
            else:
                print("ℹ️ Brak wolnych terminów")
        except Exception as e:
            print("❌ Błąd przy sprawdzaniu terminów:", e)

    except Exception as e:
        print("❌ Wystąpił błąd:", e)
        send_email("❗ Błąd w InfoCarChecker", str(e))

    finally:
        driver.quit()

# -----------------------------
# Uruchomienie funkcji
# -----------------------------
if __name__ == "__main__":
    check_info_car()
