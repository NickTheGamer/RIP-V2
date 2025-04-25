import unittest
from RIP_daemon import Router


class TestLargeNetwork(unittest.TestCase):
    def setUp(self):
        self.router = Router(1, [], [])
        self.maxDiff = None

    def create_mesh_network(self):
        # Simulate a mesh network where every router is connected to every other router
        network = {}
        for i in range(1, 11):  # Use a smaller number of routers for simplicity
            network[f'Router{i}'] = {f'Router{j}': 1 for j in range(1, 11) if j != i}
        return network

    def create_star_network(self):
        # Simulate a star network with Router1 as the central hub
        network = {}
        for i in range(2, 11):
            network[f'Router1'] = {f'Router{i}': 1}
            network[f'Router{i}'] = {f'Router1': 1}
        return network

    def create_tree_network(self):
        # Simulate a tree network
        network = {
            'Router1': {'Router2': 1, 'Router3': 1},
            'Router2': {'Router4': 1, 'Router5': 1},
            'Router3': {'Router6': 1, 'Router7': 1},
            'Router4': {}, 'Router5': {}, 'Router6': {}, 'Router7': {}
        }
        return network

    def create_variable_cost_network(self):
        # Simulate a network with varying link costs
        network = {
            'Router1': {'Router2': 1, 'Router3': 5},
            'Router2': {'Router3': 1, 'Router4': 2},
            'Router3': {'Router4': 1},
            'Router4': {}
        }
        return network

    def create_cyclic_network(self):
        # Simulate a cyclic network
        network = {
            'Router1': {'Router2': 1, 'Router3': 1},
            'Router2': {'Router3': 1, 'Router4': 1},
            'Router3': {'Router4': 1, 'Router1': 1},
            'Router4': {}
        }
        return network

    def test_mesh_topology(self):
        self.routers = self.create_mesh_network()
        routes = [(i, j, 1) for i in range(1, 11) for j in range(1, 11) if i != j]
        self.router.calculate_routes(routes)
        print(f"Final routing table (Mesh): {self.router.routing_table}")

    def test_star_topology(self):
        self.routers = self.create_star_network()
        routes = [(1, i, 1) for i in range(2, 11)] + [(i, 1, 1) for i in range(2, 11)]
        self.router.calculate_routes(routes)
        print(f"Final routing table (Star): {self.router.routing_table}")

    def test_tree_topology(self):
        self.routers = self.create_tree_network()
        routes = [
            (1, 2, 1), (1, 3, 1),
            (2, 4, 1), (2, 5, 1),
            (3, 6, 1), (3, 7, 1)
        ]
        self.router.calculate_routes(routes)
        print(f"Final routing table (Tree): {self.router.routing_table}")

    def test_variable_costs(self):
        self.routers = self.create_variable_cost_network()
        routes = [
            (1, 2, 1), (1, 3, 5),
            (2, 3, 1), (2, 4, 2),
            (3, 4, 1)
        ]
        self.router.calculate_routes(routes)
        print(f"Final routing table (Variable Costs): {self.router.routing_table}")

    def test_cyclic_topology(self):
        self.routers = self.create_cyclic_network()
        routes = [
            (1, 2, 1), (1, 3, 1),
            (2, 3, 1), (2, 4, 1),
            (3, 4, 1), (3, 1, 1)
        ]
        self.router.calculate_routes(routes)
        print(f"Final routing table (Cyclic): {self.router.routing_table}")

    def test_link_failure(self):
        # Simulate a network with a link failure
        routes = [
            (1, 2, 1), (2, 3, 1), (3, 4, 1),  # Initial routes
        ]
        self.router.calculate_routes(routes)

        # Simulate a link failure between Router 2 and Router 3
        routes = [
            (1, 2, 1), (3, 4, 1),  # Remove the route (2, 3)
        ]
        self.router.calculate_routes(routes)

        # Assert that Router 3 is now unreachable
        self.assertEqual(self.router.routing_table.get(3), (16, None, False))
        print(f"Final routing table after link failure: {self.router.routing_table}")


if __name__ == '__main__':
    unittest.main()