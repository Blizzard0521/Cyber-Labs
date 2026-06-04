#!/bin/bash

#Check if the script is being run as root
if ["$EUD" -ne 0 ]; then 
echo "Error: THis script must be run as root."
exit 1
fi 

echo "Root privileges confirmed.Starting user management..."

# --- Main Menu Function ---

show_menu() {
	echo "==================="
	echo " User Management Toolkit "
	echo "==================="
	echo "1. Create a new user"
	echo "2. Elevate a user to Admin (PrivEsc)"
	echo "3. Delete a user (Cover Tracks)"
	echo "4. Exit"
	echo "==================="
	read -p "Select an option (1-4): " choice
}

# --- Create User Function ---

create_user() {
	read -p "Enter the username you want to create: " username

	# Check if the user already exists in the system
	if id "$username" &>/dev/null; then
		echo "[-] Error: The user '$username' already exists."
	else
		echo "[+] Attempting to create user '$username'..."
		# Create the user with a home directory and bash shell
		useradd -m -s /bin/bash "$username"

		#Prompt to set a password for the new user
		passwd "$username"
		echo "[+] User '$username' created successfully!"
	fi
}

# --- Modify User FUnction (PrivEsc Focus) ---

modify_user() {
	read -p "ENter the username to elvate to admin (sudo): " username
	
	if id "$username" &>/dev/null; then 
		echo "[+] Adding user '$username' to the sudo group..."
		# -aG appends the user to the supplementary group 'sudo'
		usermod -aG sudo "$username"
		echo "[+] Success! '$username' can now run commands as root."
	else
		echo "[-] Error: User '$username' does not exist."
	fi
}

# --- Delete User Function (Covering Track Focus) ---

delete_user() {
	read -p "Enter the username to delete: " username

	if id "$username" &>/dev/null; then 
		echo "[+] Attempting to delete user '$username' and their files ..."
		# -r removes the home directory and mail spool
		userdel -r "$username"
		echo "[+] User '$username' and their home directory wiped successfully!"
	else
		echo "[-] Error: User '$username' does not exist."
	fi
}



# --- Execution Loop ---
while true; do 
        show_menu
        case $choice in
                1) create_user ;;
                2) modify_user ;;
                3) delete_user ;; 
                4) echo "Exiting ..."; exit 0;;
                *) echo "[-] Invalid option. Please try again." ;;
        esac
        echo "" #Print a blank line for readability
done
		
