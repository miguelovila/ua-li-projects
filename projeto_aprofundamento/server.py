#!/usr/bin/python3

# Libraries
import sys
import socket
import base64
import csv
import select

from common_comm import send_dict, recv_dict
from Crypto.Cipher import AES

"""
	This is the server. It receives the client requests, process them and sends the response to the client.
	It accepts secure connections and non-secure connections depending on the client's START request.
	It also receives the client's numbers and saves the maximum, minimum and number of numbers sent in a csv file.
	It accepts the following operations:
		- START: register the client
		- QUIT: unregister the client
		- NUMBER: add a number to the client's list of numbers
		- STOP: unregister the client and send a report to the client

	Usage: python3 server.py port
			port - The port where the server will be listening (1024-65535)

	Example: python3 server.py 1024
"""

# Dictionary of users connected to the server
users = {}


def print_msg(pfx="DBUG", msg="Checkpoint", print_on_console=True):
    # Print the message with coloured prefix
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[96m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    THIN = '\033[0m'
    RESET = '\x1b[0m'
    # Choose the action to perform: print or return
    if print_on_console:
        if pfx == "ERRO":
            print(f"{RED}{BOLD}[{pfx}]{THIN} {msg}{RESET}")
        elif pfx == "INFO":
            print(f"{GREEN}{BOLD}[{pfx}]{THIN} {msg}{RESET}")
        elif pfx == ">>>>":
            print(f"{BLUE}{BOLD}[{pfx}]{THIN} {msg}{RESET}")
        else:
            print(f"{YELLOW}{BOLD}[{pfx}]{THIN} {msg}{RESET}")
    else:
        if pfx == "ERRO":
            return f"{RED}{BOLD}[{pfx}]{THIN} {msg}{RESET}"
        if pfx == "INFO":
            return f"{GREEN}{BOLD}[{pfx}]{THIN} {msg}{RESET}"
        if pfx == ">>>>":
            return f"{BLUE}{BOLD}[{pfx}]{THIN} {msg}{RESET}"
        return f"{YELLOW}{BOLD}[{pfx}]{THIN} {msg}{RESET}"


def find_client_id(client_sock):
    # Return the client id of the client_sock
    for client_id in users:
        if users[client_id]["socket"] == client_sock:
            return client_id
    # If the client is not registered, return False
    return "Unknown"


def encrypt_intvalue(cipherkey, data):
    # Encrypt an integer value with AES, returning a base64 encoded string
    cipher = AES.new(cipherkey, AES.MODE_ECB)
    data = cipher.encrypt(bytes("%16d" % (data), "utf8"))
    return str(base64.b64encode(data), "utf8")


def decrypt_intvalue(cipherkey, data):
    # Decrypt base64 encoded data from server, returning an integer
    cipher = AES.new(cipherkey, AES.MODE_ECB)
    data = cipher.decrypt(base64.b64decode(data))
    return int(data.decode("utf8"))

# Incomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP" }
#
# Outcomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, min, max }


def new_msg(client_sock):
    # Get the message from the client and process it accordingly. Read the client request, detect the operation requested by the client, execute the operation and obtain the response and send it to the client
    rq = recv_dict(client_sock)
    if rq["op"] == "START":
        op = new_client(client_sock, rq)
    elif rq["op"] == "QUIT":
        op = quit_client(client_sock)
    elif rq["op"] == "NUMBER":
        op = number_client(client_sock, rq)
    elif rq["op"] == "STOP":
        op = stop_client(client_sock)
    else:
        # If the operation is not recognized, send the error message to the client
        op = {
            "op": rq["op"],
            "status": False,
            "error": "Invalid operation"
        }
    # Print debug message
    print_msg("DBUG", f"Socket {client_sock} sent {rq} and received {op}")
    # Send the response to the client
    send_dict(client_sock, op)


def new_client(client_sock, request):
    # Check if the client is in a secure connection or not
    if request["cipher"] == None:
        # If the client is not in a secure connection, save the cipher as None
        cipher = None
    else:
        # If the client is in a secure connection, decode the cipher received and save it
        cipher = base64.b64decode(request["cipher"])
    # Check if the client is already registered
    if request["client_id"] not in users:
        # If the client is not registered, register it with default values
        users[request["client_id"]] = {
            "socket": client_sock,
            "cipher": cipher,
            "numbers": []
        }
        # Send the response to the client
        return {
            "op": "START",
            "status": True
        }
    else:
        # If the client is already registered, send the error message to the client
        return {
            "op": "START",
            "status": False,
            "error": "Client already registered"
        }


def clean_client(client_sock):
    # Remove the client from the dictionary
    try:
        del users[find_client_id(client_sock)]
    except:
        pass


def quit_client(client_sock):
    # Check if the client is registered
    if find_client_id(client_sock) in users:
        # Remove the client from the dictionary
        clean_client(client_sock)
        # Send the response to the client
        return {
            "op": "QUIT",
            "status": True
        }
    else:
        # Send the error message to the client
        return {
            "op": "QUIT",
            "status": False,
            "error": "Client not registered"
        }


def create_file():
    # Create the report file with the header
    header = [
        'client_id',
        'numval',
        'minval',
        'maxval'
    ]
    with open('report.csv', 'w') as report:
        writer = csv.writer(report, delimiter=',')
        writer.writerow(i for i in header)


def update_file(client_id):
    # Update the report file with the client id, the number of numbers received and the minimum and maximum values
    data = [
        client_id,
        len(users[client_id]["numbers"]),
        min(users[client_id]["numbers"]),
        max(users[client_id]["numbers"])
    ]
    with open('report.csv', 'a+', newline="") as report:
        writer = csv.writer(report, delimiter=',')
        writer.writerow(i for i in data)


def number_client(client_sock, request):
    # Check if the client is registered
    if find_client_id(client_sock) in users:
        # Check if the value received is a number
        try:
            # Check if the user is in a secure connection
            if users[find_client_id(client_sock)]["cipher"] == None:
                # If the user is not in a secure connection, add the number to the list of numbers
                users[find_client_id(client_sock)]["numbers"].append(int(request["number"]))
            else:
                # If the user is in a secure connection, decrypt the number received and add it to the list of numbers
                users[find_client_id(client_sock)]["numbers"].append(decrypt_intvalue(users[find_client_id(client_sock)]["cipher"], request["number"]))
            # Send the response to the client
            return {
                "op": "NUMBER",
                "status": True
            }
        except:
            # If the value received is not a number, send an error message to the client
            return {
                "op": "NUMBER",
                "status": False,
                "error": "Invalid number"
            }
    else:
        # If the client is not registered, send an error message to the client
        return {
            "op": "NUMBER",
            "status": False,
            "error": "Client not registered"
        }


def stop_client(client_sock):
    # Check if the client is registered
    if find_client_id(client_sock) in users:
        # Check if the client has sent at least one number
        if len(users[find_client_id(client_sock)]["numbers"]) > 0:
            # Save the report locally and send it to the client
            update_file(find_client_id(client_sock))
            # Check if the client is in a secure connection
            if users[find_client_id(client_sock)]["cipher"] == None:
                # Generate decrypted report
                client_data = {
                    "op": "STOP",
                    "status": True,
                    "min": min(users[find_client_id(client_sock)]["numbers"]),
                    "max": max(users[find_client_id(client_sock)]["numbers"])
                }
            else:
                # Generate encrypted report
                client_data = {
                    "op": "STOP",
                    "status": True,
                    "min": encrypt_intvalue(users[find_client_id(client_sock)]["cipher"], min(users[find_client_id(client_sock)]["numbers"])),
                    "max": encrypt_intvalue(users[find_client_id(client_sock)]["cipher"], max(users[find_client_id(client_sock)]["numbers"]))
                }
            # Clean the client from the dictionary
            clean_client(client_sock)
            # Send the report to the client
            return client_data
        else:
            # Clean the client from the dictionary
            clean_client(client_sock)
            # Send error message to the client
            return {
                "op": "STOP",
                "status": False,
                "error": "No numbers received"
            }
    else:
        # Send error message to the client
        return {
            "op": "STOP",
            "status": False,
            "error": "Client not registered"
        }


def validate_args(args):
    # Check if the number of arguments is correct
    if len(args) != 2:
        print_msg("ERRO", f"Usage: python3 {args[0]} port")
        sys.exit(1)
    # Check if the port number is valid
    if not args[1].isdigit():
        print_msg("ERRO", f"Usage: port must be an integer")
        sys.exit(2)
    if int(args[1]) < 1024 or int(args[1]) > 65535:
        print_msg("ERRO", f"Usage: port must be between 1024 and 65535")
        sys.exit(2)


def main():
    # validate the number of arguments and eventually print error message and exit with error and verify the type of of arguments and eventually print error message and exit with error
    validate_args(sys.argv)
    # Get the port of the server
    port = int(sys.argv[1])
    # Create the socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen(10)
    print_msg("INFO", f"Server listening on port {port}")
    clients = []
    # Create the report file with the header
    create_file()
    # Start the server
    while True:
        try:
            available = select.select([server_socket] + clients, [], [])[0]
        except ValueError:
            # Sockets may have been closed, check for that
            for client_sock in clients:
                if client_sock.fileno() == -1:
                    clients.remove(client_sock)  # closed
            continue  # Reiterate select
        for client_sock in available:
            # New client?
            if client_sock is server_socket:
                newclient, addr = server_socket.accept()
                clients.append(newclient)
            # Or an existing client
            else:
                # See if client sent a message
                if len(client_sock.recv(1, socket.MSG_PEEK)) != 0:
                    new_msg(client_sock)
                else:  # Or just disconnected
                    clients.remove(client_sock)
                    clean_client(client_sock)
                    client_sock.close()
                    break  # Reiterate select


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_msg("INFO", f"Server terminated")
        sys.exit(0)
    except Exception as e:
        print_msg("ERRO", f"{e}")
        sys.exit(3)
