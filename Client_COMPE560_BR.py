import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

#Client settings to connect
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345

#Client class with GUI setup
class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client") #Title on top of GUI

        #Connection variables
        self.client_socket = None
        self.connected = False

        #GUI Layout
        self.chat_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
        self.chat_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        #Message Entry layout and call to receive_message function to recieve incoming messages when connected
        self.message_entry = tk.Entry(root, width=50)
        self.message_entry.grid(row=1, column=0, padx=10, pady=10)
        self.message_entry.bind("<Return>", lambda event: self.send_message())
        #Layout for send button and call to send_message function when called
        self.send_button = tk.Button(root, text="Send", command=self.send_message, width=10)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)
        #Layout for connect button and call to connect_to_server function when called
        self.connect_button = tk.Button(root, text="Connect", command=self.connect_to_server, width=10)
        self.connect_button.grid(row=2, column=0, padx=10, pady=10)
        #Layout for quit button and call to quit_client function when pressed
        self.quit_button = tk.Button(root, text="Quit", command=self.quit_client, width=10)
        self.quit_button.grid(row=2, column=1, padx=10, pady=10)
        
    #Function to connect to server with error handling
    def connect_to_server(self):
        #Make connection if not already connected
        if not self.connected:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((SERVER_IP, SERVER_PORT))
                self.connected = True
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, "[CONNECTED] Connected to the server.\n")
                self.chat_area.config(state='disabled')

                # Start a thread to listen for incoming messages
                threading.Thread(target=self.receive_messages, daemon=True).start()
            #Detect connection error
            except Exception as e:
                messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
        #Also show if already connected
        else:
            messagebox.showinfo("Already Connected", "You are already connected to the server.")
            
    #Function to decode messages for receiving
    def receive_messages(self):
        try:
            while self.connected:
                message = self.client_socket.recv(1024)
                if message:
                    self.chat_area.config(state='normal')
                    self.chat_area.insert(tk.END, f"{message.decode()}\n")
                    self.chat_area.yview(tk.END)
                    self.chat_area.config(state='disabled')
                else:
                    break
        except Exception as e:
            print(f"[ERROR] Receiving messages: {e}")
        finally:
            self.disconnect_from_server()
            
    #Function to send messages and idenify when user wishes to quit
    def send_message(self):
        if self.connected:
            message = self.message_entry.get()
            if message.lower() == "quit":
                self.quit_client()
            elif message:
                try:
                    self.client_socket.send(message.encode())
                    self.message_entry.delete(0, tk.END)
                except Exception as e:
                    messagebox.showerror("Send Error", f"Could not send message: {e}")
        else:
            messagebox.showinfo("Not Connected", "You are not connected to the server.")
    
    #Function to disconnect from the server and send notification of leaving
    def disconnect_from_server(self):
        if self.connected:
            try:
                self.client_socket.send("[DISCONNECTED] Client has left the chat.".encode())
                self.client_socket.close()
            except Exception as e:
                print(f"[ERROR] Disconnecting: {e}")
            finally:
                self.connected = False
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, "[DISCONNECTED] Disconnected from server.\n")
                self.chat_area.config(state='disabled')
                
    #Seperate function to actually quit GUI
    def quit_client(self):
        self.disconnect_from_server()
        self.root.quit()

#Main function to start the GUI
def main():
    root = tk.Tk()
    client_gui = ClientGUI(root)
    root.protocol("WM_DELETE_WINDOW", client_gui.quit_client)
    root.mainloop()

if __name__ == "__main__":
    main()
