import socket
import threading
import json
import sys
import random
import string
import des
import rsa

chat_host = '127.0.0.1'
chat_port = 55555

pka_host = '127.0.0.1'
pka_port = 55556

nickname = input("Enter your nickname: ")

my_publicKey, my_privateKey = rsa.generate_rsa_keys(bits=2048)
# print("Public Key:", my_publicKey)
# print("Private Key:", my_privateKey)

chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
chat_socket.connect((chat_host, chat_port))

def generate_des_key(length=8):
    if length > 8:
        raise ValueError("Length cannot be more than 8 characters.")
    
    # Generate a random string of the specified length
    random_des = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return random_des

def do_format(secretKey, message, sender, signature):
  full_message = f"{secretKey};{message}|{sender}?{signature}"
  return full_message

def register_with_pka(my_name, my_publicKey):
  # print("entering register with pka")
  pka_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  pka_socket.connect((pka_host, pka_port))
  key = json.dumps(my_publicKey)
  packet = f"REGISTER:{my_name};{key}"
  pka_socket.send(packet.encode('utf-8'))
  response = pka_socket.recv(1024).decode('utf-8')
  pka_socket.close()
  # print("exitting register with pka")
  return response

def get_public_key_from_pka(their_name):
  # print("entering getting public key")
  pka_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  pka_socket.connect((pka_host, pka_port))
  # pka_socket.send("REQUEST".encode('utf-8'))
  # pka_socket.send(their_name.encode('utf-8'))
  packet = f"REQUEST:{their_name}"
  pka_socket.send(packet.encode('utf-8'))
  response = pka_socket.recv(1024).decode('utf-8')
  if response == "nf":
    print(f"User {their_name} not found")
  else:
    response = tuple(json.loads(response))
  pka_socket.close()
  # print("exitting getting public key")
  return response

def receive():
  while True:
    try:
      message_package = chat_socket.recv(4096).decode('utf-8')
      # print(message_package)

      if ":" in message_package:
        msg_type, content1 = message_package.split(":", 1)
        # print(f":----type----- {msg_type}")
        if msg_type == "system":
          print(content1)
        elif msg_type == "user":
          if ";" in content1:
            encrypted_desKey, content2 = content1.split(";",1)
            # print(f":-----endeskey---- {encrypted_desKey}")
            if "|" in content2:
              encrypted_message, content3 = content2.split("|",1)
              sender_name, signature = content3.split("?", 1)
              # print(f":----enmessage----- {encrypted_message}")
              # print(f":----sendername----- {sender_name}")
              # print(f":-----signature----- {signature}")
              try:
                their_publicKey = get_public_key_from_pka(sender_name)
                # print(f'receiving: {sender_name} public key is {their_publicKey}')

                decrypted_desKey = rsa.rsa_decrypt(my_privateKey, encrypted_desKey)
                # print(f":-----decdeskey------ {decrypted_desKey}")

                if rsa.rsa_verify(their_publicKey, decrypted_desKey, signature):
                  print(f"Signature verified successfully.")

                  decrypted_message = des.decrypt_text(encrypted_message, decrypted_desKey)
                  print(f"Decrypted Message from {sender_name}: {decrypted_message}")
                else:
                  print(f"Signature verification failed for {sender_name}'s message.")
                  decrypted_message = des.decrypt_text(encrypted_message, decrypted_desKey)
                  print(f"Decrypted Message from {sender_name}: {decrypted_message}")
              except Exception as e:
                # print(f"Error in decrypting message: {e}")
                print(f"Error in decrypting message: This message is probably not sent to you")
          else:
            print("Malformed message received.")
      else:
        if message_package == 'NICK':
          chat_socket.send(nickname.encode('utf-8'))
        else:
          print(message_package)

    except Exception as e:
      print(f"An error occurred in receive function: {e}")
      break

  chat_socket.close()

def write():
  while True:
    try:
      their_name = input("Who to send?: ").strip()
      if not their_name:
        print("Recipient name cannot be empty.")
        continue
      # print(f"Recipient entered: {their_name}")  # Debugging

      their_publicKey = get_public_key_from_pka(their_name)

      if their_publicKey == "nf":
        continue

      # print(f"Public key retrieved: {their_publicKey}")


      message = input("Enter your message: ").strip()
      if not message:
        print("Message cannot be empty.")
        continue
      # print(f"Message entered: {message}")
      
      des_key = generate_des_key()
      encrypted_message = des.encrypt_text(message, des_key)
      print(f"DES key generated: {des_key}")

      signature = rsa.rsa_sign(my_privateKey, des_key)
      # print(f"-----signsent----- {signature}")
      rsa_desKey = rsa.rsa_encrypt(their_publicKey, des_key)
      # print(f"RSA DES key encrypted: {rsa_desKey}")

      # print(f"Encrypted message: {encrypted_message}")
      package = do_format(rsa_desKey, encrypted_message, nickname, signature)
      chat_socket.send(package.encode('utf-8'))

    except Exception as e:
      print(f"An error occurred in write function: {e}")
      chat_socket.close()
      break

print(register_with_pka(nickname, my_publicKey))

try:
  receive_thread = threading.Thread(target=receive)
  receive_thread.start()

  write_thread = threading.Thread(target=write)
  write_thread.start()

  receive_thread.join()
  write_thread.join()

except KeyboardInterrupt:
  print("\nDisconnecting from the server...")
  chat_socket.close()
  sys.exit(0)
