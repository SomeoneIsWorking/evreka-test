import socket
import json

def test_tcp_server_multiple_clients():
    clients = []
    test_data_list = []
    
    # Create and connect multiple clients
    for i in range(3):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 5500))
        clients.append(client)
        
        data = {
            "device_id": f"test_device_{i}",
            "latitude": 41.0082 + i,
            "longitude": 28.9784 + i,
            "speed": 20.5 + i
        }
        test_data_list.append(data)
        client.send(json.dumps(data).encode())
    
    # Cleanup
    for client in clients:
        client.close()