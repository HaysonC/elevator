# Upon request to obtain, it generates a passenger from certain rules. Return the passenger objects for the
# floor to register.
from elevatorConstants import DEFAULT_BUSY_MULTIPLIER
from passenger import Passenger

from random import randint


class PassengerGenerator(object):
    def __init__(self,
                 floorCount: int,
                 busyMultiplier: int = DEFAULT_BUSY_MULTIPLIER):
        self.floorCount: int = floorCount
        self.busyMultiplier: float = busyMultiplier

    def obtain(self) -> list[Passenger]:
        raise NotImplementedError("This method must be implemented in a subclass")


class RandomPassengerGenerator(PassengerGenerator):
    def obtain(self) -> list[Passenger]:
        passengers: list[Passenger] = []
        for _ in range(int(round(self.busyMultiplier * self.floorCount))):
            origin = randint(0, self.floorCount - 1)
            destination = randint(0, self.floorCount - 1)
            while origin == destination:
                destination = randint(0, self.floorCount - 1)
            passengers.append(Passenger(origin, destination))
        return passengers