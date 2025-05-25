import json
import subprocess
import csv
import time
from itertools import product
import argparse

def start_server(server_type, workers):
    # Fix command agar thread bener-bener pake multithreading dan process pake multiprocessing
    if server_type == 'thread':
        cmd = ['python3', 'file_server_multithreading.py', str(workers)]
    else:
        cmd = ['python3', 'file_server_multiprocessing.py', str(workers)]
    return subprocess.Popen(cmd)

def run_client_test(operation, server_address, file_size, workers, use_process_pool):
    cmd = [
        'python3', 'client_stress_test.py',
        '--server', server_address,
        '--operation', operation,
        '--file-size', str(file_size),
        '--workers', str(workers)
    ]
    
    if use_process_pool:
        cmd.append('--use-process-pool')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"[Client Error] {result.stderr.strip()}")
            return None
    except Exception as e:
        print(f"[Client Exception] Client test failed: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=str, default='stress_test_results.csv', help='Output CSV filename')
    args = parser.parse_args()

    operations = ['upload', 'download']
    volumes = [10, 50, 100]
    client_workers = [1, 5, 50]
    server_workers = [1, 5, 50]
    server_types = ['thread', 'process']

    combinations = list(product(operations, volumes, client_workers, server_types, server_workers))

    with open(args.output, 'w', newline='') as csvfile:
        fieldnames = [
            'test_id',
            'operation',
            'file_size_mb',
            'client_workers',
            'server_type',
            'server_workers',
            'total_time',
            'throughput_bytes_sec',
            'client_success',
            'client_failed',
            'server_status'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        test_id = 1
        for operation, file_size, c_workers, s_type, s_workers in combinations:
            print(f"\n[TEST {test_id}] {operation.upper()} {file_size}MB | client={c_workers}, server={s_type}({s_workers})")

            # Kill server dengan pkill -f 'file_server' masih dipakai, tapi hati2
            subprocess.run(['pkill', '-f', 'file_server'], stderr=subprocess.DEVNULL)
            time.sleep(1)

            server_proc = start_server(s_type, s_workers)
            time.sleep(2)  # waktu buat server siap

            try:
                result = run_client_test(operation, 'localhost:6666', file_size, c_workers, s_type == 'process')

                if not result:
                    print(f"[FAILED] Test {test_id}")
                    writer.writerow({
                        'test_id': test_id,
                        'operation': operation,
                        'file_size_mb': file_size,
                        'client_workers': c_workers,
                        'server_type': s_type,
                        'server_workers': s_workers,
                        'total_time': 'ERROR',
                        'throughput_bytes_sec': 'ERROR',
                        'client_success': 0,
                        'client_failed': 0,
                        'server_status': 'ERROR'
                    })
                else:
                    writer.writerow({
                        'test_id': test_id,
                        'operation': operation,
                        'file_size_mb': file_size,
                        'client_workers': c_workers,
                        'server_type': s_type,
                        'server_workers': s_workers,
                        'total_time': result.get('total_time', 'N/A'),
                        'throughput_bytes_sec': result.get('throughput', 'N/A'),
                        'client_success': result.get('successful', 0),
                        'client_failed': result.get('failed', 0),
                        'server_status': 'OK' if server_proc.poll() is None else 'CRASHED'
                    })
            finally:
                server_proc.terminate()
                server_proc.wait()
                test_id += 1
                time.sleep(1)

if __name__ == '__main__':
    main()
