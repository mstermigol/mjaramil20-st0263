import os
import sys
import time
import grpc
import dotenv
import pserver_pb2
import pserver_pb2_grpc
from pserver import serve
from threading import Thread


env_path = os.path.join(os.path.dirname(__file__),
                        f"../configs/.env_{sys.argv[1]}")
dotenv.load_dotenv(dotenv_path=env_path)

PSERVER_PORT = os.getenv("PSERVER_PORT")
PSERVER_URL = os.getenv("PSERVER_URL")

def LogIn():
    username = input("Enter username: ")
    password = input("Enter password: ") 
    request = pserver_pb2.Credentials(username = username, password = password)
    reply = stub.RequestLogIn(request)
    while reply.status_code == 401:
        print("Invalid credentials. Please try again")
        print()
        username = input("Enter username: ")
        password = input("Enter password: ") 
        request = pserver_pb2.LogIn(username = username, password = password)
        reply = stub.RequestLogIn(request) 
    requestPing = pserver_pb2.Any()
    stub.RequestPinging(requestPing)    
    print("You are logged in")
    print()
    

if __name__ == "__main__":
    channel = grpc.insecure_channel(f"{PSERVER_URL}:{PSERVER_PORT}")
    stub = pserver_pb2_grpc.PServerStub(channel)
    pserver_thread = Thread(target=serve)
    pserver_thread.daemon = True
    pserver_thread.start()
    LogIn()
    while True:
        print("0. Exit")
        print("1. Download")
        print("2. Upload")
        print("3. List Index")
        rpc_call = input("Option: ")
        if rpc_call == "0":
            break
        elif rpc_call == "1":
            file_name = input("Enter the file name: ")
            request = pserver_pb2.File(file_name = file_name)
            reply = stub.DownloadFile(request)
            if reply.status_code == 200:
                print("Successful file download")
            elif reply.status_code == 404:
                print("Could not download the file")
        elif rpc_call == "2":
            file_name = input("Enter the file name: ")
            request = request = pserver_pb2.File(file_name = file_name)
            reply = stub.UploadFile(request)
            if reply.status_code == 200:
                print("Uploaded successfully")
            elif reply.status_code == 409:
                print("The file already existed in the other peer")
            elif reply.status_code == 404:
                print("There are no peers at the moment")
        elif rpc_call == "3":
            request = pserver_pb2.Any()
            reply = stub.ListIndex(request)
            if reply.my_list:
                print(reply.my_list)
            else:
                print("There are no files")



    channel.close()
