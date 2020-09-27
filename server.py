import socket
import tqdm
import os
import sys
import time
import shutil
from _thread import *
import threading

# device's IP address
SERVER_HOST = "127.0.0.1"

# efines the buffer size
BUFFER_SIZE = 4096

# creates the server socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# stores the port
SERVER_PORT = int(sys.argv[1])

# stores the directory
DIRECTORY = sys.argv[2]

# create two lists that will map the cache
names =[]
sizes =[]

#creates a variable that stores the amount of free memory in the cache (in bytes)
cacheAvailableMemory = 67108864

# create a lock
lock = threading.Lock()

# creates the cache folder
cache = 'cache'
path = os.getcwd() + "/" + cache
if(os.path.exists(cache)):
    shutil.rmtree(path)
os.mkdir(cache)

# search files in the main directory
def fetchDirectory(filesize, fileName,locked):

    # adds files smaller than 64MB to the cache
    if(filesize <= 67108864):
        addToCache(filesize, fileName)
        fetchCache(filesize, fileName, locked)

    else:
        # search for files in the main directory that are larger than 64MB
        lock.release()
        print("\n")
        progress = tqdm.tqdm(range(filesize), f"Sending {fileName}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(arq, "rb") as f:
            for _ in progress:

                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:

                    progress.refresh(nolock=False, lock_args=None)
                    progress.close()
                    print("\nFile sended successfully")
                    break
                client_socket.sendall(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))


        time.sleep(5) #used to test the multi-thread
        client_socket.close() # closes the client socket



# function responsible for getting files from the cache
def fetchCache(filesize, fileName, locked):

    print("\n")
    progress = tqdm.tqdm(range(filesize), f"Sending {fileName}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(cache + "/" + fileName, "rb") as f:
        for _ in progress:

            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                progress.refresh(nolock=False, lock_args=None)
                progress.close()
                print("\nFile sended successfully")
                break
            client_socket.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
    time.sleep(5) #used to test the multi-thread
    if(locked==1):
        lock.release()
    client_socket.close() # fcloses the client socket



# function responsible for adding file to cache
def addToCache(filesize,fileName):

    global cacheAvailableMemory

    if( filesize <= cacheAvailableMemory):
        names.append(fileName)
        sizes.append(filesize)
        cacheAvailableMemory = cacheAvailableMemory - filesize
        shutil.copyfile(arq,cache + "/" + fileName)

    else:
        # remove files until you have enough space
        while(filesize > cacheAvailableMemory):
            cacheAvailableMemory = cacheAvailableMemory + sizes[0]
            os.remove(cache + "/" +names[0])
            names.pop(0)
            sizes.pop(0)

        names.append(fileName)
        sizes.append(filesize)
        cacheAvailableMemory = cacheAvailableMemory - filesize
        shutil.copyfile(arq,cache + "/" + fileName)

def on_new_client(client_socket, address):

    # receives the file name requested by the client
    fileName = client_socket.recv(BUFFER_SIZE).decode()
    #stores the file name
    fileName = os.path.basename(fileName)


    if(fileName == "list"):   # send the list of files in the cache
        lock.release()
        print("\nSending list files")
        list = "\nList of files on cache server:\n\n"
        for name in names:
            list = list + name + "\n"
        client_socket.send(f"{list}".encode())
        client_socket.close()

    else:

        print(f"\nClient {address[0]} is requesting file {fileName}")

        global arq
        arq = DIRECTORY + "/" + fileName                 #concatenates the main directory and file name

        # check if the file exists in cache
        if(os.path.exists(fileName)):
            print(f"\nCache hit. File {fileName} sent to the client.")
            filesize = os.path.getsize(fileName)        # get the file size in bytes and store
            client_socket.send(f"{filesize}".encode())  # send the file size to the client
            fetchCache(int(filesize), fileName, 1)      #search the file in the main directory

        # check if the file exists in the main directory
        elif(os.path.exists(arq)):

            print(f"\nCache miss. File {fileName} sent to the client")

            filesize = os.path.getsize(arq)             # get the file size in bytes and store
            client_socket.send(f"{filesize}".encode())  # send the file size to the client
            locked = 1
            # check if you can already release
            if(filesize < cacheAvailableMemory):
                locked = 0
                lock.release()
            fetchDirectory(int(filesize), fileName , locked) #search the file in the main directory

        else:
            # file not found
            print(f"\nFile {fileName} not found")
            lock.release()
            client_socket.close()

# connect the socket to the address provided
s.bind((SERVER_HOST, int(SERVER_PORT)))

# start listening
s.listen()

#creates an infinite loop that keeps checking connections
while True:
    # accepts the connection, if any
    print("\nWaiting for connection")
    client_socket, address = s.accept()
    lock.acquire()
    # create a new thread
    threading._start_new_thread(on_new_client,(client_socket, address))




s.close()
