from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

#untuk menggunakan processpoolexecutor, karena tidak mendukung subclassing pada process,
#maka class ProcessTheClient dirubah dulu menjadi function, tanpda memodifikasi behaviour didalamnya

def ProcessTheClient(request_str):
    try:
        hasil = httpserver.proses(request_str)
        return hasil + b'\r\n\r\n'
    except Exception as e:
        return f"HTTP/1.0 500 Internal Server Error\r\n\r\n{str(e)}".encode()


def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    my_socket.bind(('0.0.0.0', 8890))
    my_socket.listen(1)

    with ProcessPoolExecutor(20) as executor:
        while True:
            connection, client_address = my_socket.accept()
            #logging.warning("connection from {}".format(client_address))

            try:
                rcv = b""
                connection.settimeout(3)

                # baca awal request
                while True:
                    data = connection.recv(4096)
                    if not data:
                        break
                    rcv += data
                    if b"\r\n\r\n" in rcv:
                        break

                if not rcv:
                    connection.close()
                    continue

                # cek Content-Length
                headers_raw = rcv.decode(errors='ignore')
                content_length = 0
                for line in headers_raw.split("\r\n"):
                    if line.lower().startswith("content-length:"):
                        try:
                            content_length = int(line.split(":")[1].strip())
                        except:
                            pass

                body_start = rcv.find(b"\r\n\r\n") + 4
                current_body = rcv[body_start:]
                while len(current_body) < content_length:
                    chunk = connection.recv(4096)
                    if not chunk:
                        break
                    rcv += chunk
                    current_body += chunk

                # kirim request string ke proses
                request_str = rcv.decode(errors='ignore')
                future = executor.submit(ProcessTheClient, request_str)
                hasil = future.result(timeout=5)

                connection.sendall(hasil)

            except Exception as e:
                print("[SERVER ERROR]", e)

            connection.close()
            #menampilkan jumlah process yang sedang aktif
            jumlah = ['x' for i in the_clients if i.running() == True]
            print(jumlah)

def main():
    Server()


if __name__=="__main__":
    main()