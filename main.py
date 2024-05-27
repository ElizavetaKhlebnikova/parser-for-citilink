from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

CITILINK_URL = "https://www.citilink.ru"
CITILINK_CATALOG_URL = CITILINK_URL + "/catalog/krupnaya-bytovaya-tehnika/"

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
driver.maximize_window()


def parse_appliances():
    data = []
    driver.get(CITILINK_CATALOG_URL)
    try:
        item_grid = WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, ".edhylph0.app-catalog-1sl3l2s.e3tyxgd0")
            )
        )
        item_hrefs = item_grid.find_elements(By.CSS_SELECTOR, "a")
        for item_href in item_hrefs:
            url = item_href.get_attribute("href")  # находим url категории
            driver.get(url)
            try:
                # переходим в каталог категории
                products_cards = WebDriverWait(driver, 10).until(
                    expected_conditions.presence_of_element_located(
                        (By.CSS_SELECTOR, ".ehanbgo0.app-catalog-1rygk07.e1loosed0")
                    )
                )
                # находим все ссылки продуктов в категории
                products_hrefs = list(map(lambda x: x.get_attribute("href"), products_cards.find_elements(By.CSS_SELECTOR, ".app-catalog-fjtfe3.e1lhaibo0")))

                for product_href in products_hrefs:
                    # переходим по ссылке продукта
                    print(product_href)
                    try:
                        driver.get(product_href)
                        product = WebDriverWait(driver, 10).until(
                            expected_conditions.presence_of_element_located(
                                (By.CSS_SELECTOR, ".app-catalog-avk7an.ewgkexk0")
                            )
                        )
                        # тут можно извлекать информацию о продукте
                        title = product.find_element(By.CSS_SELECTOR,
                                                     ".e1ubbx7u0.eml1k9j0.app-catalog-lc5se5.e1gjr6xo0")
                        title_text = title.text
                        print(title_text)


                    except TimeoutException:
                        logging.warning(f"Не удалось загрузить страницу товара: {product_url}")

            except TimeoutException:
                logging.warning(f"Не удалось загрузить страницу категории: {url}")

    except TimeoutException:
        logging.error("Не удалось найти сетку товаров на странице каталога бытовой техники.")
        return data
    finally:
        driver.quit()

    return pd.DataFrame(data)


appliances_df = parse_appliances()
print(appliances_df)
