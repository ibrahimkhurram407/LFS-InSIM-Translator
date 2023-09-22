import socket
import threading
from googletrans import Translator

def translate_to_turkish(message):
    # Translate the message to Turkish
    translator = Translator()
    translated = translator.translate(message, src='auto', dest='tr')
    return "Turkish: " + translated.text

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(1024).decode("utf-8")
            if not data:
                break

            # Check if the message starts with "/t "
            if data.startswith("/t "):
                translated_message = translate_to_turkish(data[3:])
            else:
                # By default, translate to English
                translated_message = "English: " + data

            print("Received: " + data)
            print("Translated: " + translated_message)

            # Send the translated message back to the client
            client_socket.send(translated_message.encode("utf-8"))

    except Exception as e:
        print(f"Error: {str(e)}")

    client_socket.close()

def insim_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)

    print(f"InSim server listening on {host}:{port}")

    try:
        while True:
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr[0]}:{addr[1]}")
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()

    except KeyboardInterrupt:
        print("Server stopped.")

if __name__ == "__main__":
    insim_server("localhost", 29999)
