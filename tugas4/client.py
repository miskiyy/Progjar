import socket

def send_request(request, host='localhost', port=8889):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(request.encode())
    response = b""
    while True:
        data = s.recv(4096)
        if not data:
            break
        response += data
    s.close()
    return response.decode(errors='ignore')


def list_files():
    req = "GET /list HTTP/1.0\r\n\r\n"
    resp = send_request(req)
    print("=== LIST FILES ===")
    print(resp)


def upload_file(filename, host='localhost', port=8889):
    try:
        with open(filename, 'r') as f:  # baca sebagai text, bukan binary
            filedata = f.read()
        body = f"{filename}\n{filedata}"
        req = f"POST /upload HTTP/1.0\r\nContent-Length: {len(body)}\r\n\r\n{body}"
        resp = send_request(req, host, port)
        print("=== UPLOAD FILE ===")
        print(resp)
    except Exception as e:
        print("Upload failed:", e)


def delete_file(filename, host='localhost', port=8890):
    body = filename + "\r\n"  # <- ini kuncinyaaa
    headers = (
        f"POST /delete HTTP/1.0\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"\r\n"
    )
    request = headers + body
    resp = send_request(request, host, port)
    print("=== DELETE FILE ===")
    print(resp)


if __name__ == "__main__":
    print("[CLIENT] Mulai list file")
    list_files()

    print("[CLIENT] Upload file")
    upload_file('testing.txt')

    print("[CLIENT] Selesai upload, list lagi")
    list_files()

    print("[CLIENT] Delete")
    delete_file('testing.txt')

    print("[CLIENT] List final")
    list_files()
