import socket

host = "localhost"
port = 5000

# Example ISO message (very simple test)
msg = b"0800822000000000000004000000000000001234567890123456"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

s.send(msg)
response = s.recv(4096)

print("Response:", response)

s.close()