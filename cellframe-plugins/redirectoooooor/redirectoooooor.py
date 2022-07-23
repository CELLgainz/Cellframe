from DAP.Core import logIt
from DAP import configGetItem

import socket
import threading

plugin_name="redirectoooooor"
version="0.1"
port = 12345

def redirectData():
    node_socket_path = configGetItem("conserver", "listen_unix_socket_path")

    ext_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        ext_socket.bind(("localhost", port))
    except:
        logIt.error("Failed to bind external socket! Port in use?")

    while True:
        local_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        ext_socket.listen()
        logIt.notice(f"{plugin_name}: External socket listening...")
        ext_conn, addr = ext_socket.accept()
        logIt.notice(f"{plugin_name}: Client connected from {addr}!")
        fwd = ext_conn.recv(1024)
        try:
            local_socket.connect(node_socket_path)
            logIt.notice(f"{plugin_name}: Connected to local socket!")
        except:
            logIt.error(f"{plugin_name}: Connection to local socket failed!")
        fwd_str = fwd.decode("utf-8")
        fwd_str = fwd_str.replace("\r\n", " ")
        logIt.notice(f"{plugin_name}: Received data: {fwd_str}")
        local_socket.sendall(fwd)
        data = local_socket.recv(1024)
        ext_conn.sendto(data, addr)
        ext_conn.close()
        local_socket.close()

def init():
    logIt.notice(f"{plugin_name} version {version} started...")
    socketThread = threading.Thread(target=redirectData)
    socketThread.start()
    return 0

def deinit():
    return