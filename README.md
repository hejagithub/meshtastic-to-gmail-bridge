# Meshtastic Email Relay

Meshtastic Email Relay is a Python script that enables you to send and receive emails via the Meshtastic network. The script uses Gmail credentials to interact with the Gmail API and a Meshtastic Serial Interface to communicate with Meshtastic nodes.

## Features

- **Send Emails**: Send emails to specific addresses directly from your Meshtastic node.
- **Retrieve Emails**: Fetch and display recent emails with pagination.
- **Email Details**: Show detailed views of individual emails.
- **Available Commands**:
  - `SENDEMAIL:recipient@example.com:Subject:Body` - Send an email to the specified recipient with the given subject and body.
  - `GETMAILS` - Retrieve recent emails.
  - `HELP` - Display the available commands.
  - `NEXT` - Go to the next set of emails in the list.
  - `CONTINUE` - Continue reading a long email.
  - `EXIT` - Exit to the main menu.

## Installation

1. **Clone the Repository**: Clone this repository to your local machine:
   ```sh
   git clone https://github.com/hejagithub/meshtastic-email-relay.git
   ```

2. **Install Required Packages**: Navigate to the project directory and install the required Python packages using `pip`:
   ```sh
   cd meshtastic-email-relay
   pip install -r requirements.txt
   ```

## Setup

1. **Generate an App Password**: 
   - Ensure you have 2-Step Verification enabled on your Google account.
   - Generate an App Password for your Gmail account. Follow the instructions [here](https://support.google.com/accounts/answer/185833?hl=en) to create an App Password.

2. **Update the Script**: Open the `email_relay.py` script and update the following placeholders with your actual credentials:
   
   - `GMAIL_EMAIL`: Replace with your Gmail email address.
   - `GMAIL_APP_PASSWORD`: Replace with your App Password.
    ​
   ```python
   GMAIL_EMAIL = 'your-email@gmail.com'
   GMAIL_APP_PASSWORD = 'your-app-password'
   ALLOWED_SENDERS = []  # Optional: List of node IDs to whitelist
   ```

## Usage

1. **Run the Script**: Execute the script using Python:
   ```sh
   python email_relay.py
   ```

2. **Interact with the Script**: Use the following commands to interact with the script via your Meshtastic node:
   - `SENDEMAIL:recipient@example.com:Subject:Body`: Send an email to the specified recipient.
   - `GETMAILS`: Retrieve recent emails.
   - `HELP`: Display the available commands.
   - `NEXT`: Go to the next set of emails.
   - `CONTINUE`: Continue reading a long email.
   - `EXIT`: Exit to the main menu.

## Example Commands

- **Send an Email**:
  ```
  SENDEMAIL:example@domain.com:Test Subject:This is a test email body
  ```

- **Retrieve Emails**:
  ```
  GETMAILS
  ```

- **Get Help**:
  ```
  HELP
  ```

## Notes

- The script assumes you have a Meshtastic device connected to your computer via a serial interface (e.g., COM4).
- Ensure that your Meshtastic device is configured correctly and connected before running the script.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork this repository, make your changes, and submit a pull request.

---

**Replace the following placeholders with your actual information:**

- `your-email@gmail.com`: Replace with your Gmail email address.
- `your-app-password`: Replace with your App Password.

---

By following the steps outlined in this README, you should be able to set up and run the Meshtastic Email Relay script with ease. Happy emailing! This README and python script were made by AI
```
