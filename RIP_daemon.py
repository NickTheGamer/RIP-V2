import sys
from socket import socket, AF_INET, SOCK_DGRAM


global routers
routers = []

class Router:
    
    def __init__(self, id, input_ports, output_ports):
        self.id = id
        self.input_ports = input_ports
        self.output_ports = output_ports
        self.routing_table = {}
        self.check_constraints()
        self.instantiate_ports()
        self.convert_output_ports()

    def __str__(self):
        return f'Router ID: {self.id}\n' \
            f'Input Ports: {self.input_ports}\n' \
            f'Output Ports: {self.output_ports}\n'
    
    def instantiate_ports(self):
        for port in self.input_ports:
            sock = socket(AF_INET, SOCK_DGRAM)
            sock.bind(('', port))

    def check_constraints(self):
        if self.id < 1 or self.id > 64000:
            raise Exception("Router-id must be between 1 and 64000 (inclusive).")
        for input in self.input_ports:
            if input < 1024 or input > 64000:
                raise Exception("Port numbers must be between 1024 and 64000 (inclusive).")
        for output in self.output_ports:
            output = output.split('-')
            port = int(output[0])
            if port < 1024 or port > 64000:
                raise Exception("Port numbers must be between 1024 and 64000 (inclusive).")
            
    def convert_output_ports(self):
        self.output_ports = [tuple(map(int, output.split('-'))) for output in self.output_ports]

    def RIPv2(self):
        pass


def read_config_file(filename):
    routers_config = []
    current_router = {}

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                if current_router:
                    routers_config.append(current_router)
                    current_router = {}
                continue

            parts = line.split()
            if not parts:
                continue

            key = parts[0].lower().replace('_', '-')
            values = parts[1:]

            if key == 'router-id':
                current_router['router-id'] = int(values[0])
            elif key == 'input-ports':
                current_router['input-ports'] = list(map(int, values))
            elif key == 'output-ports':
                current_router['output-ports'] = values

        if current_router:
            routers_config.append(current_router)

    return routers_config


def routing_loop():
    for router in routers:
        router.RIPv2


def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    config_file = sys.argv[1]
    routers_config = read_config_file(config_file)

    for config in routers_config:
        router_id = config.get('router-id')
        input_ports = config.get('input-ports', [])
        output_ports = config.get('output-ports', [])
        routers.append(Router(router_id, input_ports, output_ports))

    for router in routers:
        print(router)

    #while True:
    #    routing_loop()


if __name__ == "__main__":
    main()
