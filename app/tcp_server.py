import socket
import json
import pika
import logging
from threading import Thread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TCPServer:
    def __init__(self, host='0.0.0.0', port=5500):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        
        # RabbitMQ connection
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='location_data')
        
        logger.info(f"TCP Server started on {host}:{port}")

    def handle_client(self, client_socket: socket.socket):
        client_address = client_socket.getpeername()
        logger.info(f"New connection from {client_address}")
        
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                location_data = json.loads(data.decode())
                self.channel.basic_publish(
                    exchange='',
                    routing_key='location_data',
                    body=json.dumps(location_data)
                )
                logger.info(f"Received and published data from {client_address}")
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from {client_address}")
            except Exception as e:
                logger.error(f"Error handling client {client_address}: {str(e)}")
                break
        
        logger.info(f"Client {client_address} disconnected")
        client_socket.close()

    def start(self):
        while True:
            client, _ = self.server.accept()
            thread = Thread(target=self.handle_client, args=(client,))
            thread.start()

if __name__ == "__main__":
    server = TCPServer()
    server.start()
