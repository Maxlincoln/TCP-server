import socket
import tqdm
import os
import sys
import time

# defines the buffer size
BUFFER_SIZE = 4096 #

# create the client socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# checks if 4 parameters have passed (this means that the client wants the list of files in the cache)
if(len(sys.argv)==4):
    host = sys.argv[1]
    port = int(sys.argv[2])
    fileName = sys.argv[3]

else:
    host = sys.argv[1]
    port = int(sys.argv[2])
    fileName = sys.argv[3]
    local = sys.argv[4]


print(f"\n[+] Connecting to {host}:{port}")

# checks if there is someone listening at that address / port, if any, connect
x = s.connect_ex((host, port))

if(x!= 0):
    print("\nServer not found")
    s.close()
    sys.exit()

# send the requested file name to the server
s.send(f"{fileName}".encode())

# receives something from the server (the size of the file to be transferred or the list of files in the cache)
serverReturn = s.recv(BUFFER_SIZE).decode()

# if the client requested the list, print the list
if(len(sys.argv)==4):
    print('\033[32m' + serverReturn + '\033[0;0m')
    s.close()
    sys.exit()

# stores what returned from the server
filesize = serverReturn

# checks if the returned one can be transformed to an integer, in case of error it means that the requested file does not exist on the server
try:
    filesize = int(filesize)

except ValueError:
    print(f"\nFile {fileName} not found")
    s.close()
    sys.exit()

# starts receiving the file
print("\n")
progress = tqdm.tqdm(range(filesize), f"Receiving {fileName}", unit="B", unit_scale=True, unit_divisor=1024)

# concatenates the directory where the file will be saved with the file name
arq = local + "/" + fileName

# receives data in packets of up to 4096 bytes (buffer size)
with open(arq, "wb") as f:

    for _ in progress:
        bytes_read = s.recv(BUFFER_SIZE)
        if not bytes_read:
            # file transmitting is done
            progress.refresh(nolock=False, lock_args=None)
            progress.close()
            print("\nFile received successfully")
            break
        f.write(bytes_read)
        # update the progress bar
        progress.update(len(bytes_read))
# close the socket
s.close()
