"""
Autor: Pablo Sanchez Rico
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = 1
NORTH = 0

NCARS = 30
NPED = 5
TIME_CARS_NORTH = 0.5  # a new car enters each 0.5s
TIME_CARS_SOUTH = 0.5  # a new car enters each 0.5s
TIME_PED = 5 # a new pedestrian enters each 5s
TIME_IN_BRIDGE_CARS = (1, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRIAN = (30, 10) # normal 1s, 0.5s

class Monitor():
    
    def __init__(self):
        self.mutex = Lock()
        self.Wcar_north = Value('i', 0)
        self.Wcar_south = Value('i', 0)
        self.inside_north = Value('i', 0)
        self.inside_south = Value('i', 0)
        self.Wpedestrian = Value('i', 0)
        self.inside_pedestrian = Value('i', 0)
        self.open_south = Condition(self.mutex)
        self.open_north = Condition(self.mutex)
        self.open_pedestrian = Condition(self.mutex)

    def no_cars_north(self):
        return self.inside_north.value == 0
        
    def no_cars_south(self):
        return self.inside_south.value == 0
        
    def no_pedestrian(self):
        return self.inside_pedestrian.value == 0

    def wants_enter_car(self, direction: int) -> None:
        self.mutex.acquire()
        if direction == SOUTH:
            self.Wcar_south.value += 1
            self.open_south.wait_for(self.no_cars_north) and self.open_south.wait_for(self.no_pedestrian)
            self.inside_south.value += 1
            self.Wcar_south.value -= 1
        if direction==NORTH:
            self.Wcar_north.value += 1
            self.open_north.wait_for(self.no_cars_south) and self.open_north.wait_for(self.no_pedestrian)
            self.inside_north.value += 1
            self.Wcar_north.value -= 1
        self.mutex.release()

    def leaves_car(self, direction: int) -> None:
        self.mutex.acquire()
        if direction == SOUTH:
            self.inside_south.value -= 1
            if self.no_cars_south:
                self.open_north.notify_all()
        if direction == NORTH:
            self.inside_north.value -= 1
            if self.no_cars_north:
                self.open_pedestrian.notify_all()
        self.mutex.release()

    def wants_enter_pedestrian(self) -> None:
        self.mutex.acquire()
        self.Wpedestrian.value += 1        
        self.open_pedestrian.wait_for(self.no_cars_north) and self.open_pedestrian.wait_for(self.no_cars_south)
        self.inside_pedestrian.value += 1
        self.Wpedestrian.value -= 1
        self.mutex.release()
        
    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()
        self.inside_pedestrian.value -= 1
        if self.no_pedestrian:
            self.open_south.notify_all()
        self.mutex.release()
         

    def __repr__(self) -> str:
        return f'Monitor: {self.inside_north.value}, {self.inside_south.value}, {self.inside_pedestrian.value}' 


def delay_car_north() -> None:
    delay_time=random.uniform(*TIME_IN_BRIDGE_CARS)
    print(f"car heading north entering bridge delay {delay_time} s.")
    time.sleep(delay_time)
    
def delay_car_south() -> None:
    delay_time=random.uniform(*TIME_IN_BRIDGE_CARS)
    print(f"car heading south entering bridge delay {delay_time} s.")
    time.sleep(delay_time)

def delay_pedestrian() -> None:
    delay_time=random.uniform(*TIME_IN_BRIDGE_CARS)
    print(f"pedestrian entering bridge delay {delay_time} s.")
    time.sleep(delay_time)


def car(cid: int, direction: int, monitor: Monitor)  -> None:
    print(f"car {cid} heading {direction} wants to enter. {monitor}")
    monitor.wants_enter_car(direction)
    print(f"car {cid} heading {direction} enters the bridge. {monitor}")
    if direction==NORTH :
        delay_car_north()
    else:
        delay_car_south()
    print(f"car {cid} heading {direction} leaving the bridge. {monitor}")
    monitor.leaves_car(direction)
    print(f"car {cid} heading {direction} out of the bridge. {monitor}")

def pedestrian(pid: int, monitor: Monitor) -> None:
    print(f"pedestrian {pid} wants to enter. {monitor}")
    monitor.wants_enter_pedestrian()
    print(f"pedestrian {pid} enters the bridge. {monitor}")
    delay_pedestrian()
    print(f"pedestrian {pid} leaving the bridge. {monitor}")
    monitor.leaves_pedestrian()
    print(f"pedestrian {pid} out of the bridge. {monitor}")


def gen_pedestrian(monitor: Monitor) -> None:
    pid = 0
    plst = []
    for _ in range(NPED):
        pid += 1
        p = Process(target=pedestrian, args=(pid, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_PED))
    for p in plst:
        p.join()

def gen_cars(direction: int, time_cars, monitor: Monitor) -> None:
    cid = 0
    plst = []
    for _ in range(NCARS):
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/time_cars))
    for p in plst:
        p.join()


def main():
    monitor = Monitor()
    gcars_north = Process(target=gen_cars, args=(NORTH, TIME_CARS_NORTH, monitor))
    gcars_south = Process(target=gen_cars, args=(SOUTH, TIME_CARS_SOUTH, monitor))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    gcars_north.start()
    gcars_south.start()
    gped.start()
    gcars_north.join()
    gcars_south.join()
    gped.join()


if __name__ == '__main__':
    main()
