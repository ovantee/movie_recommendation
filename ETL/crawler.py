from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    # Open the target URL
    driver.get('https://www.imdb.com/title/tt4154796/')  # URL for 'Avengers: Endgame'

    # Wait for the page to load completely
    driver.implicitly_wait(10)

    # Fetch the image link
    image_element = driver.find_element(By.CSS_SELECTOR, '.ipc-media .ipc-image')
    image_link = image_element.get_attribute('src')

    # Fetch director links
    directors = driver.find_elements(By.XPATH, '//a[contains(@href, "/name") and contains(text(), "Russo")]')
    director_links = [director.get_attribute('href') for director in directors]

    # Fetch star links
    stars = driver.find_elements(By.XPATH, '//a[contains(@href, "/name") and (@aria-disabled="false")]')
    star_links = [star.get_attribute('href') for star in stars if 'nm' in star.get_attribute('href')][:3]  # Top 3 stars

    print("Image Link:", image_link)
    print("Director Links:", director_links)
    print("Star Links:", star_links)

finally:
    # Close the browser
    driver.quit()
