#!/usr/bin/python3

# Libraries
from ast import arg
from cgi import test
import os
import sys
import socket
import base64
import re

from common_comm import sendrecv_dict
from Crypto.Cipher import AES

"""
	This is the client. It connects to the server, sends requests and receives responses.
	It can connect to the server using an encrypted connection or not.
	It supports the following operations:
		- START: Connects to the server
		- QUIT: Closes the connection with the server
		- STOP: Stops the connection with the server and prints the min, max and sent values
		- NUMBER: Sends a number to the server

	Usage: python3 client.py client_id port (address)
			client_id - The client id
			port - The port to connect to the server (1024-65535)
			address - The address to connect to the server (default: localhost)

	Example: python3 client.py miguel 1024 maomv.rocks
"""


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


def validate_response(client_sock, response):
    # Verify if response from server is valid or is an error message and act accordingly
    if response['op'] == 'START':
        if response['status'] == True:
            print_msg("INFO", "Connection established")
        else:
            print_msg("ERRO", response['error'])
            client_sock.close()
            sys.exit(3)
    else:
        if response['status'] == False:
            print_msg("ERRO", response['error'])
            client_sock.close()
            sys.exit(3)


def quit_action(client_sock):
    # Send the QUIT operation to the server
    quitRQ = {
        'op': 'QUIT'
    }
    quitOP = sendrecv_dict(client_sock, quitRQ)
    validate_response(client_sock, quitOP)
    client_sock.close()
    sys.exit(4)


def stop_action(client_sock, lst, cipher):
    stopRQ = {
        'op': 'STOP'
    }
    stopOP = sendrecv_dict(client_sock, stopRQ)
    validate_response(client_sock, stopOP)
    # Print the min, max and sent values
    print_msg("INFO", f"Numbers: {lst}")
    print_msg("INFO", f"Minimum: {stopOP['min'] if cipher is None else decrypt_intvalue(cipher,stopOP['min'])}")
    print_msg("INFO", f"Maximum: {stopOP['max'] if cipher is None else decrypt_intvalue(cipher,stopOP['max'])}")


def number_action(client_sock, usrinput, lst, cipher):
    # Verify if the input is a number
    try:
        if cipher is None:
            numberRQ = {
                'op': 'NUMBER',
                'number': int(usrinput)
            }
        else:
            numberRQ = {
                'op': 'NUMBER',
                'number': encrypt_intvalue(cipher, int(usrinput))
            }
        numberOP = sendrecv_dict(client_sock, numberRQ)
        validate_response(client_sock, numberOP)
        lst.append(int(usrinput))
    except ValueError:
        print_msg("ERRO", "Invalid number or command")

# Outcomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "NUMBER", number }
# { op = "STOP" }
#
# Incomming message structure:
# { op = "START", status }
# { op = "QUIT" , status }
# { op = "NUMBER", status }
# { op = "STOP", status, min, max }


def run_client(client_sock, client_id, cipher=None):
    # List with numbers sent to the server
    lst = []
    # Send the START operation to the server
    if cipher is None:
        startRQ = {
            'op': 'START',
            'client_id': client_id,
            'cipher': cipher
        }
    else:
        startRQ = {
            'op': 'START',
            'client_id': client_id,
            'cipher': str(base64.b64encode(cipher), "utf8")
        }
    startOP = sendrecv_dict(client_sock, startRQ)
    validate_response(client_sock, startOP)
    while 1:
        # Ask the user for the operation to be performed
        print_msg("INFO", "Commands available: QUIT, STOP")
        usrinput = input(
            print_msg(">>>>", "Enter command or integer: ", False))
        if usrinput.lower() in ["quit", "q"]:
            # Send the QUIT operation to the server
            quit_action(client_sock)
            break
        elif usrinput.lower() in ["stop", "s"]:
            # Send the STOP operation to the server
            stop_action(client_sock, lst, cipher)
            break
        else:
            # Send the NUMBER operation to the server
            number_action(client_sock, usrinput, lst, cipher)


def validate_args(args):
    # Validate the number of arguments
    if len(args) < 3 or len(args) > 4:
        print_msg("ERRO", f"Usage: python3 {args[0]} client_id port (address)")
        sys.exit(1)
    # Validate type of arguments
    if not(args[2].isdigit()):
        print_msg("ERRO", f"Usage: port must be an integer")
        sys.exit(2)
    if int(args[2]) < 1024 or int(args[2]) > 65535:
        print_msg("ERRO", f"Usage: port must be between 1024 and 65535")
        sys.exit(2)
    # Validate if address is valid
    if len(args) == 4:
        # Tries to connect to the server and verify if it is a valid address or ip
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set timeout to 5 seconds to try to resolve the address and connect
        test_socket.settimeout(5)
        try:
            test_socket.connect((args[3], int(args[2])))
            test_socket.close()
        except:
            # If the address or port is not valid, print error and exit
            test_socket.close()
            print_msg("ERRO", f"Usage: address must be a valid IP or hostname or port")
            sys.exit(2)


def main():
    # Validate the number of arguments and eventually print error message and exit with error. Verify type of of arguments and eventually print error message and exit with error.
    validate_args(sys.argv)
    # Get the hostname of the server
    machine = sys.argv[3] if len(sys.argv) == 4 else "localhost"
    # Get the port of the server
    port = int(sys.argv[2])
    # Get the client_id
    client_id = sys.argv[1]
    # Set cipher key
    cipher = os.urandom(16)
    # Create socket and connect to the server
    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((machine, port))
    except:
        print_msg("ERRO", f"Could not connect to {machine}:{port}")
        sys.exit(1)
    # Ask the user if he wants encryption or not
    if input(print_msg(">>>>", "Do you want to use encryption? [Yes/no] ", False)).lower() in ["yes", "y"]:
        # Run the client with encryption
        run_client(client_sock, client_id, cipher)
    else:
        # Run the client without encryption
        run_client(client_sock, client_id)
    # Close the socket
    client_sock.close()
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_msg("INFO", f"Client terminated by user")
        sys.exit(0)
    except Exception as e:
        print_msg("ERRO", f"{e}")
        sys.exit(5)
