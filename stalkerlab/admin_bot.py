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
        self.last_message_id = 0
        self.initialize_seen_messages()
    
    def initialize_seen_messages(self):
        """Initialize with existing messages"""
        try:
            conn = sqlite3.connect('monolith.db')
            c = conn.cursor()
            # Get the highest message ID to track resets
            max_id = c.execute('SELECT MAX(id) FROM messages').fetchone()[0]
            self.last_message_id = max_id if max_id else 0
            
            # Only store recent message IDs
            messages = c.execute('SELECT id FROM messages ORDER BY id DESC LIMIT 100').fetchall()
            self.seen_message_ids = set(msg[0] for msg in messages)
            conn.close()
        except Exception as e:
            print(f"[!] Error initializing message tracker: {e}")
    
    def check_for_chat_reset(self):
        """Check if chat has been cleared by comparing message counts"""
        try:
            conn = sqlite3.connect('monolith.db')
            c = conn.cursor()
            
            # Get current highest message ID
            current_max_id = c.execute('SELECT MAX(id) FROM messages').fetchone()[0]
            current_max_id = current_max_id if current_max_id else 0
            
            # If current max ID is less than what we've seen, chat was cleared
            if current_max_id < self.last_message_id:
                print("[*] Chat reset detected! Reinitializing message tracker...")
                self.seen_message_ids.clear()
                self.initialize_seen_messages()
                
            conn.close()
            return current_max_id < self.last_message_id
        except Exception as e:
            print(f"[!] Error checking for chat reset: {e}")
            return False
    
    def has_new_messages(self):
        """Check for new messages by comparing with seen IDs"""
        try:
            # First check if chat was cleared
            if self.check_for_chat_reset():
                return True
                
            conn = sqlite3.connect('monolith.db')
            c = conn.cursor()
            
            # Only check recent messages
            current_messages = c.execute('SELECT id FROM messages ORDER BY id DESC LIMIT 100').fetchall()
            current_ids = set(msg[0] for msg in current_messages)
            
            # Update last seen message ID
            if current_messages:
                self.last_message_id = max(current_ids)
            
            # Cleanup old message IDs (keep only recent ones)
            self.seen_message_ids = set(id for id in self.seen_message_ids 
                                      if id > self.last_message_id - 100)
            
            # Check for new messages
            new_messages = current_ids - self.seen_message_ids
            if new_messages:
                self.seen_message_ids.update(current_ids)
                return True
            return False
            
        except Exception as e:
            print(f"[!] Error checking messages: {e}")
            return False
        finally:
            conn.close()

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=chrome_options)

def admin_bot():
    print("[*] Starting admin bot with headless Chrome...")
    driver = None
    tracker = MessageTracker()
    
    try:
        driver = setup_driver()
        
        print("[*] Performing initial login...")
        driver.get("http://localhost:5000/monolith")
        username = driver.find_element(By.NAME, "username")
        password = driver.find_element(By.NAME, "password")
        submit = driver.find_element(By.TAG_NAME, "button")
        
        username.send_keys("monolith_master")
        password.send_keys("super_secret_monolith_pw")
        submit.click()
        print("[*] Initial login successful")
        
        consecutive_errors = 0
        while True:
            try:
                if tracker.has_new_messages():
                    print("[*] New messages detected!")
                    
                    # Visit mentor panel
                    print("[*] Visiting mentor panel...")
                    driver.get("http://localhost:5000/monolith/mentor-panel")
                    
                    # Wait for messages to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "chat"))
                    )
                    
                    # Stay on the page briefly to let XSS execute
                    time.sleep(2)
                    print("[*] Messages checked")
                    consecutive_errors = 0
                
                # Adaptive sleep: increase delay if no activity
                time.sleep(5)
                
            except Exception as e:
                print(f"[!] Error in admin bot: {e}")
                consecutive_errors += 1
                
                if consecutive_errors >= 3:
                    print("[!] Too many consecutive errors, restarting browser...")
                    if driver:
                        driver.quit()
                    driver = setup_driver()
                    consecutive_errors = 0
                    
                    # Re-login after browser restart
                    try:
                        driver.get("http://localhost:5000/monolith")
                        username = driver.find_element(By.NAME, "username")
                        password = driver.find_element(By.NAME, "password")
                        submit = driver.find_element(By.TAG_NAME, "button")
                        
                        username.send_keys("monolith_master")
                        password.send_keys("super_secret_monolith_pw")
                        submit.click()
                        print("[*] Re-login successful")
                    except:
                        print("[!] Re-login failed, will retry...")
                        time.sleep(5)
                
    except KeyboardInterrupt:
        print("\n[*] Shutting down admin bot...")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    admin_bot() 