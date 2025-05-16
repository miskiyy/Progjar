import socket
import threading
import time

SERVER_IP = '0.0.0.0'  
PORT = 45000
NUM_CLIENTS = 5 

def client_thread(id):
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((SERVER_IP, PORT))
			print(f"[Client {id}] Connected to server")

        	# 1. Kirim command yang valid
            s.sendall(b"TIME\r\n")
        	response = s.recv(1024)
        	print(f"[Client {id}] TIME Response: {response.decode().strip()}")

        	# 2. Kirim command yang TIDAK valid
        	s.sendall(b"HELLO\r\n")
        	s.settimeout(1.0)
        	try:
            	response = s.recv(1024)
            	print(f"[Client {id}] Unexpected Response: {response.decode().strip()}")
        	except socket.timeout:
            	print(f"[Client {id}] No response for invalid command (expected)")

        	# 3. QUIT untuk nutup koneksi
        	s.sendall(b"QUIT\r\n")

	except Exception as e:
				print(f"[Client {id}] Error: {e}")

def main():
	threads = []
	start_time = time.time()

	for i in range(NUM_CLIENTS):
    	t = threading.Thread(target=client_thread, args=(i,))
    	t.start()
    	threads.append(t)

	for t in threads:
    	t.join()

	duration = time.time() - start_time
	print(f"\nAll clients done in {duration:.2f} seconds")

if __name__ == "__main__":
	main()
