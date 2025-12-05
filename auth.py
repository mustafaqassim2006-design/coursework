import bcrypt
import os

USER_DATA_FILE = r"c:/MDX CSSE/Mustafa/My_Work/Data/users.txt"


def hash_password(plain_text_password):
    """Hash a plain text password using bcrypt."""
    password_bytes = plain_text_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_text_password, hashed_password):
    """Verify a plain text password against a stored hash."""
    password_bytes = plain_text_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def user_exists(username):
    """Check if a username already exists in users.txt."""
    if not os.path.exists(USER_DATA_FILE):
        return False

    with open(USER_DATA_FILE, "r") as file:
        for line in file:
            stored_username = line.strip().split(",")[0]
            if stored_username == username:
                return True
    return False


def register_user(username, password):
    """Register a new user and store hashed password in users.txt."""
    if user_exists(username):
        print(f"Error: Username '{username}' already exists.")
        return False

    hashed_pw = hash_password(password)

    with open(USER_DATA_FILE, "a") as file:
        file.write(f"{username},{hashed_pw}\n")

    print(f"Success: User '{username}' registered successfully!")
    return True


def login_user(username, password):
    """Login a user by checking username and password."""
    if not os.path.exists(USER_DATA_FILE):
        print("Error: No users registered yet.")
        return False

    with open(USER_DATA_FILE, "r") as file:
        for line in file:
            stored_username, stored_hash = line.strip().split(",")

            if stored_username == username:
                if verify_password(password, stored_hash):
                    print(f"Success: Welcome, {username}!")
                    return True
                else:
                    print("Error: Invalid password.")
                    return False

    print("Error: Username not found.")
    return False


def validate_username(username):
    """Basic username validation."""
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be 3–20 characters."
    if not username.isalnum():
        return False, "Username must be alphanumeric."
    return True, ""


def validate_password(password):
    """Basic password validation."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    return True, ""

def exisiting_usernames(username):
    """Return a list of existing usernames."""
    usernames = []
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            for line in file:
                stored_username = line.strip().split(",")[0]
                usernames.append(stored_username)
    
    if username in usernames:
        return False, f"{username} already exists."
    else:
        return True, ""

def display_menu():
    """Print the main menu."""
    print("\n" + "=" * 50)
    print("  MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print("  Secure Authentication System")
    print("=" * 50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-" * 50)


def main():
    """Main program loop."""
    print("\nWelcome to the Week 7 Authentication System!")

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == "1":
            # Registration flow
            print("\n--- USER REGISTRATION ---")
            username = input("Enter a username: ").strip()

            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            # Check if username already exists
            exists, error_msg = exisiting_usernames(username)
            if exists is False:
                print(f"Error: {error_msg}")
                continue

            password = input("Enter a password: ").strip()

            # Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if password != password_confirm:
                print("Error: Passwords do not match.")
                continue

            # Register the user
            register_user(username, password)

        elif choice == "2":
            # Login flow
            print("\n--- USER LOGIN ---")
            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            # Attempt login
            if login_user(username, password):
                print("\nYou are now logged in.")
            # Pause before returning to menu
            input("\nPress Enter to return to main menu...")

        elif choice == "3":
            # Exit
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break

        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")


if __name__ == "__main__":
    main()
