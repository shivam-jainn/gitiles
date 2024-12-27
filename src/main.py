import argparse
from profiles import create_profile, list_profiles, delete_profile, switch_profile, init_repo_with_profile
from ssh_setup import create_fresh_profile

def main():
    parser = argparse.ArgumentParser(description="Git Profile Manager CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create profile command
    create_parser = subparsers.add_parser("create", help="Create a new Git profile")
    create_parser.add_argument("name", type=str, nargs="?", help="Name of the profile")
    create_parser.add_argument("email", type=str, nargs="?", help="Email associated with the profile")
    create_parser.add_argument("ssh_key_path", type=str, nargs="?", help="Path to the SSH key")
    create_parser.add_argument("--fresh", action="store_true", help="Generate a new SSH key for the profile interactively")
    
    # List profiles command
    subparsers.add_parser("list", help="List all Git profiles")

    # Delete profile command
    delete_parser = subparsers.add_parser("delete", help="Delete a Git profile")
    delete_parser.add_argument("name", type=str, help="Name of the profile to delete")

    # Switch profile command
    switch_parser = subparsers.add_parser("switch", help="Switch to a Git profile")
    switch_parser.add_argument("name", type=str, help="Name of the profile to switch to")
    switch_parser.add_argument("--local", action="store_true", help="Switch profile locally for the current repo")

    init_parser = subparsers.add_parser("init", help="Initialize a Git repository with a specific profile")
    init_parser.add_argument("repo_path", help="Path to the repository to initialize")
    init_parser.add_argument("profile", help="Profile to use for initializing the repository")

    args = parser.parse_args()

    try:
        if args.command == "create":
            if args.fresh:
                # Call the function to create the profile interactively with a fresh SSH key
                create_fresh_profile()
            else:
                if not args.name or not args.email or not args.ssh_key_path:
                    parser.print_help()
                    return
                # If not fresh, just create the profile with the given details
                create_profile(args.name, args.email, args.ssh_key_path)
        elif args.command == "list":
            list_profiles()
        elif args.command == "delete":
            delete_profile(args.name)
        elif args.command == "switch":
            switch_profile(args.name, local=args.local)
        elif args.command == "init":
            init_repo_with_profile(args.repo_path, args.profile)
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
