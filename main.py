import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import random
import time
from dotenv import load_dotenv
import smtplib

load_dotenv()


ua = UserAgent(os='windows', browsers=['edge', 'chrome'], min_percentage=1.3)
random_user_agent = ua.random


options = Options()
options.add_argument(f"user-agent={random_user_agent}")
options.add_argument("--headless")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


urls = [
    "https://www.amazon.com/Kasa-Starlight-Detection-Compatible-KC420WS/dp/B09SBRB59Z/ref=lp_19185106011_1_6?pf_rd_p=53d84f87-8073-4df1-9740-1bf3fa798149&pf_rd_r=NBTM5YD14F1RCBZWGH0C&sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D",
    "https://www.amazon.com/Galayou-Security-Cameras-Storage-G7/dp/B0BD5VXKGW/ref=pd_ci_mcx_pspc_dp_d_2_t_1?pd_rd_w=pLTy7&content-id=amzn1.sym.568f3b6b-5aad-4bfd-98ee-d827f03151e4&pf_rd_p=568f3b6b-5aad-4bfd-98ee-d827f03151e4&pf_rd_r=9GMDJDZJDGSYKKVP5QTM&pd_rd_wg=b4Nz4&pd_rd_r=deff0aaa-0267-4e9f-a5de-8f046538b52c&pd_rd_i=B0BD5VXKGW&th=1",
    "https://www.amazon.com/dp/B0BRKJ3323/ref=sspa_dk_detail_4?psc=1&pd_rd_i=B0BRKJ3323&pd_rd_w=cY1oH&content-id=amzn1.sym.386c274b-4bfe-4421-9052-a1a56db557ab&pf_rd_p=386c274b-4bfe-4421-9052-a1a56db557ab&pf_rd_r=EBQ225APWVG8W4BQ79MD&pd_rd_wg=kMP03&pd_rd_r=07fd9b56-ce7a-4e89-86ae-e20fce5d0b96&s=photo&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWxfdGhlbWF0aWM"
]

for url in urls:
    try:
        driver.get(url)

        soup = BeautifulSoup(driver.page_source, "lxml")

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "productTitle")))

        product_name_element = soup.find("span", id="productTitle")
        product_name = product_name_element.text.strip().upper() if product_name_element else "Unknown Product"

        discount_span = soup.find("span",
                                  class_="a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage")

        if discount_span:

            discount_text = discount_span.text
            cleaned_discount = int(discount_text.replace("-", "").replace("%", ""))

            if cleaned_discount > 15:

                price_span = soup.find("span",
                                       class_="a-price aok-align-center reinventPricePriceToPayMargin priceToPay")
                price = price_span.text.split("$")[1] if price_span else "Unknown"

                message = f"{product_name} is on sale for {discount_text}\nPrice: ${price}\n\nClick the link: {url}"

                # Send email
                with smtplib.SMTP(os.environ["SMTP_ADDRESS"], port=587) as connection:
                    connection.starttls()
                    connection.login(os.environ["EMAIL_ADDRESS"], os.environ["EMAIL_PASSWORD"])
                    connection.sendmail(
                        from_addr=os.environ["EMAIL_ADDRESS"],
                        to_addrs=os.environ["EMAIL_ADDRESS"],
                        msg=f"Subject:Amazon Price Alert!\n\n{message}".encode("utf-8")
                    )
                print(f"Email sent to {product_name}")
            else:
                print(f"No significant discount found for {product_name}.")
        else:
            print(f"No discount information available for {product_name}.")
    except Exception as e:
        print(f"An error occurred for URL {url}: {e}")
time.sleep(random.randint(1, 2))

driver.quit()