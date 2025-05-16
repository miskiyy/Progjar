import socket
import threading
import logging
from datetime import datetime

CRLF = b'\r\n'

class ProcessTheClient(threading.Thread):
	def __init__(self, connection, address):
    	threading.Thread.__init__(self)
    	self.connection = connection
    	self.address = address
    	self.running = True

	def run(self):
    	buffer = b""
    	try:
        	while self.running:
            	data = self.connection.recv(1024)
            	if not data:
                	break
            	logging.warning(f"[{self.address}] Messages: {data!r}")
            	buffer += data
            	while CRLF in buffer:
                	line, buffer = buffer.split(CRLF, 1)
                	line_str = line.decode('utf-8', errors='ignore').strip()

                	if line_str.upper().startswith("TIME"):
                    	now = datetime.now()
                    	jam = now.strftime("%H:%M:%S")
                    	response = f"JAM {jam}\r\n"
                    	logging.warning(f"[{self.address}] Sending: {response.strip()}")
                    	self.connection.sendall(response.encode('utf-8'))

                	elif line_str.upper() == "QUIT":
                    	logging.warning(f"[{self.address}] Received QUIT. Closing connection.")
                    	self.running = False
                    	break
                	else:
                    	logging.warning(f"[{self.address}] Unknown command: {line_str!r}")
    	except Exception as e:
        	logging.warning(f"Exception from {self.address}: {e}")
    	finally:
        	self.connection.close()
        	logging.info(f"Connection closed from {self.address}")

class TimeServer(threading.Thread):
	def __init__(self, host='0.0.0.0', port=45000):
    	threading.Thread.__init__(self)
    	self.host = host
    	self.port = port
    	self.clients = []
    	self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	def run(self):
    	self.sock.bind((self.host, self.port))
    	self.sock.listen(5)
    	logging.warning(f"Time server listening on {self.host}:{self.port}")
    	try:
        	while True:
            	conn, addr = self.sock.accept()
            	logging.warning(f"Connection from {addr}")
            	client_thread = ProcessTheClient(conn, addr)
            	client_thread.start()
            	self.clients.append(client_thread)
    	except KeyboardInterrupt:
        	logging.warning("Server shutting down.")
    	finally:
        	self.sock.close()

def main():
	logging.basicConfig(level=logging.WARNING, format='%(asctime)s %(levelname)s %(message)s')
	server = TimeServer()
	server.start()

if __name__ == "__main__":
	main()
