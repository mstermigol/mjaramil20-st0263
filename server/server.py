import json
import os
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, request, Response, jsonify
import time
from datetime import datetime
import random

env_path = os.path.join(os.path.dirname(__file__), "./configs/.env_server")
load_dotenv(dotenv_path=env_path)

SERVER_URL = os.getenv("SERVER_URL")
SERVER_PORT = os.getenv("SERVER_PORT")

app = Flask(__name__)

users = {}
files = {}
activeUsers = {}

@app.route("/login", methods=["POST"])
def login():
    pserverData = request.json
    username = pserverData.get("username")
    password = pserverData.get("password")
    url = pserverData.get("url")
    lastPing = pserverData.get("lastPing")
    if username in users:
        if users[username] == password:
            activeUsers[url] = lastPing
            return Response(status=200)
        else:
            return Response(status=401)
    else:
        users[username] = password
        activeUsers[url] = lastPing
        return Response(status=200)

@app.route("/index", methods=["POST"])
def index():
    pserverData = request.json
    pserverIndex = pserverData.get("index")
    url = pserverData.get("url")
    for file in pserverIndex:
        if file in files and url not in files[file]:
            files[file].append(url)
        elif file not in files:
            files[file] = [url]
    return Response(status=200)

@app.route("/upload", methods=["GET"])
def upload():
    pserverData = request.json
    url = pserverData.get("url")
    active = list(activeUsers.keys())

    if (len(active) > 1):
        peers = []
        for urlServer in active:
            if (urlServer != url):
                peers.append(urlServer)        
        peer = random.choice(peers)
        return peer, 200, {'Content-Type': 'text/plain'}    
    else:
        return Response(status=404)
    
@app.route("/download", methods=["GET"])
def download():
    pserverData = request.json
    url = pserverData.get("url")
    file_name = pserverData.get("file_name")
    if file_name in files:
        potentialUrls = files[file_name]
        if(len(potentialUrls) < 2):
            peers = []
            for urlPeer in potentialUrls:
                if urlPeer != url and urlPeer in activeUsers:
                    peers.append(urlPeer)
            if peers:
                peer = random.choice(peers)
                if (peer):
                    return peer, 200, {'Content-Type': 'text/plain'}
    return Response(status=404)

@app.route("/ping", methods=["POST"])
def ping():
    pserverData = request.json
    url = pserverData.get("url")
    lastPing = pserverData.get("lastPing")
    activeUsers[url] = lastPing
    return Response(status=200)

def CheckPings():
    while True:
        currentTime = datetime.now()
        usersRemove = []
        if activeUsers:
            for url, lastPing in activeUsers.items():
                if (currentTime - datetime.strptime(lastPing, "%Y-%m-%d %H:%M:%S")).total_seconds() > 15:
                    usersRemove.append(url)
            for url in usersRemove:
                del activeUsers[url]
                print(f"{url} deleted")
                print(users)
                print(files)
                print(activeUsers)    
        time.sleep(5)

if __name__ == "__main__":
    ping_checker_thread = Thread(target=CheckPings)
    ping_checker_thread.daemon = True
    ping_checker_thread.start()
    app.run(host=SERVER_URL, port=SERVER_PORT, debug=True)