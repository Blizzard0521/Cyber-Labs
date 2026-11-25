from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa, padding 
import cryptography.hazmat.primitives.hashes as hashes 
from cryptography.hazmat.primitives import serialization
import base64
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
aes_key_path = os.path.join(script_dir, "key.key")
rsa_private_key_path = os.path.join(script_dir, "private_key.pem")

def try_again():
    while True:
        try_again = input("Do you want to encrypt/decrypt another message? (y/n): ").strip().lower()
        if try_again == "y":
            return True
        elif try_again == "n":
            print("Exiting the encryption tool. Thank you for using it!")
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def encrypt_decrypt_message():
    while True:
        mode = input("Choose a mode \n1. Encrypt \n2. Decrypt \n").strip()
        method = input("Choose the encryption method \n1. AES \n2. RSA \n").strip()
        user_message = input("Enter a message to " + ("encrypt" if mode == "1" else "decrypt") + ": ")
        if method == "1":
            need_new_key = True
            if os.path.exists(aes_key_path):
                with open(aes_key_path, "rb") as key_file:
                    key = key_file.read()
                if len(key) > 0:
                    need_new_key = False

            if need_new_key:
                key = Fernet.generate_key()
                with open(aes_key_path, "wb") as key_file:
                    key_file.write(key)

            f = Fernet(key)
            
            if mode == "1":
                encrypted_message = f.encrypt(user_message.encode())
                print(f"Encrypted message: {encrypted_message.decode()}")

            elif mode == "2":
                decrypted_message = f.decrypt(user_message.encode())
                print(f"Decrypted message: {decrypted_message.decode()}")

            else:
                print("Invalid mode selected. Please choose 1 for Encrypt or 2 for Decrypt.")
                if not try_again():
                    break

            if not try_again():
                break

        elif method == "2":
            if os.path.exists(rsa_private_key_path):
                with open(rsa_private_key_path, "rb") as key_file:
                    private_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=None
                    )

            else: 
                private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
                )

                pem = private_key.private_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PrivateFormat.TraditionalOpenSSL,
                            encryption_algorithm=serialization.NoEncryption()
                )

                with open(rsa_private_key_path, "wb") as key_file:
                    key_file.write(pem)


            public_key = private_key.public_key()

            if mode == "1":
                try:
                    ciphertext = public_key.encrypt(
                    user_message.encode(),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                        )
                    )
                    encoded = base64.b64encode(ciphertext).decode()
                    print("Encrypted message:", encoded)

                    if not try_again():
                        break
                    
                except ValueError as e:
                    print("Message too long for RSA encryption:", e)

            elif mode == "2":
                try:
                    ciphertext = base64.b64decode(user_message.encode())
                    plaintext = private_key.decrypt(
                    ciphertext,
                    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(), label=None)
                    )
                    print("Decrypted:", plaintext.decode())

                    if not try_again():
                        break
                except ValueError as e:
                    print("Decryption failed. Please ensure the input is a valid RSA encrypted message:", e)
                    if not try_again():
                        break
        else:
            print("Invalid method selected. Please choose 1 for AES or 2 for RSA.")
            if not try_again():
                break

encrypt_decrypt_message()



