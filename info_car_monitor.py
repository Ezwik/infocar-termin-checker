import smtplib
import ssl
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import os

# --- dane z GitHub Secrets ---
INFOCAR_LOGIN = os.environ.get("INFOCAR_LOGIN")
INFOCAR_PASS = os.environ.get("INFOCAR_PASS")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

def send_email(subject, body):
    """Wysyła e-mail powiadamiający."""
    message = f"Subject: {subject}\n\n{body}"
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_SENDER, EMAIL_PASS)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message)

def check_info_car():
    opts = Options()
    opts.binary_location = "/usr/bin/chromium-browser"
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=opts)

    try:
        print("Otwieram stronę Info-Car...")
        driver.get("https://info-car.pl/new/prawo-jazdy/sprawdz-wolny-termin")
        time.sleep(3)

        # kliknięcie "Zaloguj"
        driver.find_element(By.LINK_TEXT, "Zaloguj").click()
        time.sleep(2)

        # logowanie
        driver.find_element(By.ID, "username").send_keys(INFOCAR_LOGIN)
        driver.find_element(By.ID, "password").send_keys(INFOCAR_PASS)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(5)

        print("Zalogowano, wybieram WORD i egzamin...")

        # wybór WORD
        select_word = Select(driver.find_element(By.ID, "wojewodztwo"))
        select_word.select_by_visible_text("śląskie")
        time.sleep(2)

        select_word2 = Select(driver.find_element(By.ID, "osrodek"))
        select_word2.select_by_visible_text("Wojewódzki Ośrodek Ruchu Drogowego w Katowicach")
        time.sleep(2)

        # wybór rodzaju egzaminu
        select_exam = Select(driver.find_element(By.ID, "rodzajEgzaminu"))
        select_exam.select_by_visible_text("Egzamin praktyczny")
        time.sleep(1)

        # wybór kategorii
        select_cat = Select(driver.find_element(By.ID, "kategoria"))
        select_cat.select_by_visible_text("C")
        time.sleep(2)

        # kliknięcie "Szukaj terminów"
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(5)

        html = driver.page_source
        if "Brak wolnych terminów" in html:
            print("❌ Brak wolnych terminów w Katowicach (C, praktyka).")
        else:
            print("✅ ZNALEZIONO TERMIN!")
            send_email(
                "🚗 Info-Car – znaleziono termin!",
                "Pojawił się wolny termin w WORD Katowice (praktyka, kategoria C)!\nSprawdź: https://info-car.pl/new/prawo-jazdy/sprawdz-wolny-termin"
            )

    except Exception as e:
        print("Błąd:", e)
        send_email("❗ Błąd w InfoCarChecker", str(e))

    finally:
        driver.quit()

if __name__ == "__main__":
    check_info_car()
