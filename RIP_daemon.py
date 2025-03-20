import sys

def read_config_file(filename):
    config = {}
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            parts = line.split()
            if not parts:
                continue  # Skip empty lines
            
            if parts[0] == "router-id":
                config['router-id'] = parts[1]  
            elif parts[0] == "input-ports":
                config['input-ports'] = [int(port) for port in parts[1:]] 
    return config

def main():
    if len(sys.argv) != 2:
        print("Usage: python RIP_daemon.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    config = read_config_file(config_file)
    
    router_id = config.get('router-id', "Not specified")
    input_ports = config.get('input-ports', [])
    
    print(f"Router ID: {router_id}")
    print(f"Input Ports: {input_ports}")

if __name__ == "__main__":
    main()
