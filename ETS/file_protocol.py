import json
import logging
import shlex

from file_interface import FileInterface

"""
* class FileProtocol bertugas untuk memproses 
data yang masuk, dan menerjemahkannya apakah sesuai dengan
protokol/aturan yang dibuat

* data yang masuk dari client adalah dalam bentuk bytes yang 
pada akhirnya akan diproses dalam bentuk string

* class FileProtocol akan memproses data yang masuk dalam bentuk
string
"""

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()
    def proses_string(self,string_datamasuk=''):
        logging.warning(f"string diproses: {string_datamasuk}")
        try:
            if string_datamasuk.strip().upper().startswith("UPLOAD "):
                # pisahkan menjadi: UPLOAD filename base64_content
                # UPLOAD <spasi> filename <spasi> base64_content (base64_content bisa mengandung spasi)
                parts = string_datamasuk.strip().split(' ', 2)
                if len(parts) < 3:
                    return json.dumps(dict(status='ERROR', data='Format upload salah'))
                c_request = parts[0].lower()
                filename = parts[1]
                base64_content = parts[2]
                params = [filename, base64_content]
                cl = getattr(self.file, c_request)(params)
                return json.dumps(cl)
            else:
                # Untuk request lain, tetap gunakan shlex.split
                c = shlex.split(string_datamasuk.lower())
                c_request = c[0].strip()
                logging.warning(f"memproses request: {c_request}")
                params = [x for x in c[1:]]
                cl = getattr(self.file,c_request)(params)
                return json.dumps(cl)
        except Exception as e:
            logging.warning(f"Exception: {e}")
            return json.dumps(dict(status='ERROR',data='request tidak dikenali'))


if __name__=='__main__':
    #contoh pemakaian
    fp = FileProtocol()
    print(fp.proses_string("LIST"))
    print(fp.proses_string("GET pokijan.jpg"))