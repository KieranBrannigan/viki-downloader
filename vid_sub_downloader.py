import sys, os

import requests

from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


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
    chrome_options.add_argument(f"download.default_directory={download_dir}")
    chrome_options.add_experimental_option("prefs", {
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

    driver.get("http://www.lilsubs.com/")

    return driver

def hover(driver, element):
    hover = ActionChains(driver).move_to_element(element).perform()


def enter_link(driver: WebDriver, link: str):
    input_box_id = "link"
    input_box: WebElement = driver.find_element_by_id(input_box_id)
    hover(driver, input_box)
    input_box.send_keys(link)
    
    download_btn_class = "btn-primary"
    download_btn: WebElement = driver.find_element_by_class_name(download_btn_class)
    hover(driver, download_btn)
    download_btn.click()

def get_buttons(driver: WebDriver) -> List[WebElement]:
    return driver.find_elements_by_class_name("btn-primary")


def download_sub(driver: WebDriver, buttons: List[WebElement], lang="chinese"):
    b: WebElement
    btn = None
    for b in buttons:
        if lang.lower() in b.text.lower():
            btn: WebElement = b
            break
    
    if btn != None:
        hover(driver, btn)
        btn.click()

def write_file_from_link(url: str, output_file_name: str):
    resp = requests.get(url)
    with open(os.path.join("output", output_file_name) + ".mp4", 'wb') as Out:
        Out.write(resp.content)
    


def download_video(driver: WebDriver, buttons: List[WebElement], outputFileName: str, quality: str="360p"):
    b: WebElement

    for b in buttons:
        if quality.lower() in b.text.lower():
            btn: WebElement = b

    hover(driver, btn)
    btn.click()
    ### TODO: Wait for doc to load, then download the video using the btn href link.
    #driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.TAB)
    driver.switch_to.window(driver.window_handles[1])

    download_button_xpath = "/html/body/div/center[2]/a"
    download_button: WebElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, download_button_xpath))
        )
    
    
    video_file_link: str = download_button.get_attribute("href")
    ### TODO: switch back to main window
    while len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
    driver.switch_to.window(driver.window_handles[0])
    
    write_file_from_link(video_file_link, outputFileName) 
    


if __name__ == "__main__":
    driver = init_driver()

    with open("downloaded_links.txt", 'r') as ReadFile:
        links = ReadFile.readlines()

    print(links)

    input("Click ENTER when onto the episode 1 page to continue...")

    for link in links:
        current_file: str = link.split("/")[-1].strip()
        enter_link(driver, link)
        driver.implicitly_wait(2)
        buttons: List[WebElement] = get_buttons(driver)
        download_sub(driver, buttons)
        download_video(driver, buttons, current_file)