import os
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import meshtastic
from meshtastic.serial_interface import SerialInterface
import time
import threading

# Increase the maximum line length to handle larger payloads
imaplib._MAXLINE = 10000

class EmailRelay:
    def __init__(self, gmail_email, gmail_password, com, allowed_senders=None):
        """
        Initialize the email relay with Gmail credentials, allowed senders, and Meshtastic interface.
        """
        self.gmail_email = gmail_email
        self.gmail_password = gmail_password
        self.allowed_senders = allowed_senders or []
        
        # Use SerialInterface with the device
        self.interface = SerialInterface(com)
        
        # Help message with available commands
        self.help_message = (
            "Available Commands:\n"
            "- SENDEMAIL:recipient@example.com:Subject:Body\n"
            "  Send an email to a specific address\n"
            "- GETMAILS\n"
            "  Retrieve recent emails\n"
            "- HELP\n"
            "  Display this help message"
        )
        
        # Initialize email list and index
        self.emails = []
        self.current_email_index = 0
        
        # Setup message handler
        self.setup_message_handler()
        
        # Self-test method
        self.self_test()
    
    def send_email(self, to_email, subject, body):
        """
        Send an email via Gmail SMTP.
        """
        try:
            print(f"Attempting to send email to {to_email} with subject '{subject}' and body '{body}'")
            msg = MIMEMultipart()
            msg['From'] = self.gmail_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                print("Connecting to Gmail SMTP server...")
                server.starttls()
                server.login(self.gmail_email, self.gmail_password)
                print("Sending email...")
                server.send_message(msg)
            
            print(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False
    
    def fetch_recent_emails(self, max_emails=10):
        """
        Fetch recent emails from Gmail inbox.
        """
        try:
            print("Connecting to Gmail IMAP server...")
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.gmail_email, self.gmail_password)
            mail.select('inbox')
            
            print("Fetching email IDs...")
            _, search_data = mail.search(None, 'ALL')
            email_ids = search_data[0].split()
            print(f"Found {len(email_ids)} email IDs.")
            
            email_ids = email_ids[-max_emails:][::-1]  # Reverse to get newest emails first
            
            email_summaries = []
            for email_id in email_ids:
                print(f"Fetching email with ID: {email_id}")
                _, msg_data = mail.fetch(email_id, '(RFC822)')
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                subject = email_message['Subject']
                sender = email.utils.parseaddr(email_message['From'])[1]
                
                # Extract text body
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = email_message.get_payload(decode=True).decode()
                
                email_summaries.append({
                    'email_id': email_id,
                    'sender': sender,
                    'subject': subject,
                    'body': body
                })
                print(f"Fetched email: {email_summaries[-1]}")
            
            mail.close()
            mail.logout()
            print(f"Fetched {len(email_summaries)} emails.")
            return email_summaries
        
        except Exception as e:
            print(f"Failed to fetch emails: {e}")
            return []
    
    def handle_message(self, packet):
        """
        Handle incoming Meshtastic messages for email commands.
        """
        try:
            message = packet.get('payload', {}).get('text', '').strip()
            print(f"Received message: {message}")
            
            if message.startswith('SENDEMAIL:'):
                parts = message.split(':', 3)
                if len(parts) == 4:
                    _, to_email, subject, body = parts
                    success = self.send_email(to_email, subject, body)
                    response = f"Email {'sent successfully' if success else 'failed'}"
                    self.interface.sendText(response)
            
            elif message.startswith('GETMAILS'):
                self.current_email_index = 0
                self.emails = self.fetch_recent_emails(10)
                self.send_email_list()
            
            elif message == 'NEXT':
                self.current_email_index += 5
                self.send_email_list()
            
            elif message == 'CONTINUE':
                self.show_email_detail()
            
            elif message == 'EXIT':
                self.interface.sendText(self.help_message)
            
            elif message.upper() == 'HELP':
                self.interface.sendText(self.help_message)
            
            else:
                response = (
                    "Unrecognized command. Type HELP to see available commands:\n" + 
                    self.help_message
                )
                self.interface.sendText(response)
        except Exception as e:
            print(f"Message handling error: {e}")
    
    def send_email_list(self):
        """
        Send the list of emails to the user.
        """
        print(f"Current email index: {self.current_email_index}")
        if self.current_email_index >= len(self.emails):
            self.interface.sendText("No more emails.")
            return
        
        email_list = ""
        for i, email_summary in enumerate(self.emails[self.current_email_index:self.current_email_index+5]):
            email_list += f"[{self.current_email_index + i + 1}] {email_summary['subject']} | {email_summary['sender']}\n"
        
        email_list += "\n[N]ext Page"
        
        chunks = [email_list[i:i+500] for i in range(0, len(email_list), 500)]
        for chunk in chunks:
            self.interface.sendText(chunk)
            print(f"Sent chunk: {chunk}")
    
    def show_email_detail(self):
        """
        Show the detailed view of a single email.
        """
        if self.current_email_index >= len(self.emails):
            self.interface.sendText("No more emails.")
            return
        
        email_summary = self.emails[self.current_email_index]
        email_detail = f"From: {email_summary['sender']}\nSubject: {email_summary['subject']}\n"
        body = email_summary['body']
        
        if len(body) > 100:
            email_detail += body[:100] + "...\n\n[C]ontinue [N]ext Email"
        else:
            email_detail += body + "\n\n[C]ontinue [N]ext Email"
        
        self.interface.sendText(email_detail)
        print(f"Sent email detail: {email_detail}")
    
    def setup_message_handler(self):
        """
        Set up message handler for Meshtastic interface.
        """
        def on_receive(packet):
            self.handle_message(packet)
        
        self.interface.my_app = on_receive
        print("Message handler setup complete.")
    
    def self_test(self):
        """
        Send a test message to trigger script functionality
        """
        print("Running self-test...")
        time.sleep(2)  # Give time for interface to set up
        
        self.interface.sendText("HELP")
        print("Self-test complete.")
    
    def run(self):
        """
        Keep the script running and listening for messages.
        """
        print("Email Relay is running. Waiting for messages...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping Email Relay...")
        finally:
            self.interface.close()
            print("Email Relay stopped.")

def main():
    GMAIL_EMAIL = 'your-email@gmail.com'
    GMAIL_APP_PASSWORD = 'your-app-password'  # Use App Password, not account password
    ALLOWED_SENDERS = []  # Optional: List of node IDs to whitelist
    COM_PORT = 'COM4'
    
    email_relay = EmailRelay(GMAIL_EMAIL, GMAIL_APP_PASSWORD, COM_PORT, ALLOWED_SENDERS)

    # Start the relay
    email_relay.run()

if __name__ == '__main__':
    main()
