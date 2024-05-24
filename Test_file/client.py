# -*- coding: utf-8 -*-
"""
Created on Thu May 23 20:42:25 2024

@author: zyk10
"""

#Use to testing the web server
import socket

def send_request(host, port, path):
    try:
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))

        # Form the HTTP GET request
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        client_socket.sendall(request.encode())

        # Receive the response
        response = client_socket.recv(4096)
        print(response.decode())

        # Close the socket
        client_socket.close()
    except Exception as e:
        print(f"An error happend: {e}")

if __name__ == "__main__":
    host = "localhost"
    port = 8080

    # Trigger a 200 OK response
    print("Triggering 200 OK response:")
    send_request(host, port, "/")

    # Trigger a 403 Forbidden response
    print("Triggering 403 Forbidden response:")
    send_request(host, port, "/../tttt.pdf")

    # Trigger a 404 Not Found response
    print("Triggering 404 Not Found response:")
    send_request(host, port, "/non_existent_file.html")
