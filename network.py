import socket
import threading

class Server:
    """
    A simple TCP server to manage client connections and broadcast data.
    Now with on_connect and on_disconnect callbacks.
    """
    def __init__(self, host='127.0.0.1', port=65432, on_receive=None, on_connect=None, on_disconnect=None):
        self.host = host
        self.port = port
        self.on_receive = on_receive
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.clients = []
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"Server started on {self.host}:{self.port}")

        self.running = True
        self.accept_thread = threading.Thread(target=self._accept_connections)
        self.accept_thread.daemon = True
        self.accept_thread.start()

    def _accept_connections(self):
        """Accepts new connections in a loop."""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"Accepted connection from {addr}")
                with self.lock:
                    self.clients.append(client_socket)

                if self.on_connect:
                    self.on_connect(client_socket, addr)

                handler_thread = threading.Thread(target=self._handle_client, args=(client_socket,))
                handler_thread.daemon = True
                handler_thread.start()
            except OSError:
                break

    def _handle_client(self, client_socket):
        """Handles messages from a single client."""
        while self.running:
            try:
                header = client_socket.recv(4)
                if not header:
                    break

                msg_len = int.from_bytes(header, 'big')
                data = client_socket.recv(msg_len)

                if data and self.on_receive:
                    self.on_receive(client_socket, data.decode('utf-8'))
            except (ConnectionResetError, BrokenPipeError):
                break

        print(f"Client {client_socket.getpeername()} disconnected.")
        with self.lock:
            if client_socket in self.clients:
                self.clients.remove(client_socket)

        if self.on_disconnect:
            self.on_disconnect(client_socket)

        client_socket.close()

    def _send_message(self, client_socket, message):
        """Encodes and sends a message to a single client socket."""
        try:
            encoded_message = message.encode('utf-8')
            header = len(encoded_message).to_bytes(4, 'big')
            client_socket.sendall(header + encoded_message)
        except (ConnectionResetError, BrokenPipeError):
            # The client might have disconnected. The handler thread will clean it up.
            pass

    def send_to(self, client_socket, message):
        """Public method to send a message to a specific client."""
        self._send_message(client_socket, message)

    def broadcast(self, message, source_socket=None):
        """Broadcasts a message to all clients, optionally excluding the source."""
        with self.lock:
            for client in self.clients:
                if client is not source_socket:
                    self._send_message(client, message)

    def shutdown(self):
        """Shuts down the server."""
        self.running = False
        with self.lock:
            for client in self.clients:
                client.close()
        # This will cause the accept() call to raise an OSError, stopping the accept_thread
        self.server_socket.close()
        print("Server shut down.")


class Client:
    """
    A simple TCP client to connect to the server.
    """
    def __init__(self, host='127.0.0.1', port=65432, on_receive=None):
        self.host = host
        self.port = port
        self.on_receive = on_receive
        self.client_socket = None
        self.running = False
        self.listen_thread = None

    def connect(self):
        """Connects to the server and starts listening for messages."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            self.running = True
            self.listen_thread = threading.Thread(target=self._listen_for_messages)
            self.listen_thread.daemon = True
            self.listen_thread.start()
            return True
        except ConnectionRefusedError:
            print("Connection refused. Is the server running?")
            return False

    def _listen_for_messages(self):
        """Listens for incoming messages from the server."""
        while self.running:
            try:
                header = self.client_socket.recv(4)
                if not header:
                    break

                msg_len = int.from_bytes(header, 'big')
                data = self.client_socket.recv(msg_len)

                if data and self.on_receive:
                    self.on_receive(data.decode('utf-8'))
            except (ConnectionResetError, BrokenPipeError, OSError):
                break

        print("Disconnected from server.")
        self.running = False
        if self.client_socket:
            self.client_socket.close()

    def send(self, message):
        """Sends a message to the server."""
        if self.running and self.client_socket:
            try:
                encoded_message = message.encode('utf-8')
                header = len(encoded_message).to_bytes(4, 'big')
                self.client_socket.sendall(header + encoded_message)
            except (ConnectionResetError, BrokenPipeError):
                print("Failed to send message. Connection lost.")
                self.running = False

    def shutdown(self):
        """Shuts down the client."""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        print("Client shut down.")
