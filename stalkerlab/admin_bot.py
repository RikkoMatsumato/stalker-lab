from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sqlite3
import json
import os

class MessageTracker:
    def __init__(self):
        self.seen_message_ids = set()
        self.initialize_seen_messages()
    
    def initialize_seen_messages(self):
        """Initialize with existing messages"""
        try:
            conn = sqlite3.connect('monolith.db')
            c = conn.cursor()
            messages = c.execute('SELECT id FROM messages').fetchall()
            self.seen_message_ids = set(msg[0] for msg in messages)
            conn.close()
        except Exception as e:
            print(f"[!] Error initializing message tracker: {e}")
    
    def has_new_messages(self):
        """Check for new messages by comparing with seen IDs"""
        try:
            conn = sqlite3.connect('monolith.db')
            c = conn.cursor()
            current_messages = c.execute('SELECT id FROM messages').fetchall()
            current_ids = set(msg[0] for msg in current_messages)
            conn.close()
            
            # Check if there are any messages we haven't seen
            new_messages = current_ids - self.seen_message_ids
            if new_messages:
                self.seen_message_ids = current_ids
                return True
            return False
            
        except Exception as e:
            print(f"[!] Error checking messages: {e}")
            return False

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

def admin_bot():
    print("[*] Starting admin bot with headless Chrome...")
    driver = setup_driver()
    tracker = MessageTracker()
    
    # Initial login
    try:
        print("[*] Performing initial login...")
        driver.get("http://127.0.0.1:5000/monolith")
        username = driver.find_element(By.NAME, "username")
        password = driver.find_element(By.NAME, "password")
        submit = driver.find_element(By.TAG_NAME, "button")
        
        username.send_keys("monolith_master")
        password.send_keys("super_secret_monolith_pw")
        submit.click()
        print("[*] Initial login successful")
    except Exception as e:
        print(f"[!] Error during initial login: {e}")
        driver.quit()
        return
    
    while True:
        try:
            # Check for new messages more frequently
            if tracker.has_new_messages():
                print("[*] New messages detected!")
                
                # Visit mentor panel
                print("[*] Visiting mentor panel...")
                driver.get("http://127.0.0.1:5000/monolith/mentor-panel")
                
                # Wait for messages to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "chat"))
                )
                
                # Stay on the page briefly to let XSS execute
                time.sleep(2)
                print("[*] Messages checked")
            
            # Short sleep between checks
            time.sleep(5)
            
        except Exception as e:
            print(f"[!] Error in admin bot: {e}")
            try:
                # Attempt to re-login and continue
                print("[*] Attempting to re-login...")
                driver.quit()
                driver = setup_driver()
                driver.get("http://127.0.0.1:5000/monolith")
                
                username = driver.find_element(By.NAME, "username")
                password = driver.find_element(By.NAME, "password")
                submit = driver.find_element(By.TAG_NAME, "button")
                
                username.send_keys("monolith_master")
                password.send_keys("super_secret_monolith_pw")
                submit.click()
                print("[*] Re-login successful")
            except:
                print("[!] Re-login failed, waiting before retry...")
                time.sleep(5)

if __name__ == "__main__":
    admin_bot() 