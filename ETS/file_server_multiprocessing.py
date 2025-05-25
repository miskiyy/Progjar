from socket import *
import socket
import logging
import sys
from multiprocessing import Pool

from file_protocol import FileProtocol

# fungsi handler client — harus fungsi biasa untuk Pool
def handle_client(conn_addr):
    connection, address = conn_addr
    fp = FileProtocol()
    d = ''
    while True:
        data = connection.recv(1024)
        if data:
            d += data.decode()
            if "\r\n\r\n" in d:
                try:
                    cmd = d.strip().split()
                    perintah = cmd[0].lower() if len(cmd) > 0 else 'unknown'
                    filename = cmd[1] if len(cmd) > 1 else ''
                    logging.warning(f"memproses request: {perintah} {filename}")
                except Exception as e:
                    logging.warning(f"gagal parsing request untuk logging: {e}")

                hasil = fp.proses_string(d.strip())
                hasil = hasil + "\r\n\r\n"
                connection.sendall(hasil.encode())
                break
        else:
            break
    connection.close()
    return True

class Server:
    def __init__(self, ipaddress='0.0.0.0', port=8889, pool_size=3):
        self.ipinfo = (ipaddress, port)
        self.pool_size = pool_size
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.process_pool = Pool(processes=self.pool_size)

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo} dengan process pool (pool_size={self.pool_size})")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        while True:
            connection, client_address = self.my_socket.accept()
            logging.warning(f"connection from {client_address}")
            self.process_pool.apply_async(handle_client, args=((connection, client_address),))

def main():
    pool_size = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    svr = Server(ipaddress='0.0.0.0', port=8889, pool_size=pool_size)
    svr.run()

if __name__ == "__main__":
    main()