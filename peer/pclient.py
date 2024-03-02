import os
import sys
import time
import grpc
import dotenv
import pserver_pb2
import pserver_pb2_grpc
from pserver import serve, upload_file
from threading import Thread


env_path = os.path.join(os.path.dirname(__file__),
                        f"../configs/.env_{sys.argv[1]}")
dotenv.load_dotenv(dotenv_path=env_path)

PSERVER_PORT = os.getenv("PSERVER_PORT")
PSERVER_URL = os.getenv("PSERVER_URL")


if __name__ == "__main__":
    channel = grpc.insecure_channel(f"{PSERVER_URL}:{PSERVER_PORT}")
    stub = pserver_pb2_grpc.PServerStub(channel)
    pserver_thread = Thread(target=serve)
    pserver_thread.daemon = True
    pserver_thread.start()
    while True:
        print("0. Exit")
        print("1. Download")
        print("2. Upload")
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
                print("File not found")
        elif rpc_call == "2":
            file_name = input("Enter the file name: ")
            response = upload_file(file_name)
            if response.status_code == 200:
                print("Uploaded")
            else:
                print("error")



    channel.close()
