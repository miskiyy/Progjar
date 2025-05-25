from socket import *
import socket
import threading
import logging
import time
import sys
from concurrent.futures import ThreadPoolExecutor


from file_protocol import  FileProtocol
fp = FileProtocol()

# Rubahlah model pemrosesan concurrency yang ada, dari multithreading menjadi multithreading menggunakan pool

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        self.fp = FileProtocol()

    def run(self):
        try:
            d = ''
            while True:
                data = self.connection.recv(1024)
                if data:
                    d += data.decode()
                    if "\r\n\r\n" in d:
                        cmd = d.strip().split()
                        perintah = cmd[0].lower() if len(cmd) > 0 else 'unknown'
                        filename = cmd[1] if len(cmd) > 1 else ''
                        logging.warning(f"memproses request: {perintah} {filename}")

                        hasil = self.fp.proses_string(d.strip())
                        hasil = hasil + "\r\n\r\n"
                        self.connection.sendall(hasil.encode())
                        d = ''  # reset buffer kalau mau support multiple requests per connection
                else:
                    break
            self.connection.close()
            return True
        except Exception as e:
            logging.error(f"error saat menangani client {self.address}: {e}")



class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=8889, pool_size=3):
        self.ipinfo=(ipaddress,port)
        self.pool_size = pool_size
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.pool_size)

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}, pool (max={self.pool_size})")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(3)
        while True:
            connection, client_address = self.my_socket.accept()
            logging.warning(f"connection from {client_address}")

            handler = ProcessTheClient(connection, client_address)
            self.thread_pool.submit(handler.run)


def main():
    pool_size = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    svr = Server(ipaddress='0.0.0.0', port=8889, pool_size=pool_size)
    svr.run()


if __name__ == "__main__":
    main()