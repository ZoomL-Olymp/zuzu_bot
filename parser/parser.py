from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def clean_price_string(price_text):
    """
    Cleans the price string to extract a valid float value.

    Args:
        price_text (str): The raw price string from the webpage.

    Returns:
        float: The cleaned price as a float, or None if parsing fails.
    """
    cleaned_price = re.sub(r'[^\d.,]', '', price_text).strip()  # Remove non-numeric characters except ',' and '.'
    cleaned_price = cleaned_price.replace(',', '.')  # Standardize decimal separator to '.'

    if cleaned_price.count('.') > 1:
        parts = cleaned_price.split('.')
        # Check if it's a number with thousand separators (e.g., 1.234.567)
        if all(len(part) <= 3 for part in parts[1:]):  # Correctly handles thousand separators
              cleaned_price =  ''.join(parts) # if so remove dots
        else:
             return None # if not, price is not valid.

    try:
        return float(cleaned_price)  # Convert to float
    except ValueError:
        return None  # Return None if conversion fails


def parse_website_price(url, xpath):
    """
    Parses a website to extract prices of a product and calculates their average.

    Args:
        url (str): The URL of the website to parse.
        xpath (str): The XPath expression to locate the price elements.

    Returns:
        float: The average price found on the website, or None if no valid prices are found.
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
    chrome_options.add_argument('--no-sandbox')  # Bypass OS security model
    chrome_options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    chrome_options.add_argument('--disable-gpu') # applicable to windows os only
    chrome_options.add_argument('--window-size=1920,1080') # Set a reasonable window size.
    service = ChromeService(ChromeDriverManager().install())  # Use webdriver_manager to handle ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)  # Initialize Chrome WebDriver

    try:
        driver.get(url)  # Navigate to the URL
        driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to appear

        price_elements = driver.find_elements(By.XPATH, xpath)  # Find all elements matching the XPath
        prices = []
        for price_element in price_elements:
            price_text = price_element.text  # Get the text content of the element
            cleaned_price = clean_price_string(price_text)  # Clean and convert the price
            if cleaned_price is not None:
                prices.append(cleaned_price)  # Add valid prices to the list

        if not prices:
            logging.warning(f"No valid prices found for XPath: {xpath} on {url}")
            return None  # Return None if no valid prices were found

        # Calculate the average price for this website
        average_price_for_website = sum(prices) / len(prices)
        logging.info(f"Successfully parsed prices from {url}. Average: {average_price_for_website}")
        return average_price_for_website  # Return the average price

    except NoSuchElementException:
        logging.error(f"No elements found with XPath: {xpath} on {url}")
        return None  # Return None if no elements are found
    except TimeoutException:
        logging.error(f"Timeout waiting for page to load: {url}")
        return None  # Return None in case of a timeout
    except Exception as e:
        logging.error(f"An error occurred while parsing {url}: {e}")
        return None  # Return None for any other exceptions
    finally:
        driver.quit()  # Close the browser instance in all cases


def get_average_prices(websites_data, product_name="зюзюблик"):
    """
    Collects the average price of a product from multiple websites.

    Args:
        websites_data (list): A list of dictionaries, each containing 'url' and 'xpath' keys.
        product_name (str): The name of product (not used in current logic but can be used for future enchancement).

    Returns:
        dict: A dictionary where keys are website titles and values are the average prices (or None).
    """
    website_averages = {}  # Store average price for each website

    for website in websites_data:
        average_price = parse_website_price(website['url'], website['xpath'])  # Get average price from each website
        website_averages[website['title']] = average_price  # Store average or None

    return website_averages  # Return only the dictionary of website averages