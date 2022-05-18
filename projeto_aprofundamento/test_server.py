from subprocess import Popen, PIPE
import subprocess
import random
import signal
import os

test_server = None


def server_test(args=""):
    # Argument parser for server.py
    proc = Popen(f"python3 server.py {args}", stdout=PIPE, shell=True)
    for line in iter(proc.stdout.readline, b''):
        # Return the first line of the output
        return line.decode("utf-8").rstrip()


def server_prober(id, port, encryption, address, work_order):
    # Argument parser for server_prober.py
    proc = Popen(
        f"python3 server_prober.py {id} {port} {encryption} {address} {work_order}", stdout=PIPE, shell=True)
    stdout = ""
    for line in iter(proc.stdout.readline, b''):
        stdout += line.decode("utf-8").rstrip()
    return stdout


def test_insufficient_args():
    # Test that the server prints the correct usage message when insufficient arguments are given
    assert "Usage: python3 server.py port" in server_test("")


def test_more_args():
    # Test that the server prints the correct usage message when more arguments are given
    assert "Usage: python3 server.py port" in server_test("arg1 arg2 arg3")
    assert "Usage: python3 server.py port" in server_test("1234 2222 arg3")
    assert "Usage: python3 server.py port" in server_test("1234 2222 arg3 arg4")


def test_invalid_port():
    # Test that the server prints the correct usage message when an invalid port is given
    assert "Usage: port must be an integer" in server_test("invalid_port")
    assert "Usage: port must be an integer" in server_test("-1")
    assert "Usage: port must be between 1024 and 65535" in server_test("65536")
    assert "Usage: port must be between 1024 and 65535" in server_test("1023")
    assert "Usage: port must be between 1024 and 65535" in server_test("0")


def test_run_server():
    # Runs the server when testing and returns the process
    global test_server
    test_server = subprocess.Popen(["python3","server.py","1024"], stdin=None, stdout=PIPE, stderr=None, shell=False)


def test_normal_run():
    # Test that the server runs normally with any random valid input
    rnd_list = [random.randrange(-random.randint(1, 100), random.randint(1, 100), 1) for i in range(random.randint(1, 100))]
    rnd_list_str = ','.join(str(n) for n in rnd_list)
    max_num = max(rnd_list)
    min_num = min(rnd_list)
    assert f"[INFO]Connection established[INFO]Numbers: {rnd_list}[INFO]Minimum: {min_num}[INFO]Maximum: {max_num}" == server_prober("user0", 1024, 'y', "localhost", f"START,{rnd_list_str},STOP")
    assert f"[INFO]Connection established[INFO]Numbers: {rnd_list}[INFO]Minimum: {min_num}[INFO]Maximum: {max_num}" == server_prober("user0", 1024, 'n', "localhost", f"START,{rnd_list_str},STOP")


def test_invalid_op():
    # Test that the server sends the correct usage message when an invalid operation is given
    assert "[INFO]Connection established[ERRO]Invalid operation" == server_prober("user0", 1024, 'n', "localhost", "START,INAVLIDOP,STOP")
    assert "[ERRO]Invalid operation" == server_prober("user0", 1024, 'n', "localhost", "INAVLIDOP,START,INAVLIDOP,STOP")
    assert "[INFO]Connection established[ERRO]Invalid operation" == server_prober("user0", 1024, 'n', "localhost", "START,10,INAVLIDOP")
    assert "[INFO]Connection established[ERRO]Invalid operation" == server_prober("user0", 1024, 'y', "localhost", "START,INAVLIDOP,STOP")
    assert "[ERRO]Invalid operation" == server_prober("user0", 1024, 'y', "localhost", "INAVLIDOP,START,INAVLIDOP,STOP")
    assert "[INFO]Connection established[ERRO]Invalid operation" == server_prober("user0", 1024, 'y', "localhost", "START,10,INAVLIDOP")


def test_unexpected_op():
    # Test that the server sends the correct usage message when an unexpected operation is given
    assert "[ERRO]Client not registered" == server_prober("user0", 1024, 'y', "localhost", "10,20,30,40,-10,1000,STOP")
    assert "[ERRO]Client not registered" == server_prober("user0", 1024, 'y', "localhost", "QUIT,20,30,40,-10,1000,STOP")
    assert "[ERRO]Client not registered" == server_prober("user0", 1024, 'y', "localhost", "STOP,20,30,40,-10,1000,STOP")
    assert "[ERRO]Client not registered" == server_prober("user0", 1024, 'n', "localhost", "10,20,30,40,-10,1000,STOP")
    assert "[ERRO]Client not registered" == server_prober("user0", 1024, 'n', "localhost", "QUIT,20,30,40,-10,1000,STOP")
    assert "[ERRO]Client not registered" == server_prober("user0", 1024, 'n', "localhost", "STOP,20,30,40,-10,1000,STOP")


def test_invalid_number():
    # Test that the server sends the correct message when an invalid number is given
    assert "[INFO]Connection established[ERRO]Invalid operation" == server_prober("user0", 1024, 'y', "localhost", "START,20,QUERO,40,-10,1000,STOP")
    assert "[INFO]Connection established[ERRO]Invalid operation" == server_prober("user0", 1024, 'y', "localhost", "START,20,30,VINTE,-10,1000,STOP")
    assert "[INFO]Connection established[ERRO]Invalid operation" == server_prober("user0", 1024, 'n', "localhost", "START,20,NESTE,40,-10,1000,STOP")
    assert "[INFO]Connection established[ERRO]Invalid operation" == server_prober("user0", 1024, 'n', "localhost", "START,20,1000,TRABALHO,-10,1000,STOP")


def test_exists_user():
    # Test that the server sends the correct message when an user already exists
    assert "[INFO]Connection established[ERRO]Client already registered" == server_prober("user0", 1024, 'y', "localhost", "START,20,START,40,-10,1000,STOP")
    assert "[INFO]Connection established[ERRO]Client already registered" == server_prober("user0", 1024, 'n', "localhost", "START,20,30,START,-10,1000,STOP")


def test_insufficient_data():
    assert "[INFO]Connection established[ERRO]No numbers received" == server_prober("user0", 1024, 'y', "localhost", "START,STOP")
    assert "[INFO]Connection established[ERRO]No numbers received" == server_prober("user0", 1024, 'n', "localhost", "START,STOP")


def test_quit():
    assert "[INFO]Connection established[INFO]Client terminated" == server_prober("user0", 1024, 'y', "localhost", "START,QUIT,STOP")
    assert "[INFO]Connection established[INFO]Client terminated" == server_prober("user0", 1024, 'y', "localhost", "START,QUIT,STOP")
    assert "[INFO]Connection established[INFO]Client terminated" == server_prober("user0", 1024, 'n', "localhost", "START,10,20,30,QUIT,STOP")
    assert "[INFO]Connection established[INFO]Client terminated" == server_prober("user0", 1024, 'n', "localhost", "START,10,20,30,QUIT,STOP")


def test_shutdown_server():
    # Shuts down the server using its PID
    global test_server
    os.kill(test_server.pid, signal.SIGTERM)