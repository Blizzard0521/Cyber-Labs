import hashlib
import argparse

parser = argparse.ArgumentParser(description="Crack a password hash using a wordlist.")
parser.add_argument("hash", help="The target hash to crack.")
args = parser.parse_args()

def password_cracker():
    target_hash = args.hash
    target_hash = target_hash.strip().lower()
    algo = ""
    count = 0 

    if len(target_hash) == 32:
        algo = "md5"
    elif len(target_hash) == 40:
        algo = "sha1"
    elif len(target_hash) == 64:
        algo = "sha256"
    else:
        print("Unknown hash type")
        exit()

    #Download the rockyou.txt file from the Internet to try
    with open(r"C:\devPROJECTS\Cyber-Labs\05-python-security-toolkit\password-cracker\rockyou.txt", "r", encoding="latin-1") as f:
    # f is a fle object, it is a stream that allows you to load the instances one by one, instead of loading the entire file into memory at once. This is useful for large files like rockyou.txt, which contains millions of passwords.
    # "r" means read mode, "latin-1" encoding is used to handle special characters in the rockyou.txt file 
    # r"" means raw string, which is used to avoid issues with backslashes in file paths on Windows.
        for line in f:
            word = line.strip()
            count += 1
            attempt = hashlib.new(algo, word.encode()).hexdigest()
            if target_hash == attempt:
                print("Password found: " + word)
                print(f"Number of attempts: {count}")
                break
        else:
            print("Password not found")
            print(f"Number of attempts: {count}")
            

print("Welcome to the Password Cracker!")
password_cracker()