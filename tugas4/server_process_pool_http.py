from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

#fungsi yang akan dijalankan oleh processpool, hanya memproses data string
def ProcessTheClientString(request_str):
        try:
                hasil = httpserver.proses(request_str)
                return hasil + b'\r\n\r\n'
        except Exception as e:
                return f"HTTP/1.0 500 Internal Server Error\r\n\r\n{str(e)}".encode()

#fungsi utama yang akan menerima koneksi dan membaca data dari socket
def Server():
        the_clients = []
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        my_socket.bind(('0.0.0.0', 8890))
        my_socket.listen(1)

        with ProcessPoolExecutor(20) as executor:
                while True:
                        connection, client_address = my_socket.accept()
                        rcv = ""
                        while True:
                                try:
                                        data = connection.recv(4096)
                                        if data:
                                                d = data.decode()
                                                rcv += d
                                                if rcv[-2:] == '\r\n':
                                                        # end of command, proses string
                                                        future = executor.submit(ProcessTheClientString, rcv)
                                                        hasil = future.result(timeout=10)
                                                        connection.sendall(hasil)
                                                        rcv = ""
                                                        connection.close()
                                                        break
                                        else:
                                                break
                                except OSError:
                                        break
                        connection.close()
                        #menampilkan jumlah process yang sedang aktif
                        jumlah = ['x' for i in the_clients if i.running()==True]
                        print(jumlah)

def main():
        Server()

if __name__=="__main__":
        main()