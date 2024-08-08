import pyodbc
import os
import string
import random
import re
import logging
from cryptography.fernet import Fernet, InvalidToken
from getpass import getpass

# File containing encryption key
KEY_FILE = "key.txt"
MAX_ATTEMPTS = 3
KEY = None

# Set up logging
logging.basicConfig(filename='password_safe_LOG.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Create file handler
fh = logging.FileHandler('password_safe.log')
fh.setLevel(logging.INFO)
# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# Add file handler to root logger
logging.getLogger().addHandler(fh)

# Password strength checker
def is_strong_password(pwd):
    logger = logging.getLogger(__name__)

    # Check password strength
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+-=])[A-Za-z\d!@#$%^&*()_+-=]{8,}$"
    if re.match(pattern, pwd):
        return True
    else:
        logger.warning("Password is weak. It should be at least 8 characters long and contain at least one digit, one lowercase, one uppercase, and one special character.")
        return False

# Check if MASTER_PASSWORD environment variable is set
if not os.getenv("master_password"):
    # Prompt user to set MASTER_PASSWORD environment variable
    print("Please set the MASTER_PASSWORD environment variable.")
    while True:
        master_password = getpass("Enter your master password: ")
        if is_strong_password(master_password):
            break
        else:
            print("Password is weak. It should be at least 8 characters long and contain at least one digit, one lowercase, one uppercase, and one special character.")
            print("Please change it before saving.\n")
else:
    master_password = os.getenv("master_password")

# Generate safe password
def generate_password():
    length = 12
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

# Encrypt the password using the generated key
def encrypt_password(password):
    cipher_suite = Fernet(KEY)
    return cipher_suite.encrypt(password.encode()).decode()

# Decrypt the encrypted password using the key
def decrypt_password(encrypted_password):
    logger = logging.getLogger(__name__)
    cipher_suite = Fernet(KEY)
    try:
        return cipher_suite.decrypt(encrypted_password.encode()).decode()
    except InvalidToken:
        logger.warning("Invalid encrypted password.")
        return ""

# Initialize the encryption key
def initialize_key():
    global KEY
    try:
        with open(KEY_FILE, "rb") as key_file:
            KEY = key_file.read()
    except FileNotFoundError:
        KEY = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(KEY)

# Add function. Overwrites passwords.txt file or creates it if it's not existing.
def add_password():
    while True:
        service = input("Name of service: ")
        if not service:
            print("Service name cannot be empty. Please try again.\n")
            continue
        username = input("Username: ")
        if not username:
            print("Username cannot be empty. Please try again.\n")
            continue
        email = input("Email: ")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("Invalid email format. Please try again.\n")
            continue

        print("Input password or type '1' to generate one.")
        password = getpass("Password: ")

        if is_strong_password(password):
            print("Password is strong!")
            break
        elif password == "1":
            password = generate_password()
            break
        else:
            print("Password is weak. It should be at least 8 characters long and contain at least one digit, one lowercase, one uppercase, and one special character.")
            print("Please change it before saving.\n")

    encrypted_password = encrypt_password(password)
    try:
        with open("passwords.txt", "a") as f:
            f.write(f"{service} | {username} | {email} | {encrypted_password}\n")
    except Exception as e:
        logging.error(f"Error writing password to file: {e}")
        print("An error occurred while saving the password. Please try again later.")

# View function. Views contents of passwords.txt file
def view_passwords():
    try:
        with open("passwords.txt", "r") as f:
            for line in f.readlines():
                data = line.strip().split(" | ")
                if len(data) == 4:
                    service, username, email, encrypted_password = data
                    decrypted_password = decrypt_password(encrypted_password)
                    print(f"Service: {service} | Username: {username} | Email: {email} | Password: {decrypted_password}")
                else:
                    continue
    except Exception as e:
        logging.error(f"Error reading passwords from file: {e}")
        print("An error occurred while reading the passwords. Please try again later.")

# Delete function. Deletes credentials for a given service
def delete_credentials():
    while True:
        deleted_service = input("From which service credentials should be deleted? (type service name): ")
        if not deleted_service:
            print("Service name cannot be empty. Please try again.\n")
            continue
        break

    # Read existing passwords from file
    try:
        with open("passwords.txt", "r") as f:
            lines = f.readlines()
    except Exception as e:
        logging.error(f"Error reading passwords from file: {e}")
        print("An error occurred while reading the passwords. Please try again later.")
        return
    
    service_found = any(line.startswith(deleted_service + " | ") for line in lines)

    try:
        if service_found:
            new_lines = [line for line in lines if not line.startswith(deleted_service + " | ")]
            with open("passwords.txt", "w") as f:
                f.writelines(new_lines)
            print(f"Credentials for '{deleted_service}' deleted successfully.\n")
        else:
            print(f"Service name '{deleted_service}' not found. No credentials were deleted.\n")
    except Exception as e:
        logging.error(f"Error writing passwords to file: {e}")
        print("An error occurred while deleting the password. Please try again later.")
        return

# Log into the app with a master password. Incorrect password attempts block access.
def login():
    attempt = 0

    try:
        while True:
            login_attempt = getpass("master Password: ").encode()

            if login_attempt == os.getenv("master_password").encode():
                print("Access granted.\n")
                break
            else:
                attempt += 1
                if attempt >= MAX_ATTEMPTS:
                    print("Access blocked.")
                    break
                else:
                    print(f"Incorrect password. Attempts left: {MAX_ATTEMPTS - attempt}\n")
    except Exception as e:
        logging.error(f"Error comparing passwords: {e}")
        print("An error occurred while logging in. Please try again later.")

# User input to Menu with add, view, delete, and quit options.
def main():
    initialize_key()
    login()
    while True:
        print("1. Add new password")
        print("2. View existing passwords")
        print("3. Delete password")
        print("4. Quit")
        mode = input("Enter the number corresponding to your choice: ")

        if mode == "1":
            add_password()
        elif mode == "2":
            view_passwords()
            print("\n")
        elif mode == "3":
            delete_credentials()
        elif mode == "4":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid input. Please enter a valid option.\n")

if __name__ == "__main__":
    main()    
