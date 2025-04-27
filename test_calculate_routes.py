import unittest
import time
from RIP_daemon import Router, ROUTE_TIMEOUT, GARBAGE_COLLECTION_INTERVAL

# filepath: /home/noah-davis/Documents/2025/COSC364/RIP assignment/cosc364-assignment-1/test_RIP_daemon.py


class TestCalculateRoutes(unittest.TestCase):
    def setUp(self):
        # Initialize a router with ID 1, input ports, and output ports
        self.router = Router(1, [5000], ["5001-1-2", "5002-1-3"])
        self.router2_id = 2
        self.router3_id = 3

    def test_add_new_routes(self):
        # Add new routes to the routing table
        routes = [
            (self.router2_id, 4, 5001, 1),  # Route to destination 4 via Router 2
            (self.router3_id, 5, 5002, 1),  # Route to destination 5 via Router 3
        ]
        self.router.calculate_routes(routes)

        # Assert the routes are added
        self.assertIn(4, self.router.routing_table)
        self.assertIn(5, self.router.routing_table)
        self.assertEqual(self.router.routing_table[4][0], 2)  # Cost = 1 (to Router 2) + 1
        self.assertEqual(self.router.routing_table[5][0], 2)  # Cost = 1 (to Router 3) + 1

    def test_update_existing_routes(self):
        # Add initial routes
        initial_routes = [
            (self.router2_id, 4, 5001, 5),  # Route to destination 4 via Router 2 with cost 5
        ]
        self.router.calculate_routes(initial_routes)

        # Update the route with a lower cost
        updated_routes = [
            (self.router2_id, 4, 5001, 2),  # Route to destination 4 via Router 2 with cost 2
        ]
        self.router.calculate_routes(updated_routes)

        # Assert the route is updated with the lower cost
        self.assertEqual(self.router.routing_table[4][0], 3)  # Cost = 1 (to Router 2) + 2

    


if __name__ == "__main__":
    unittest.main()