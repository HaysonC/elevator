from typing import Union, Literal

from elevator import Elevator
from obtainPassenger import PassengerGenerator, RandomPassengerGenerator
from passenger import Passenger

from elevatorConstants import DEFAULT_ELEVATOR_FLOOR, DEFAULT_ELEVATOR_COUNT, DEFAULT_ELEVATOR_CAPACITY


class Floors(object):
    def __init__(self,
                 passengerGenerator: Union[PassengerGenerator, None] = None,
                 elevatorCount: int = DEFAULT_ELEVATOR_COUNT,
                 floorCount: int = DEFAULT_ELEVATOR_FLOOR,
                 elevatorCapacity: int = DEFAULT_ELEVATOR_CAPACITY
                 ) -> None:
        """
        Initialize the floors

        :param passengerGenerator: PassengerGenerator object to generate passengers according to rules
        :param elevatorCount: Elevator count
        :param floorCount: Floor count
        :param elevatorCapacity: Elevator capacity
        """
        self.time: int = 0
        self._floors: list[set[Passenger]] = [set() for _ in range(floorCount)]
        self._elevators: list[Elevator] = [Elevator(elevatorCapacity, floorCount) for _ in range(elevatorCount)]
        self.takeIns: list[bool] = [False for _ in range(elevatorCount)]
        self.floorRequests: list[tuple[bool, bool]] = [(False, False) for _ in range(floorCount)]
        self.updateFloor(0)

        if passengerGenerator is None:
            self.passengerGenerator = RandomPassengerGenerator(floorCount)
        else:
            self.passengerGenerator = passengerGenerator

    def setDropOffs(self, takeIns: list[bool]) -> None:
        """
        Set the take in status of the elevators

        :param takeIns: list[bool]
        :return: None
        """
        self.takeIns = takeIns


    def setElevatorDirection(self, directions: list[Literal["up", "down", "idle"]]) -> None:
        """
        Set the direction of the elevators

        :param directions: list[str]
        :return: None
        """
        for i, direction in enumerate(directions):
            self._elevators[i].set_direction(direction)

    def getElevatorLocation(self) -> list[int]:
        """
        Get the location of the elevators

        :return: list[int]
        """
        return [elevator.current_floor for elevator in self._elevators]

    def getElevatorDirection(self) -> list[str]:
        """
        Get the direction of the elevators

        :return: list[str]
        """
        return [elevator.elevator_direction for elevator in self._elevators]

    def getFloorRequests(self) -> list[tuple[bool, bool]]:
        """
        Get the floor requests

        :return: list[tuple[bool, bool]]
        """
        return self.floorRequests

    def getInternalRequests(self) -> list[set[int]]:
        """
        Get the internal requests of the elevators

        :return: list[set[Passenger]]
        """
        return [elevator.get_internal_requests() for elevator in self._elevators]

    def updateFloor(self, wait: int = 1) -> int:
        """
        Update the floor requests for each floor and wait time of passengers

        :return: total wait time of passengers on the floor
        """
        waitTime = 0
        for floor in self._floors:
            for passenger in floor:
                passenger.wait(wait)
                waitTime += passenger.wait_time
        for i, floor in enumerate(self._floors):
            up = False
            down = False
            for passenger in floor:
                if passenger.press() == "up":
                    up = True
                else:
                    down = True
                if up and down:
                    break
            self.floorRequests[i] = (up, down)
        return waitTime

    def next(self) -> int:
        """
        The next time step

        updates (in order):

            UPDATE (INTERNAL):
            - generate passengers (1)
            - elevator next (3)
            - update floor (4)


            UPDATE (EXTERNAL):
            - elevator take in (2)
            - set direction (5)

        :return: int: total wait time of passengers if any is dropped off, else 0
        """
        # generate passengers
        passengers = self.passengerGenerator.obtain()
        for passenger in passengers:
            self._floors[passenger.origin].add(passenger)

        # elevator take in
        for i, elevator in enumerate(self._elevators):
            if self.takeIns[i]:
                elevator.add_passengers(self._floors[elevator.current_floor])

        # elevator next
        waitTime = 0
        for elevator in self._elevators:
            waitTime += elevator.next()

        # update floor
        floor_time = self.updateFloor()

        waitTime += floor_time

        self.time += 1
        return waitTime




