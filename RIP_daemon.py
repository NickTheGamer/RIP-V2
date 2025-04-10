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
        self.initialise_routing_table()

    def __str__(self):
        return f'Router ID: {self.id}\n' \
            f'Input Ports: {self.input_ports}\n' \
            f'Output Ports: {self.output_ports}\n'
    
    def display_routing_table(self):
        print('--------------------------------')
        print(f'Router: {self.id}')
        for entry in self.routing_table.keys():
            print(f'Destination: {entry} Cost: {self.routing_table[entry][0]}, Next hop: {self.routing_table[entry][1][0]}')
        print('--------------------------------')


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

    def initialise_routing_table(self):
        for output in self.output_ports:
            self.routing_table[output[2]] = (output[1], (output[2], output[0]))


    def construct_packet(self):
        packet = bytearray()

        packet.append(2) #COMMAND: reponse
        packet.append(2) #Version: 2
        packet += self.id.to_bytes(2, 'big') #Router-ID in place of zero-byte field

        for entry in self.routing_table.keys():
            cost = self.routing_table[entry][0]
            dest_id = self.routing_table[entry][1][0]
            next_hop = self.routing_table[entry][1][0]

            if next_hop == self.id: #split-horizon with poison reverse
                cost = 16

            packet += (2).to_bytes(2, 'big') #address family identifier
            packet += (0).to_bytes(2, 'big') #Route tag (set to 0)
            packet += dest_id.to_bytes(4, 'big')
            packet += bytes(4) #Subnet mask not used
            packet += next_hop.to_bytes(4, 'big')
            packet += cost.to_bytes(4, 'big')

        return packet


    def decode_packet(self, packet):
        if packet[0] != 2: #Check Command field
            print('Invalid packet header, Command incorrect. Packet dropped')
            return
        if packet[1] != 2: #Check version field
            print('Invalid packet header, version is not 2. Packet dropped')
            return
        
        sender_id = int.from_bytes(packet[2:4], 'big') #Check sender ID constraints
        if sender_id < 1 or sender_id > 64000:
            print("Invalid Router ID. Packet dropped.")
            return
        else: #Check sender is actually neighbour (in output ports)
            valid_id = False
            for output in self.output_ports:
                if output[2] == sender_id:
                    valid_id = True
        if not valid_id:
            print('Router is not a neighbour. Packet dropped.')
            return
        
        index = 4 #Now we iterate over the rest of the packet to extract RIP entries
        routes = []
        while index < len(packet):
            if int.from_bytes(packet[index:index+2], 'big') != 2:
                print("Invalid RIPv2 entry with incorrect Addr Family. Packet dropped.")
                return
            index += 2

            if int.from_bytes(packet[index:index+2], 'big') != 0:
                print("Invalid RIPv2 entry with Route Tag. Packet dropped.")
                return
            index += 2

            dest_id = int.from_bytes(packet[index:index+4], 'big')
            if dest_id < 1 or dest_id > 64000:
                print('Invalid RIPv2 entry with invalid Destination ID. Packet dropped.')
                return
            index += 4

            if int.from_bytes(packet[index:index+4], 'big') != 0:
                print('Invalid RIPv2 entry, Subnet mask should be 0. Packet dropped.')
                return
            index += 4

            next_hop = int.from_bytes(packet[index:index+4], 'big')
            if next_hop < 1 or next_hop > 64000:
                print('Invalid RIPv2 entry with invalid next hop. Packet dropped.')
                return
            index += 4

            cost = int.from_bytes(packet[index:index+4], 'big')
            if cost < 1 or cost > 16:
                print('Invalid RIPv2 entry with invalid cost. Packet dropped.')
                return
            index += 4

            routes.append((sender_id, dest_id, cost))

        return routes


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
    pass
    #while True:
    #    ---------


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

    routing_loop()


if __name__ == "__main__":
    main()
