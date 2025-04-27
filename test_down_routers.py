import unittest
import time
import RIP_daemon as RIP

# filepath: /home/noah-davis/Documents/2025/COSC364/RIP assignment/cosc364-assignment-1/test_RIP_daemon.py

class TestRouterDownAndRecovery(unittest.TestCase):
    def setUp(self):
        # Initialize a router with ID 1, input ports, and output ports
        self.router = RIP.Router(1, [5000], ["5001-1-2", "5002-1-3"])
        self.router2_id = 2
        self.router3_id = 3

    def test_router_down_and_recovery(self):
        # Step 1: Use calculate_routes to initialize the routing table with routes from Router 2 and Router 3
        initial_routes = [
            (self.router2_id, 4, 5001, 1),  # Route to destination 4 via Router 2
            (self.router3_id, 5, 5002, 1),  # Route to destination 5 via Router 3
        ]
        self.router.calculate_routes(initial_routes)

        # Assert the routes are added
        self.assertIn(4, self.router.routing_table)
        self.assertIn(5, self.router.routing_table)
        self.assertTrue(self.router.routing_table[4][2])  # Route to 4 is valid
        self.assertTrue(self.router.routing_table[5][2])  # Route to 5 is valid

        # Step 2: Simulate Router 2 going down
        self.router.routing_table[4] = (1, (self.router2_id, 5001), False)  # Mark route as invalid
        self.router.route_timers[self.router2_id] = time.time() - RIP.ROUTE_TIMEOUT - 1  # Simulate timeout
        self.router.update_timers()

        # Assert the route to destination 4 is invalid
        self.assertFalse(self.router.routing_table[4][2])  # Route to 4 is invalid
        # Step 3: Simulate Router 2 coming back online
        recovery_routes = [
            (self.router2_id, 4, 5001, 1),  # Route to destination 4 via Router 2
        ]
        self.router.calculate_routes(recovery_routes)

        # Assert the route to destination 4 is valid again
        self.assertIn(4, self.router.routing_table)
        self.assertTrue(self.router.routing_table[4][2])  # Route to 4 is valid


    def test_split_horizon_with_poison_reverse(self):
        # Directly initialize the routing table with a valid route to destination 4 via Router 2
        self.router.routing_table = {
            4: (1, (self.router2_id, 5001), True)  # Cost 1, next hop Router 2, route is valid
        }

        # Construct a packet for Router 2 and check poison reverse
        packet = self.router.construct_packet(self.router2_id)

        # Assert the packet contains the poisoned route to destination 4
        self.assertIn((4).to_bytes(4, 'big'), packet)  # Destination ID 4
        self.assertIn((16).to_bytes(4, 'big'), packet)  # Poisoned cost 16

    def test_garbage_collection(self):
        # Simulate a route to Router 4 via Router 2
        self.router.calculate_routes([(self.router2_id, 4, 1, 1)])  # Add cost as the fourth element

        # Mark the route as invalid
        self.router.routing_table[4] = (1, (self.router2_id, 5001), False)
        self.router.garbage_timers[4] = time.time()

        # Wait for garbage collection interval
        time.sleep(RIP.GARBAGE_COLLECTION_INTERVAL + 1)
        self.router.update_timers()

        # Assert the route is removed
        self.assertNotIn(4, self.router.routing_table)

if __name__ == "__main__":
    unittest.main()