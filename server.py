import threading
import socket

host = '127.0.0.1'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
server.settimeout(1)

clients = []
nicknames = []

def broadcast(message, msg_type="user"):
  full_message = f"{msg_type}:{message}"
  for client in clients:
    client.send(full_message.encode('utf-8'))

def handle(client):
  while True:
    try:
      message = client.recv(4096).decode('utf-8')
      print(message)
      broadcast(message, msg_type="user")


    except:
      if client in clients:
          index = clients.index(client)
          clients.remove(client)
          client.close()

          if index < len(nicknames):
              nickname = nicknames[index]
              broadcast(f'{nickname} left the chat', msg_type="system")
              print(f'{nickname} disconnected')
              nicknames.remove(nickname)
      break

def receive():
  try:
    while True:
      try:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('NICK'.encode('utf-8'))
        print("Sent NICK request to client")
        
        nickname = client.recv(4096).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)
        
        print(f'Nickname of the client is {nickname}')
        broadcast(f'{nickname} joined the chat', msg_type="system")
        # client.send('system:Connected to the server'.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.daemon = True
        thread.start()

      except socket.timeout:
          continue
              
  except KeyboardInterrupt:
    print("\nServer is shutting down.")
    for client in clients:
      client.close()
    server.close()
    exit(0)

print("Server is Listening...")
receive()
