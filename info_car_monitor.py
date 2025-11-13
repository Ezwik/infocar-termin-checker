import smtplib
import ssl
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os

INFOCAR_LOGIN = os.environ.get("INFOCAR_LOGIN")
INFOCAR_PASS = os.environ.get("INFOCAR_PASS")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

def send_email(subject, body):
    message = f"Subject: {subject}\n\n{body}"
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_SENDER, EMAIL_PASS)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message)

def check_info_car():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=opts)

    try:
        driver.get("https://info-car.pl/new/prawo-jazdy/sprawdz-wolny-termin")
        time.sleep(3)

        # Kliknij "Zaloguj"
        login_link = driver.find_element(By.LINK_TEXT, "Zaloguj")
        login_link.click()
        time.sleep(2)

        driver.find_element(By.ID, "username").send_keys(INFOCAR_LOGIN)
        driver.find_element(By.ID, "password").send_keys(INFOCAR_PASS)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(6)

        # Tutaj możesz zmienić: wybierz WORD, kategorię itp.
        html = driver.page_source
        if "Brak wolnych terminów" in html:
            print("Brak wolnych terminów.")
        else:
            print("Znaleziono termin!")
            send_email(
                "🚗 Info-Car – znaleziono termin!",
                "Pojawił się wolny termin na stronie Info-Car! Sprawdź: https://info-car.pl/new/prawo-jazdy/sprawdz-wolny-termin"
            )

    finally:
        driver.quit()

if __name__ == "__main__":
    check_info_car()
