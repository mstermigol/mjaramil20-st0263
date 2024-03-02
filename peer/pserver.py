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

env_path = os.path.join(os.path.dirname(__file__),
                        f"../configs/.env_{sys.argv[2]}")
dotenv.load_dotenv(dotenv_path=env_path)

SERVER_URL = os.getenv("SERVER_URL")
SERVER_PORT = os.getenv("SERVER_PORT")

PSERVER_PORT = os.getenv("PSERVER_PORT")
PSERVER_URL = os.getenv("PSERVER_URL")

app = Flask(__name__)

class PServerServicer(pserver_pb2_grpc.PServerServicer):
    def RequestLogIn(self, request, context):
        username = request.username
        password = request.password
        credentials = {"username": username, "password": password}
        replyREST = logIn(credentials=credentials)
        reply = pserver_pb2.Reply()
        reply.status_code = replyREST.status_code
        return reply
    
    def DownloadFile(self, request, context):
        file_name = request.file_name
        reply = pserver_pb2.Reply()
        reply.status_code = 200
        return reply
    


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server.add_insecure_port(f"{PSERVER_URL}:{PSERVER_PORT}")
    pserver_pb2_grpc.add_PServerServicer_to_server(PServerServicer(), server)
    server.start()
    server.wait_for_termination()

def uploadFile(file_name):
    url = f"{PSERVER_URL}:{PSERVER_PORT}"
    pserverData = {"file_name": file_name, "url": url}
    reply = requests.get(
        f"http://{SERVER_URL}:{SERVER_PORT}/upload", json=pserverData
    )
    return reply

def logIn(credentials):
    url = f"{PSERVER_URL}:{PSERVER_PORT}"
    username = credentials.get("username")
    password = credentials.get("password")
    pserverData = {"url": url, "username": username, "password": password}
    reply = requests.post(
        f"http://{SERVER_URL}:{SERVER_PORT}/login", json=pserverData
    )
    return reply




if __name__ == "__main__":
    serve()