from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import yaml
import random

class LinkedInManager:
    def __init__(self):
        self.load_config()
        self.driver = None
        self.setup_driver()
    
    def load_config(self):
        """Load configuration from YAML file"""
        with open('config/config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)
    
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # Uncomment for headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def login(self):
        """Login to LinkedIn"""
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            # Enter email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(self.config['linkedin']['email'])
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.config['linkedin']['password'])
            
            # Click login
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            self.wait.until(
                EC.presence_of_element_located((By.ID, "global-nav"))
            )
            
            logging.info("Successfully logged into LinkedIn")
            return True
            
        except Exception as e:
            logging.error(f"Login failed: {str(e)}")
            return False
    
    def maintain_activity(self):
        """Perform minimal activity to keep profile active"""
        activities = [
            self.view_suggested_profiles,
            self.like_relevant_posts
        ]
        
        # Randomly select one activity to perform
        activity = random.choice(activities)
        activity()
    
    def view_suggested_profiles(self):
        """View suggested profiles to generate activity"""
        try:
            self.driver.get("https://www.linkedin.com/mynetwork/")
            time.sleep(3)
            
            # Click on a few suggested connections
            connect_buttons = self.driver.find_elements(
                By.XPATH, "//button[contains(@class, 'invitation-card')]"
            )[:2]  # Limit to 2 clicks
            
            for button in connect_buttons:
                try:
                    button.click()
                    time.sleep(1)
                except:
                    continue
                    
            logging.info("Completed profile viewing activity")
            
        except Exception as e:
            logging.warning(f"Profile viewing activity failed: {str(e)}")
    
    def like_relevant_posts(self):
        """Like relevant posts in feed"""
        try:
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Find like buttons and click one
            like_buttons = self.driver.find_elements(
                By.XPATH, "//button[contains(@aria-label, 'Like')]"
            )[:1]  # Like only one post
            
            for button in like_buttons:
                try:
                    button.click()
                    time.sleep(1)
                    logging.info("Liked a post in feed")
                except:
                    continue
                    
        except Exception as e:
            logging.warning(f"Liking posts activity failed: {str(e)}")
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()