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
	This file acts as a client for the server. It is used to test the server.
	This client can be used to test the server in different scenarios depending on the arguments passed:
		- Start the server and test the connection
		- Set encryption and test the connection
		- Send a number to the server and test if it is valid
		- Send a invalid number to the server and test its response
		- Send not expected operations to the server and test its response
	Because this is a testing file, all data validation is done in the server.

	Usage: python3 server_prober.py id port encryption address worker_order
			id - The client id
			port - The port to connect to the server (1024-65535)
			encryption - The encryption option (y/n)
			address - The address of the server (ipv4 or domain)
			worker_order - The worker order as a list of actions

	Example: python3 server_prober.py miguel 1024 y localhost START,-10,10,STOP,QUIT,INVALIDOP
"""


def print_msg(pfx="DBUG", msg="Checkpoint", print_on_console=True):
    # Choose the action to perform: print or return
    if print_on_console:
        print(f"[{pfx}]{msg}")
    else:
        return f"[{pfx}]{msg}"


def encrypt_intvalue(cipherkey, data):
    # Encrypt an integer value with AES, returning a base64 encoded string
    cipher = AES.new(cipherkey, AES.MODE_ECB)
    # #16s instead of &16d just to be able to send caracters for testing purposes
    data = cipher.encrypt(bytes("%16s" % (data), "utf8"))
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


def start_action(client_sock, client_id, cipher):
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


def quit_action(client_sock):
    # Send the QUIT operation to the server
    quitRQ = {
        'op': 'QUIT'
    }
    quitOP = sendrecv_dict(client_sock, quitRQ)
    validate_response(client_sock, quitOP)
    print_msg("INFO", f"Client terminated")
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
    # Send the number to the server. As this is a testing client, the number is sent without any validation
    if cipher is None:
        numberRQ = {
            'op': 'NUMBER',
            'number': usrinput
        }
    else:
        numberRQ = {
            'op': 'NUMBER',
            'number': encrypt_intvalue(cipher, usrinput)
        }
    numberOP = sendrecv_dict(client_sock, numberRQ)
    validate_response(client_sock, numberOP)


def run_client(client_sock, client_id, work_order=[], cipher=None):
    # List with numbers sent to the server
    lst = []
    # Preform the actions requested by the testing software
    for work in work_order:
        if work == 'START':
            start_action(client_sock, client_id, cipher)
        elif work == 'STOP':
            stop_action(client_sock, lst, cipher)
        elif work == 'QUIT':
            quit_action(client_sock)
        else:
            try:
                # If the work is a number, send it to the server as a NUMBER operation
                int(work)
                number_action(client_sock, work, lst, cipher)
                lst.append(int(work))
            except ValueError:
                # If the work is not a number, send it to the server as an operation
                otherRQ = {
                    'op': work
                }
                otherOP = sendrecv_dict(client_sock, otherRQ)
                validate_response(client_sock, otherOP)


def validate_args(args):
    # Validate the number of arguments
    if len(args) != 6:
        print_msg("ERRO", f"Usage: python3 {args[0]} id port encryption address work_order")
        sys.exit(1)
    # Validate type of arguments
    if not(args[2].isdigit()):
        print_msg("ERRO", f"Usage: port must be an integer")
        sys.exit(2)
    if int(args[2]) < 1024 or int(args[2]) > 65535:
        print_msg("ERRO", f"Usage: port must be between 1024 and 65535")
        sys.exit(2)
    if not(args[3].lower() in ['y', 'n']):
        print_msg("ERRO", f"Usage: encryption must be either 'y' or 'n'")
        sys.exit(2)
    # Tries to connect to the server and verify if it is a valid address or ip
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set timeout to 5 seconds to try to resolve the address and connect
    test_socket.settimeout(5)
    try:
        test_socket.connect((args[4], int(args[2])))
        test_socket.close()
    except:
        # If the address or port is not valid, print error and exit
        test_socket.close()
        print_msg("ERRO", f"Usage: address must be a valid IP or hostname or port")
        sys.exit(2)


def main():
    # Validate the arguments
    validate_args(sys.argv)
    # Get the port of the server
    port = int(sys.argv[2])
    # Get the hostname of the server
    machine = sys.argv[4]
    # Get the client_id
    client_id = sys.argv[1]
    # Set cipher key
    cipher = os.urandom(16)
    # Create socket and connect to the server
    work_order = sys.argv[5].split(",")
    try:
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((machine, port))
    except:
        print_msg("ERRO", f"Could not connect to {machine}:{port}")
        sys.exit(1)
    # Ask the user if he wants encryption or not
    if sys.argv[3] == "y":
        # Run the client with encryption
        run_client(client_sock, client_id, work_order, cipher)
    else:
        # Run the client without encryption
        run_client(client_sock, client_id, work_order)
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
