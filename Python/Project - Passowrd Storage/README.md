# Password Manager Setup (.txt version usable for anyone, sql version is unusable (due to no sql server) and uploaded only to showcase code)

## Description

This is a simple command-line password manager written in Python. It allows you to store and manage passwords for various services. The passwords are stored in an encrypted form using the Fernet encryption scheme.

## Functionality

1. Add New Password: Add new service credentials including the service name, username, and email. You can generate a strong password if needed.
2. View Existing Passwords: View all stored passwords along with their service names, usernames, and emails. Passwords are decrypted on the fly for viewing.
3. Delete Password: Delete stored credentials for a specific service.
4. Master Password: Access to the application requires the correct master password.
5. Password Strength Checking: Ensures that passwords meet certain complexity criteria.
   
## Setup Instructions

1. **Clone the Repository**: Clone this repository to your local machine.
```bash
git clone https://https://github.com/DBvagabond/Python-Projects/edit/main/README.md
```
2. Install Required Libraries: Navigate to the repository directory and install the required libraries.
```bash
pip install cryptography
```
3. Set Up Environment Variable: Set the environment variable "MASTER_PASSWORD" to your master password. This password is used to access the password manager.
```bash
setx MASTER_PASSWORD "YourMasterPassword123"
```
4. Run the Application: Open a command prompt or terminal, navigate to the repository directory, and run the Python script.
```bash
python password_safe.py
```
## Usage
1. Upon running the script, enter your master password.
2. Choose options from the menu by entering the corresponding number.
3. Follow the prompts to add, view, or delete passwords.

## Acknowledgements
- This project utilizes the **Cryptography library** for password encryption.
- Inspiration from **Tech With Tim** [*5 Mini Python Projects - For Beginners*](https://www.youtube.com/watch?v=DLn3jOsNRVE&t=5300s&ab_channel=TechWithTim) video.
