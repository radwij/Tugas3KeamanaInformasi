import socket
import threading
import json

host = '127.0.0.1'
port = 55556

public_keys = {}

def handle_client(client_socket):
    try:
      package = client_socket.recv(1024).decode('utf-8')
      print(package)

      if ":" in package:
        operation, content = package.split(":", 1)
        if operation == "REGISTER":
          print("entering register")
          if ";" in content:
            client_name, public_key = content.split(";",1)
            unserialised_public_key = tuple(json.loads(public_key))
            print(client_name)
            print(unserialised_public_key)
            public_keys[client_name] = unserialised_public_key
            client_socket.send("REGISTERED".encode())
            print("key saved successfully")
          else:
            client_socket.send("Error in parsing content".encode())
            print("Error in parsing content")

        elif operation == "REQUEST":
          print("entering request")
          if content in public_keys:
            print(public_keys[content])
            client_socket.send(json.dumps(public_keys[content]).encode('utf-8'))
          else:
            client_socket.send("nf". encode('utf-8'))
            print(f"User {content} not found")
      else:
        print("Error in parsing package")

    except:
        print("Error handling client")
      

def pka_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    server_socket.settimeout(1)
    print("PKA is running on port 55556.")

    try:
        while True:
            try:
                client_socket, _ = server_socket.accept()
                threading.Thread(target=handle_client, args=(client_socket,)).start()
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
        server_socket.close()
        print("Server closed.")
        exit(0)
        
pka_server()