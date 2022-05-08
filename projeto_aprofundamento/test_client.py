from subprocess import Popen, PIPE


def client_test(args=""):
    # Argument parser for client.py
    proc = Popen(f"python3 client.py {args}", stdout=PIPE, shell=True)
    for line in iter(proc.stdout.readline, b''):
        # Return the first line of the output
        return line.decode("utf-8").rstrip()


def test_client_insufficient_args():
    # Test that the client prints the correct usage message when insufficient arguments are given
    assert "Usage: python3 client.py client_id port (address)" in client_test("")
    assert "Usage: python3 client.py client_id port (address)" in client_test("user")


def test_client_more_args():
    # Test that the client prints the correct usage message when more arguments are given
    assert "Usage: python3 client.py client_id port (address)" in client_test("1234 2222 arg3 arg4")
    assert "Usage: python3 client.py client_id port (address)" in client_test("1234 2sa2 arg3 arg4")
    assert "Usage: python3 client.py client_id port (address)" in client_test("1234 0001 arg3 arg4 arg5")


def test_client_invalid_port():
    # Test that the client prints the correct usage message when an invalid port is given
    assert "Usage: port must be an integer" in client_test("user invalid_port")
    assert "Usage: port must be an integer" in client_test("user -1")
    assert "Usage: port must be between 1024 and 65535" in client_test("user 65536")
    assert "Usage: port must be between 1024 and 65535" in client_test("user 1023")
    assert "Usage: port must be between 1024 and 65535" in client_test("user 0")


def test_client_valid_address_port():
    # Test that the client prints the correct usage message when an invalid address or ip or port is given
    assert "Usage: address must be a valid IP or hostname or port" in client_test("user 1234 invalid_address")
    assert "Usage: address must be a valid IP or hostname or port" in client_test("user 1234 192.168..1")
    assert "Usage: address must be a valid IP or hostname or port" in client_test("user 1234 450.168.xa.1")
    assert "Usage: address must be a valid IP or hostname or port" in client_test("user 1234 192.168.1.256")
    assert "Usage: address must be a valid IP or hostname or port" in client_test("user 1234 -somehostname")
    assert "Usage: address must be a valid IP or hostname or port" in client_test("user 1234 !somehostname")
    assert "Usage: address must be a valid IP or hostname or port" in client_test("user 1234 somerandom.com")
    assert "Usage: address must be a valid IP or hostname or port" in client_test("user 1234 maomv.rocks")
