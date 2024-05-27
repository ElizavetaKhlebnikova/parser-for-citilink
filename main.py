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
    except TimeoutException:
        logging.error("Не удалось найти сетку товаров на странице каталога бытовой техники.")
        return data

    for item_href in item_hrefs:
        url = item_href.get_attribute("href") # находим url категории
        driver.get(url)

        try:
            # переходим в каталог категории
            products_cards = WebDriverWait(driver, 10).until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, ".ehanbgo0.app-catalog-1rygk07.e1loosed0")
                )
            )
            # находим все ссылки продуктов в категории
            products_hrefs = products_cards.find_elements(By.CSS_SELECTOR, ".app-catalog-fjtfe3.e1lhaibo0")
        except TimeoutException:
            logging.warning(f"Не удалось загрузить страницу категории: {url}")
        # проходимся циклом по всем ссылкам
        for product_href in products_hrefs:
            product_url = product_href.get_attribute("href")
            # переходим по ссылке продукта
            driver.get(product_url)
            #
            # try:
            #     specs_div = driver.find_element(By.CSS_SELECTOR, "div.Specifications")
            #     specs_rows = specs_div.find_elements(By.CSS_SELECTOR, "div.Specifications__row")
            #     dimensions = None
            #     weight = None
            #     for specs_row in specs_rows:
            #         key = specs_row.find_element(By.CSS_SELECTOR, "div.Specifications__column_name").text
            #         value = specs_row.find_element(By.CSS_SELECTOR, "div.Specifications__column_value").text
            #         if key == "Размеры (ШхВхГ):":
            #             dimensions = value.split(" х ")
            #         elif key == "Вес(нетто)":
            #             weight = float(value.replace(" ", "").replace("кг", ""))
            #
            #     if dimensions and weight:
            #         height = int(dimensions[1].replace(" ", ""))
            #         depth = int(dimensions[2].replace(" ", "").replace(" см", ""))
            #         width = int(dimensions[0].replace(" ", ""))
            #         volume = height * depth * width / 1000000  # в кубических метрах
            #         density = weight / volume  # кг/м3
            #         data.append({
            #             "Наименование класса": title,
            #             "Объем (Высота _Глубина_ Ширина, м)": volume,
            #             "Вес, кг": weight,
            #             "Плотность, кг/m3": density,
            #             "Габариты (Высота Х Глубина Х  Ширина, см):": f"{height} x {depth} x {width}",
            #             "Высота, см": height,
            #             "Глубина, см": depth,
            #             "Ширина, см": width,
            #             "Высота / ширина": height / width,
            #             "Высота / глубина": height / depth
            #         })
            #
            # except NoSuchElementException:
            #     logging.warning(f"Не найдено спецификации для товара: {title}")

    driver.quit()
    return pd.DataFrame(data)


appliances_df = parse_appliances()
print(appliances_df)
