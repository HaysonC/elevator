from typing import Literal, Iterable

from passenger import Passenger

from elevatorConstants import DEFAULT_ELEVATOR_CAPACITY, UNLOADING_TIME, DEFAULT_ELEVATOR_FLOOR


class Elevator(set[Passenger]):
    def __init__(self,
                 capacity: int = DEFAULT_ELEVATOR_CAPACITY,
                 max_floor: int = DEFAULT_ELEVATOR_FLOOR) -> None:
        """
        Initialize the elevator

        :param capacity: The capacity of the elevator
        :param max_floor: The maximum floor number
        """
        super().__init__()
        self.capacity: int = capacity
        self.elevator_direction: str = "idle"
        self.current_floor: int = 0
        self.holdingTime: int = 0
        self.max_floor: int = max_floor

    def set_direction(self, direction: Literal["up", "down", "idle"]) -> None:
        """
        Set the direction of the elevator

        :param direction: str: "up",  "down" or "idle"
        :return: None
        """
        self.elevator_direction = direction

    def add_passenger(self, passenger: Passenger) -> bool:
        """
        Add passenger to the elevator

        :param passenger: Passenger object
        :return: bool: True if passenger is added, else False
        """
        if len(self) < self.capacity:
            if self.elevator_direction ==  passenger.press():
                self.add(passenger)
            return True
        return False

    def add_passengers(self, passengers_floor: set[Passenger]) -> None:
        """
        Add passengers to the elevator

        :param passengers_floor: list of Passenger objects
        :return: None
        """
        passengers_to_remove = []
        for passenger in passengers_floor:
            if self.add_passenger(passenger):
                passengers_to_remove.append(passenger)

        for passenger in passengers_to_remove:
            passengers_floor.remove(passenger)

        self.holdingTime += UNLOADING_TIME

    def get_internal_requests(self) -> set:
        """
        Get the internal requests of the elevator

        :return: set of floor numbers
        """
        for passenger in self:
            yield passenger.destination

    def next(self):
        """
        Drop off passengers or move to the next floor
        Add wait for passengers

        :return: str: total wait time of passengers
        """
        for passenger in self:
            passenger.wait()
        if self.holdingTime > 0:
            self.holdingTime -= 1
            return
        if self.elevator_direction == "up" and self.current_floor < self.max_floor - 1:
            self.current_floor += 1
        elif self.elevator_direction == "down" and self.current_floor > 0:
            self.current_floor -= 1
        doContinue = True
        for passenger in list(self):
            if passenger.destination == self.current_floor:
                self.remove(passenger)
                doContinue = False
        if not doContinue:
            self.holdingTime = UNLOADING_TIME
