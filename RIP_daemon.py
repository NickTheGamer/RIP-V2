import sys
from socket import socket, AF_INET, SOCK_DGRAM

def read_config_file(filename):
    config = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            parts = line.split()
            if not parts:
                continue  
            
            if parts[0] == "router-id":
                config['router-id'] = parts[1]  
            elif parts[0] == "input-ports":
                config['input-ports'] = [int(port) for port in parts[1:]]
    return config

def instantiate_ports(input_ports):
    ports = []
    for port in input_ports:
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(('', port))
        ports.append(sock)
    return ports

def main():
    if len(sys.argv) != 2:
        sys.exit(1)
    
    config_file = sys.argv[1]
    config = read_config_file(config_file)
    
    router_id = config.get('router-id', "Not specified")
    input_ports = config.get('input-ports', [])

    open_ports = instantiate_ports(input_ports)
    
    print(f"Router ID: {router_id}")
    print(f"Input Ports: {input_ports}")
    print(f"Open Ports: {open_ports}")

if __name__ == "__main__":
    main()
