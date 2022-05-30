from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class Browser:
    def __init__(self, download_dir):
        self.driver_path = "chrome\chromedriver.exe"
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--headless')
        self.prefs = {
            "download.default_directory" : download_dir,
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        }
        self.options.add_experimental_option("prefs", self.prefs)
        self.options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.options.add_argument("--disable-popup-blocking")
        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=self.options)
        self.driver.maximize_window()
    
    def worker(self):
        return self.driver