import socket
import threading

#Server settings
SERVER_IP = '127.0.0.1'  #Server IP (Client must match this to connect)
SERVER_PORT = 12345
clients = []

#Fucntion that broadcasts a message to all connected clients
def broadcast(message, sender_socket=None):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except Exception as e:
                print(f"Failed to send message to client: {e}")
                clients.remove(client)

#Handle incoming messages from a single client
def handle_client(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    clients.append(client_socket)
    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            print(f"[{client_address}] {message.decode()}")
            broadcast(message, sender_socket=client_socket)
    except Exception as e:
        print(f"[ERROR] {client_address}: {e}")
    finally:
        client_socket.close()
        clients.remove(client_socket)
        print(f"[DISCONNECTED] {client_address} disconnected.")
        broadcast(f"[SERVER] {client_address} has left the chat.".encode())

#Main server setup and loop
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print(f"[SERVER STARTED] Listening on {SERVER_IP}:{SERVER_PORT}")
    #Uses threads to handle multiple clients
    while True:
        client_socket, client_address = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()
