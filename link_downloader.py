### Pass the url of the show as argument
import sys, os

from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

def init_driver(headless: bool = False) -> WebDriver:
    # instantiate a chrome options object so you can set the size and headless preference
    # some of these chrome options might be uncessary but I just used a boilerplate
    # change the <path_to_download_default_directory> to whatever your default download folder is located
    download_dir = "output"
    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)
    chrome_options = Options()
    if headless: chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--verbose')
    chrome_options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False
    })
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    uBlockPath = os.path.join(os.getcwd(), "uBlock")
    chrome_options.add_argument(f"--load-extension={uBlockPath}")
    driver = webdriver.Chrome(options=chrome_options, executable_path="chromedriver.exe")

    driver.get(sys.argv[1]) # 1st argument should be the url to the viki show.

    return driver

def hover(driver, element):
    hover = ActionChains(driver).move_to_element(element).perform()

def click_episodes_tab(driver: WebDriver):
    episode_button_id = "horizontal_tab_episodes"
    ep_tab_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, episode_button_id))
    )
    #ep_tab_element = driver.find_element_by_id(episode_button_id)
    hover(driver, ep_tab_element)
    ep_tab_element.click()

def get_episode_number_tabs(driver) -> List[WebElement]:
    tabs_holder_xpath = "/html/body/div/div[1]/main/div[3]/div/div/div/div[2]/div[1]/div/div"

    driver.implicitly_wait(2)

    holder_div: WebElement = driver.find_element_by_xpath(tabs_holder_xpath)

    ### This is timing out for some reason, despite the div being present.
    # holder_div = WebDriverWait(driver, 10).until(
    #     EC.presence_of_all_elements_located((By.CLASS_NAME, tabs_holder_class_name))
    # )


    return holder_div.find_elements_by_tag_name("span")

def get_episode_links(driver: WebDriver, span: WebElement)-> List[str]:
    hover(driver, span)
    span.click()
    container_xpath = "/html/body/div/div[1]/main/div[3]/div/div/div/div[3]"
    
    driver.implicitly_wait(2)
    ### hopefully this wait is long enough for slower connections.

    container: WebElement = driver.find_element_by_xpath(container_xpath)
    
    
    # container: WebElement = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.CLASS_NAME, container_class_name))
    # )

    a: WebElement
    return [a.get_attribute("href") for a in container.find_elements_by_tag_name("a")]


if __name__ == "__main__":
    driver = init_driver()

    input("Click ENTER when onto the episode 1 page to continue...")
    click_episodes_tab(driver)
    eps_tabs = get_episode_number_tabs(driver)
    span: WebElement
    links = []
    for span in eps_tabs:
        links.extend(get_episode_links(driver, span))

    with open("downloaded_links.txt", 'w') as Write:
        Write.write("\n".join(links))