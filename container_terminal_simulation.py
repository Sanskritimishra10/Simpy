import simpy
import random

# Constants
AVG_VESSEL_ARRIVAL = 5 * 60  # average time between vessel arrivals in minutes
CONTAINERS_PER_VESSEL = 150
CRANE_TIME_PER_CONTAINER = 3  # minutes
TRUCK_TIME_PER_TRIP = 6  # minutes
SIMULATION_TIME = 10000  # total simulation time in minutes

# Container Terminal Simulation
class ContainerTerminal:
    def __init__(self, env):
        self.env = env
        self.berths = simpy.Resource(env, 2)
        self.cranes = simpy.Resource(env, 2)
        self.trucks = simpy.Resource(env, 3)

    def vessel_arrival(self):
        while True:
            # Time between vessel arrivals
            yield self.env.timeout(random.expovariate(1.0 / AVG_VESSEL_ARRIVAL))
            self.env.process(self.handle_vessel())

    def handle_vessel(self):
        arrival_time = self.env.now
        print(f'Vessel arrived at {arrival_time}')

        berth_request = self.berths.request()
        yield berth_request
        berth_time = self.env.now
        print(f'Vessel started berthing at {berth_time}')

        # Unloading containers
        crane_request = self.cranes.request()
        yield crane_request
        for _ in range(CONTAINERS_PER_VESSEL):
            yield self.env.timeout(CRANE_TIME_PER_CONTAINER)
            print(f'Crane moved container at {self.env.now}')
            
            truck_request = self.trucks.request()
            yield truck_request
            yield self.env.timeout(TRUCK_TIME_PER_TRIP)
            print(f'Truck moved container to yard at {self.env.now}')
            self.trucks.release(truck_request)
        
        self.cranes.release(crane_request)
        self.berths.release(berth_request)
        print(f'Vessel finished unloading and left at {self.env.now}')

# Set up and run the simulation
env = simpy.Environment()
terminal = ContainerTerminal(env)
env.process(terminal.vessel_arrival())
env.run(until=SIMULATION_TIME)

