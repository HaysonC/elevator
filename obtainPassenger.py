from elevatorConstants import DEFAULT_BUSY_MULTIPLIER, RANDOM_SEED
from passenger import Passenger

import random

class PassengerGenerator(object):
    def __init__(self,
                 floorCount: int,
                 busyMultiplier: int = DEFAULT_BUSY_MULTIPLIER,
                 seed: int = RANDOM_SEED) -> None:
        self.floorCount: int = floorCount
        self.busyMultiplier: float = busyMultiplier

        self.seed: int = RANDOM_SEED

    def obtain(self, *args)-> list[Passenger]:
        raise NotImplementedError("This method must be implemented in a subclass")


class RandomPassengerGenerator(PassengerGenerator):
    def obtain(self, *args) -> list[Passenger]:
        passengers: list[Passenger] = []
        for _ in range(int(round(self.busyMultiplier * self.floorCount))):
            origin = random.randint(0, self.floorCount - 1)
            destination = random.randint(0, self.floorCount - 1)
            while origin == destination:
                destination = random.randint(0, self.floorCount - 1)
            passengers.append(Passenger(origin, destination))
        return passengers



class TimeCapture(PassengerGenerator):
    def obtain(self, time: int) -> list[Passenger]:
        passengers: list[Passenger] = []
        if time % 50 in range(45, 55):
            # More passengers from 3rd floor to 1st floor
            for _ in range(int(round(self.busyMultiplier * 5))):
                passengers.append(Passenger(3, 1))
        else:
            for _ in range(int(round(self.busyMultiplier * self.floorCount))):
                origin = random.randint(0, self.floorCount - 1)
                destination = random.randint(0, self.floorCount - 1)
                while origin == destination:
                    destination = random.randint(0, self.floorCount - 1)
                passengers.append(Passenger(origin, destination))
        return passengers
