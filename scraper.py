from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Set up Selenium options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run browser in headless mode (background)
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")

# Initialize Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    # Target URL for Hepsiburada phone category
    url = "https://www.hepsiburada.com/cep-telefonlari-c-371965"
    driver.get(url)

    # Wait for the page to load completely
    WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[class*='productListContent-']"))
    )

    # Scroll the page to load more products
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for new products to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # Exit loop if no more products load
            break
        last_height = new_height

    # Find product elements (using partial class name)
    products = driver.find_elements(By.CSS_SELECTOR, "li[class*='productListContent-']")[:10]
    print(f"Number of products found: {len(products)}")  # Debug: print number of products found

    # List to store product data
    data = []

    # Extract data for each product
    for product in products:
        try:
            # Extract title
            title_elem = product.find_element(By.CSS_SELECTOR, "span[class='title-module_titleText__8FlNQ']")
            title = title_elem.text.strip() if title_elem else "N/A"
        except:
            title = "N/A"

        try:
            # Extract price
            price_elem = product.find_element(By.CSS_SELECTOR, "div[class='price-module_finalPrice__LtjvY']")
            price = price_elem.text.strip() if price_elem else "N/A"
        except:
            price = "N/A"

        try:
            # Extract rating
            rating_elem = product.find_element(By.CSS_SELECTOR, "span[class='rate-module_rating__19oVu']")
            rating = rating_elem.text.strip() if rating_elem else "N/A"
        except:
            rating = "N/A"

        # Append product data to the list
        data.append({"Title": title, "Price": price, "Rating": rating})

    # Save data to CSV file
    if data:
        df = pd.DataFrame(data)
        df.to_csv("products.csv", index=False, encoding="utf-8")
        print("Data saved to products.csv successfully!")
    else:
        print("No data found, CSV not created.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the browser
    driver.quit()