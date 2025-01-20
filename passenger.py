from typing import Literal


class Passenger(object):
    def __init__(self,
                 origin,
                 destination) -> None:
        self.origin: int = origin
        self.destination: int = destination
        self.wait_time: int = 0
        if self.origin == self.destination:
            print("\33[31mWarning: origin and destination are the same")
            print("This passenger will not be created\33[0m")
            del self

    def press(self) -> Literal["up", "down"]:
        if self.origin < self.destination:
            return "up"
        else:
            return "down"

    def wait(self, time: int = 1) -> None:
        self.wait_time += time

    def get_wait_time(self) -> int:
        return self.wait_time

    def __str__(self):
        return f'Passenger from {self.origin} to {self.destination}'
