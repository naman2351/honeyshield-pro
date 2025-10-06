from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from datetime import datetime
from .database import DatabaseManager

class MessageMonitor:
    def __init__(self, linkedin_manager):
        self.linkedin_manager = linkedin_manager
        self.driver = linkedin_manager.driver
        self.wait = linkedin_manager.wait
        self.db = DatabaseManager()
    
    def scrape_messages(self):
        """Scrape new messages from LinkedIn"""
        try:
            # Navigate to messages
            self.driver.get("https://www.linkedin.com/messaging/")
            time.sleep(5)
            
            # Get conversation list
            conversations = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'msg-conversation-listitem')]"
            )
            
            new_messages = []
            
            for conversation in conversations[:10]:  # Check first 10 conversations
                try:
                    # Click on conversation
                    conversation.click()
                    time.sleep(2)
                    
                    # Extract message data using JavaScript execution
                    message_data = self.driver.execute_script('''
                        const messages = document.querySelectorAll('.msg-s-event-listitem');
                        const lastMessage = messages[messages.length - 1];
                        
                        if (!lastMessage) return null;
                        
                        // Get sender info
                        const senderElement = lastMessage.querySelector('.msg-s-message-group__profile-link');
                        const senderName = senderElement ? senderElement.innerText.trim() : 'Unknown';
                        const senderUrl = senderElement ? senderElement.href : '';
                        
                        // Get message content
                        const contentElement = lastMessage.querySelector('.msg-s-event-listitem__body');
                        const messageContent = contentElement ? contentElement.innerText.trim() : '';
                        
                        // Check if message is new (from others)
                        const isFromMe = lastMessage.querySelector('.msg-s-message-group--by-current-user');
                        
                        return {
                            senderName: senderName,
                            senderUrl: senderUrl,
                            messageContent: messageContent,
                            isFromMe: !!isFromMe,
                            timestamp: new Date().toISOString()
                        };
                    ''')
                    
                    if (message_data and not message_data['isFromMe'] and 
                        message_data['messageContent'] and 
                        self.is_new_message(message_data)):
                        
                        new_messages.append(message_data)
                        logging.info(f"Found new message from {message_data['senderName']}")
                        
                except Exception as e:
                    logging.warning(f"Error processing conversation: {str(e)}")
                    continue
            
            return new_messages
            
        except Exception as e:
            logging.error(f"Error scraping messages: {str(e)}")
            return []
    
    def is_new_message(self, message_data):
        """Check if message is new (basic implementation)"""
        # In a real implementation, you'd check against your database
        # For MVP, we'll assume all found messages are new
        return True