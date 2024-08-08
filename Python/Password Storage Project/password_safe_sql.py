# master_password (what if forgotten?, what if stolen?, how to change? add security questions)
# What happens after password bad 3 times?
# log more stuff
# use a better encryption algorithm
# use a better key management
# use a better password generator
# use a better password strength checker
# add password grouping
# add password expiration and reminders
# add password history
# add password entropy
# add password change option
# UserID 
# Password reading from db!!!!

import pyodbc
import string
import random
import re
import logging
from cryptography.fernet import Fernet, InvalidToken
from getpass import getpass
import bcrypt

# SQL Server connection settings
sql_server = 'DESKTOP-LHUDM3L\POPDBSERVER'
sql_database = 'PasswordManagerDB'
sql_username = 'passmanager'
sql_password = 'passmanager1'

# File containing encryption key
KEY_FILE = "key.txt"
MAX_ATTEMPTS = 3
KEY = None

# logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Create file handler
fh = logging.FileHandler('password_safe_LOG.log')
fh.setLevel(logging.INFO)
# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# Add file handler to logger
logger.addHandler(fh)

def initialize_db_connection():
    global conn
    conn = pyodbc.connect(f'Driver={{SQL Server}};Server={sql_server};Database={sql_database};Uid={sql_username};Pwd={sql_password}')

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

# Modify the logic to set and check the master password
def master_password_check():
    # Check if a master password exists in the database
    cursor = conn.cursor()
    
    cursor.execute("SELECT MasterPasswordHash FROM SecuritySettings WHERE UserID = ?", 1)  # Assuming UserID 1 is for the app's settings
    row = cursor.fetchone()
    
    if row is None:
        # No master password exists in the database, prompt the user to set one
        while True:
            master_password = getpass("Set your master password: ")
            if is_strong_password(master_password):
                # Hash and salt the master password
                master_password_hash, salt = hash_and_salt_password(master_password)
                
                # Store the hashed password in the database
                cursor.execute("INSERT INTO SecuritySettings (UserID, MasterPasswordHash, Salt) VALUES (?, ?, ?)", (1, master_password_hash, salt))
                conn.commit()
                
                print("Master password set successfully.")
                break
            else:
                print("Password is weak. It should be at least 8 characters long and contain at least one digit, one lowercase, one uppercase, and one special character.")
                print("Please change it before saving.\n")
    conn.close()

# Hash the password using the salt
def hash_and_salt_password(password):
    # Generate a random salt
    salt = bcrypt.gensalt()

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    return hashed_password, salt

# Function to get the master password from the SQL database
def get_master_password(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MasterPasswordHash FROM SecuritySettings WHERE UserID = 1")
        row = cursor.fetchone()

        if row:
            return row.MasterPasswordHash
    except Exception as e:
        logging.error(f"Error retrieving master password from the database: {e}")
    return None

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

# Add function. Overwrites passwords.txt file or creates it if it's not existing.
def add_password():
    initialize_db_connection()
    try:
        service = input("Name of service: ")
        if not service:
            print("Service name cannot be empty. Please try again.\n")
            return

        username = input("Username: ")
        if not username:
            print("Username cannot be empty. Please try again.\n")
            return
        
        while True:
            email = input("Email: ")
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                print("Invalid email format. Please try again.\n")
            else:
                break
        # Replace letters between first letter and last letter before '@' with asterisks
        email_parts = email.split('@')
        email_parts[0] = email_parts[0][0] + '*'*(len(email_parts[0])-2) + email_parts[0][-1]
        email = '@'.join(email_parts)

        print("Input password or type '1' to generate one.")
        while True:
            password = getpass("Password: ")
            if is_strong_password(password):
                print("Password is strong!")
                break

            elif password == "1":
                password = generate_password()
                print("Generated Password:", password)
                break

            else:
                print("Password is weak. It should be at least 8 characters long and contain at least one digit, one lowercase, one uppercase, and one special character.")
                print("Please change it before saving.\n")
            
        # Create a database connection and cursor
        cursor = conn.cursor()

        # Define the SQL query with placeholders
        sql_query = "INSERT INTO Passwords (Service, Username, Email, Password, creationdate) VALUES (?, ?, ?, ?, GETDATE())"

        # Pass the user input as parameters
        params = (service, username, email, encrypt_password(password))

        try:
            # Execute the query with parameters
            cursor.execute(sql_query, params)
            conn.commit()
            print("Password saved successfully!")
        except Exception as e:
            logging.error(f"Error writing password to database: {e}")
            print("An error occurred while saving the password. Please try again later.")

        # Close the connection
        conn.close()

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print("An error occurred. Please try again later.")

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
    conn = None  # Initialize the connection
    try:
        conn = pyodbc.connect(f'Driver={{SQL Server}};Server={sql_server};Database={sql_database};Uid={sql_username};Pwd={sql_password}')
        while True:
            entered_password = getpass("Enter your master password: ")
            stored_password = get_master_password(conn)  # Pass the connection to get_master_password

            if stored_password and bcrypt.checkpw(entered_password.encode('utf-8'), stored_password):
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
    finally:
        if conn:
            conn.close()  # Close the connection when you're done

# User input to Menu with add, view, delete, and quit options.
def main():
    initialize_db_connection()
    master_password_check()
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