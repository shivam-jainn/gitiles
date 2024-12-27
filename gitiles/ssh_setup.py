import os
import subprocess
from pathlib import Path  # Import Path from pathlib
from gitiles.profiles import create_profile

def generate_ssh_key(ssh_key_path):
    # Ensure the SSH directory exists
    ssh_dir = Path(ssh_key_path).parent
    if not ssh_dir.exists():
        os.makedirs(ssh_dir)

    # Generate SSH key with no passphrase
    print(f"Generating a new SSH key at {ssh_key_path}...")
    subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "4096", "-f", ssh_key_path, "-N", ""], check=True)

    # Read the public key
    public_key_path = f"{ssh_key_path}.pub"
    if Path(public_key_path).exists():
        with open(public_key_path, "r") as f:
            public_key = f.read().strip()
        print(f"Your SSH public key has been generated. Copy this key to GitHub:\n\n{public_key}\n")
    else:
        raise FileNotFoundError(f"Could not find the public key at {public_key_path}")

# Function to handle the fresh profile creation interactively
def create_fresh_profile():
    # Interactively ask for the profile details
    name = input("Enter the profile name: ")
    email = input("Enter the email address associated with the profile: ")

    # Ask for SSH key path, default to ~/.ssh/{name}_key if not provided
    ssh_key_path = input(f"Enter the SSH key path (default: ~/.ssh/{name}_key): ")
    if not ssh_key_path:  # If the user presses Enter without typing anything
        ssh_key_path = f"~/.ssh/{name}_key"  # Use the default path

    ssh_key_path = os.path.expanduser(ssh_key_path)  # Expand the ~ to the home directory

    # Generate SSH key and show it to the user
    generate_ssh_key(ssh_key_path)

    # Ask for confirmation before creating the profile
    confirmation = input(f"Have you added the above SSH key to your GitHub account? (yes/no): ").strip().lower()

    if confirmation != "yes":
        print("Aborting profile creation. No changes have been made.")
        return

    # After confirmation, create the profile
    create_profile(name, email, ssh_key_path)
    print(f"Profile '{name}' created with email '{email}' and SSH key at '{ssh_key_path}'.")

