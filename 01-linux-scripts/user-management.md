# user-management.sh notes

### Step 1: Making sure script is run as root or admin

#!/bin/bash: This is called the shebang. It must be the absolute first line. It tells the Linux operating system, "Please use the Bash interpreter located in the /bin/ directory to run the commands in this file." 

#: Anything following a hash mark is a comment. The computer ignores it. It is purely for you to document your code.

The Root Check (if [ "$EUID" -ne 0 ]; then): User management modifies highly secure files like /etc/shadow. Only the root user (the ultimate admin) has permission to do this. The variable $EUID holds the Effective User ID of the person running the script. The root user always has an ID of 0.

The Logic: We are telling the script, "If the ID is Not Equal (-ne) to 0, print an error message and exit immediately with a failure code (exit 1)." This prevents your script from throwing a massive wall of ugly errors if a low-level user tries to run it.

### Step 2: Creating menu function and user creation function
Functions (show_menu(), create_user()): Instead of writing a massive wall of text, we break our code into reusable blocks called functions. It keeps the script clean and modular.

The Check (if id "$username" &>/dev/null; then): We use the native id command to check if the user exists. If you try to run useradd on a user that already exists, the script will throw an ugly error. We redirect that output to /dev/null (the Linux trash can) so it stays hidden from the screen, keeping our tool looking professional.

The Core Command (useradd -m -s /bin/bash "$username"): This is the payload.

-m: Tells Linux to create a home directory (e.g., /home/username).

-s /bin/bash: Explicitly assigns the Bash shell to the user.

🔴 The Red Team Angle: Why Flags Matter
When you compromise a machine and want to maintain access, you create a backdoor account. However, you don't name it hacker or pwned. You name it something boring to blend in with normal system operations, like sys-backup or db-updater.

Defenders (the Blue Team) know that normal "service accounts" meant for background tasks are not supposed to be logged into by humans. Therefore, secure systems often default to creating users without home directories and without usable command shells. If you just type useradd sys-backup, you might accidentally create an account that even you can't log into.

We use specific flags to override those defaults.

🛠️ Breaking Down -m and -s /bin/bash
To ensure our stealthy backdoor actually works, we feed the useradd command two critical arguments:

-m (Make Home Directory): This forces Linux to create a folder for the user (e.g., /home/sys-backup/). As an attacker, you want this directory because it gives you a hidden place to store your tools, or more importantly, a place to drop SSH keys (inside ~/.ssh/authorized_keys). This allows you to log back into the server silently, without ever triggering a password prompt.

-s /bin/bash (Set Shell): This explicitly assigns a fully interactive command line (the Bash shell) to your user. If a system defaults to giving your user a shell like /bin/false or /usr/sbin/nologin, your connection will immediately drop the moment you try to log in or catch a reverse shell. You must demand /bin/bash to get a working prompt.

The while true; do Loop: This creates an infinite loop. It ensures that after you create a user, the script doesn't just abruptly close. It takes you back to the main menu until you explicitly choose option 2 to exit.

### Step 3: Adding Delete, Modify, and Updating the Menu

🔍 Breaking Down the Attacker Mindset
We are using standard IT commands, but the flags we chose are specifically designed for offensive operations.

1. Privilege Escalation (usermod -aG sudo "$username")
Imagine you compromise a low-level web developer's account on a server. You want root access.

We use usermod (User Modify) to change their account properties.

The -G flag assigns them to a group. Here, we assign them to sudo (the administrator group in Debian/Ubuntu-based systems).

🔴 The Red Team Angle (The -a flag): The -a stands for Append. This is absolutely critical. If you just type usermod -G sudo developer, Linux will remove that user from every other group they were in and put them only in the sudo group. That will break their normal access, alert the Blue Team, and get you caught. -a ensures you silently add the admin rights without breaking their existing permissions.

2. Covering Tracks (userdel -r "$username")
When your operation is over, leaving your testhacker or sys-backup user behind is a massive forensic footprint.

We use userdel (User Delete) to remove them from /etc/passwd and /etc/shadow.

🔴 The Red Team Angle (The -r flag): If you run userdel without -r, the user is deleted, but their entire home directory (where you might have dropped hacking tools or SSH keys) is left sitting on the hard drive for forensic investigators to find. The -r flag tells the system to nuke the user's home directory and mail spools simultaneously, wiping your tracks clean.
