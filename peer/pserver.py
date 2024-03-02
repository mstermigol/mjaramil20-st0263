from datetime import datetime
import os 
import sys
import grpc
import time
import dotenv
import requests
import pserver_pb2
from flask import Flask
import pserver_pb2_grpc
from concurrent import futures
from threading import Thread

env_path = os.path.join(os.path.dirname(__file__),
                        f"../configs/.env_{sys.argv[2]}")
dotenv.load_dotenv(dotenv_path=env_path)

SERVER_URL = os.getenv("SERVER_URL")
SERVER_PORT = os.getenv("SERVER_PORT")

PSERVER_PORT = os.getenv("PSERVER_PORT")
PSERVER_URL = os.getenv("PSERVER_URL")

app = Flask(__name__)

files = ["siii", "no", "jaja", "2"]

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server.add_insecure_port(f"{PSERVER_URL}:{PSERVER_PORT}")
    pserver_pb2_grpc.add_PServerServicer_to_server(PServerServicer(), server)
    server.start()
    server.wait_for_termination()

class PServerServicer(pserver_pb2_grpc.PServerServicer):
    def RequestLogIn(self, request, context):
        username = request.username
        password = request.password
        lastPing = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        credentials = {"username": username, "password": password, "lastPing": lastPing}
        replyREST = logIn(credentials=credentials)
        reply = pserver_pb2.Reply()
        reply.status_code = replyREST.status_code
        SendIndex()
        return reply
    
    def DownloadFile(self, request, context):
        file_name = request.file_name
        channel = grpc.insecure_channel("localhost:5101")
        stub = pserver_pb2_grpc.PServerStub(channel)
        reply = stub.RequestUpload(pserver_pb2.File(file_name=file_name))
        return reply
    
    def UploadFile(self, request, context):
        file_name = request.file_name
        reply = UploadFileRequest()
        if reply.status_code == 200:
            print(reply.text)
            channel = grpc.insecure_channel(reply.text)
            stub = pserver_pb2_grpc.PServerStub(channel)
            reply = stub.RequestUpload(pserver_pb2.File(file_name=file_name))
            if reply.status_code == 200:
                return reply
            else:
                reply = pserver_pb2.Reply()
                reply.status_code = 409
                return reply
        else:
            reply = pserver_pb2.Reply()
            reply.status_code = 404
            return reply
    
    def RequestUpload(self, request, context):
        file_name = request.file_name
        if file_name not in files:
            files.append(file_name)
            reply = pserver_pb2.Reply()
            reply.status_code = 200
            SendIndex()
            return reply
        else:
            reply = pserver_pb2.Reply()
            reply.status_code = 409
            return reply

    def RequestPinging(self, request, context):
        StartPinging()
        reply = pserver_pb2.Reply()
        reply.status_code = 200
        return reply

def SendIndex():
    pserver_data = {"index": files, "url": f"{PSERVER_URL}:{PSERVER_PORT}"}
    response = requests.post(
        f"http://{SERVER_URL}:{SERVER_PORT}/index", json=pserver_data)
    return response.status_code 



def UploadFileRequest():
    url = f"{PSERVER_URL}:{PSERVER_PORT}"
    pserverData = {"url": url}
    reply = requests.get(
        f"http://{SERVER_URL}:{SERVER_PORT}/upload", json=pserverData
    )
    return reply

def logIn(credentials):
    url = f"{PSERVER_URL}:{PSERVER_PORT}"
    username = credentials.get("username")
    password = credentials.get("password")
    lastPing = credentials.get("lastPing")
    pserverData = {"url": url, "username": username, "password": password, "lastPing": lastPing}
    reply = requests.post(
        f"http://{SERVER_URL}:{SERVER_PORT}/login", json=pserverData
    )
    return reply

def StartPinging():
    ping_checker_thread = Thread(target=SendPingThread)
    ping_checker_thread.daemon = True
    ping_checker_thread.start()

def SendPingThread():
    while True:
        url = f"{PSERVER_URL}:{PSERVER_PORT}"
        lastPing = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pserverData = {"url": url, "lastPing": lastPing}
        requests.post(
            f"http://{SERVER_URL}:{SERVER_PORT}/ping", json=pserverData
        )
        time.sleep(10)

    

if __name__ == "__main__":
    serve()