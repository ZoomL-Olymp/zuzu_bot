from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from utils import clean_price_string

def parse_website_price(url, xpath):
    """Парсит цену товара с сайта по URL и XPath."""
    chrome_options = Options()
    chrome_options.add_argument('--headless') # Запуск в фоновом режиме без GUI
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options) # Инициализация ChromeDriver

    try:
        driver.get(url)
        price_element = driver.find_element(By.XPATH, xpath)
        price_text = price_element.text
        cleaned_price = clean_price_string(price_text)
        return cleaned_price
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}") # Логирование ошибки (можно улучшить)
        return None
    finally:
        driver.quit()

def get_average_prices(websites_data, product_name="зюзюблик"): # Можно сделать product_name параметром
    """Парсит цены с сайтов и вычисляет среднюю цену для каждого сайта."""
    average_prices = {}
    for website in websites_data:
        prices = [] # Список для хранения цен с одного сайта (если нужно несколько товаров)
        price = parse_website_price(website['url'], website['xpath'])
        if price is not None:
            prices.append(price)

        if prices:
            average_price = sum(prices) / len(prices)
            average_prices[website['title']] = average_price
        else:
            average_prices[website['title']] = "Цена не найдена или не удалось спарсить" # Или None, или другое значение по умолчанию

    return average_prices

if __name__ == '__main__':
    # Пример использования (для тестирования парсера отдельно)
    example_websites = [
        {"title": "Сайт 1", "url": "https://www.citilink.ru/product/videokarta-palit-geforce-rtx-4060-ti-dual-8gb-ne6406t019p1-1070d-808782/", "xpath": "//span[@class='ProductHeader__price-default_current-price']"},
        {"title": "Сайт 2", "url": "https://www.dns-shop.ru/product/92c68a422120d7b4ee74b15905164d39/videokarta-palit-geforce-rtx-4060-ti-dual-ne6406t019p1-1070d/", "xpath": "//span[@class='price-item-block']"}
    ]
    average_prices = get_average_prices(example_websites)
    print("Средние цены на зюзюблики (в данном случае видеокарты RTX 4060 Ti):")
    for title, avg_price in average_prices.items():
        print(f"- {title}: {avg_price}")