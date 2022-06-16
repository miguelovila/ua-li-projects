

#create a random password with 10 alphanumeric characters
import random
import string

def random_password():
    length= 10

    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

print(random_password())