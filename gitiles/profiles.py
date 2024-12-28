import os
import json
import subprocess
from pathlib import Path

CONFIG_FILE = Path.home() / ".git_profile_manager.json"


def ensure_config_exists():
    if not CONFIG_FILE.exists() or CONFIG_FILE.stat().st_size == 0:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"profiles": {}, "repositories": {}}, f)


def read_config():
    ensure_config_exists()
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error reading JSON file: {e}")
        return {"profiles": {}, "repositories": {}}
    except FileNotFoundError:
        print("Config file not found, creating a new one.")
        ensure_config_exists()
        return {"profiles": {}, "repositories": {}}


def write_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


# Create a new profile
def create_profile(name, email, ssh_key_path):
    config = read_config()

    if name in config['profiles']:
        raise ValueError(f"Profile '{name}' already exists.")

    if not Path(ssh_key_path).exists():
        raise FileNotFoundError(f"SSH key '{ssh_key_path}' does not exist.")

    config['profiles'][name] = {
        "email": email,
        "ssh_key_path": ssh_key_path
    }

    write_config(config)
    print(f"Profile '{name}' created successfully.")


# List all profiles and display global/local selection
def list_profiles():
    config = read_config()

    if not config['profiles']:
        print("No profiles found.")
        return

    # Check if we are in a Git repository
    current_git_profile = None
    try:
        # Get the current Git user.name and user.email (i.e., the selected profile)
        git_user_name = subprocess.check_output(["git", "config", "--get", "user.name"]).strip().decode()
        git_user_email = subprocess.check_output(["git", "config", "--get", "user.email"]).strip().decode()
        current_git_profile = (git_user_name, git_user_email)
    except subprocess.CalledProcessError:
        # If Git isn't configured or we're not in a Git repository, ignore
        current_git_profile = None

    # Print all profiles and check for global/local selection
    for profile_name, details in config['profiles'].items():
        # Checking the repository for a local profile
        local_profile = None
        repo_path = Path.cwd()  # Current directory

        if repo_path in config.get("repositories", {}):
            local_profile_name = config["repositories"][str(repo_path)]
            if local_profile_name == profile_name:
                local_profile = profile_name

        # Determine the global vs local status
        is_global = (current_git_profile and current_git_profile[0] == profile_name and current_git_profile[1] == details['email'])
        is_local = local_profile == profile_name

        print(f"Profile: {profile_name}")
        print(f"  Email: {details['email']}")
        print(f"  SSH Key: {details['ssh_key_path']}")

        # Display selection status
        if is_local:
            print("  (Local - Selected in this repository)".green())  # Green for local selection
        elif is_global:
            print("  (Global - Selected globally)")

        print()  # New line between profiles


# Delete a profile
def delete_profile(profile_name):
    config = read_config()

    if profile_name not in config['profiles']:
        raise ValueError(f"Profile '{profile_name}' does not exist.")

    del config['profiles'][profile_name]
    write_config(config)
    print(f"Profile '{profile_name}' deleted successfully.")

def switch_profile(profile_name, local=False):
    config = read_config()

    if profile_name not in config['profiles']:
        raise ValueError(f"Profile '{profile_name}' does not exist.")

    profile = config['profiles'][profile_name]
    ssh_key_path = profile["ssh_key_path"]

    # Clear existing SSH keys and add the new one
    subprocess.run(["ssh-add", "-D"], check=True)  # Remove all existing keys
    subprocess.run(["ssh-add", ssh_key_path], check=True)  # Add the profile-specific key

    if local:
        try:
            # Check if we are inside a Git repository
            repo_path = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).strip().decode()

            # Update the Git configuration for this repository locally
            subprocess.run(["git", "config", "user.name", profile_name], cwd=repo_path, check=True)
            subprocess.run(["git", "config", "user.email", profile["email"]], cwd=repo_path, check=True)

            print(f"Switched to profile '{profile_name}' locally in repository '{repo_path}'.")

        except subprocess.CalledProcessError:
            raise ValueError("Not inside a Git repository. Cannot apply local profile changes.")

    else:
        # If we're not switching locally, update globally (default behavior)
        subprocess.run(["git", "config", "--global", "user.name", profile_name], check=True)
        subprocess.run(["git", "config", "--global", "user.email", profile["email"]], check=True)

        print(f"Switched to profile '{profile_name}' globally.")

    update_shell_prompt(profile_name)

def update_shell_prompt(profile_name):
    """Update the shell prompt to include the active profile."""
    profile_indicator = f"({profile_name}) "
    shell_prompt = os.environ.get("PS1", "")
    
    if not shell_prompt.startswith(profile_indicator):
        os.environ["PS1"] = profile_indicator + shell_prompt
        print(f"Shell prompt updated to include profile: {profile_indicator.strip()}")


# Initialize a Git repository with a specific profile
def init_repo_with_profile(repo_path, profile_name):
    config = read_config()

    if profile_name not in config['profiles']:
        raise ValueError(f"Profile '{profile_name}' does not exist.")
    
    profile = config['profiles'][profile_name]
    repo_path = str(Path(repo_path).resolve())  # Ensure absolute path

    if not Path(repo_path).exists():
        raise FileNotFoundError(f"The path '{repo_path}' does not exist.")
    
    # Initialize the repository
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    
    subprocess.run(["git", "config", "user.name", profile_name], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.email", profile["email"]], cwd=repo_path, check=True)
    
    repo_config = read_config().get("repositories", {})
    repo_config[repo_path] = profile_name

    config["repositories"] = repo_config
    write_config(config)

    print(f"Repository at '{repo_path}' initialized with profile '{profile_name}'.")

