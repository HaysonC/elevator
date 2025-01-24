import pickle
from collections.abc import Iterable
from typing import Literal

import neat

from elevatorConstants import DEFAULT_ELEVATOR_FLOOR
from floor import Floors
from obtainPassenger import TimeCapture
import matplotlib.pyplot as plt
from neat.checkpoint import Checkpointer

def convert_input(value):
    if value == "up":
        return 1
    elif value == "idle":
        return 0
    elif value == "down":
        return -1
    elif isinstance(value, bool):
        return float(value)
    else:
        return float(value)


def convert_output(value: list, elevator_locations: list[int]):
    outputs = []
    for i in range(len(elevator_locations)):
        if value[i] == 0:
            outputs.append("idle")
        elif value[i] > 0:
            outputs.append("up")
        elif value[i] < 0:
            outputs.append("down")
    for i in range(len(elevator_locations), len(value)):
        if value[i] > 0:
            outputs.append(True)
        else:
            outputs.append(False)
    return outputs


def plot_fitness(stats):
    generation = range(len(stats.most_fit_genomes))
    best_fitness = [c.fitness for c in stats.most_fit_genomes]
    avg_fitness = [c for c in stats.get_fitness_mean()]


    plt.figure(figsize=(10, 6))
    plt.plot(generation, best_fitness, label="Best Fitness")
    plt.plot(generation, avg_fitness, label="Average Fitness")

    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.title("Fitness over Generations")
    plt.legend()
    plt.grid()
    plt.show()


# Define the fitness function
def evaluate_genomes(genomes, config):
    """
    Evaluate the performance of each genome in the population.
    """
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        total_steps = 300  # Number of simulation steps
        total_runs = 3
        total_wait_time = 0
        for i in range(total_runs):
            floor_system = Floors(passengerGenerator=TimeCapture(DEFAULT_ELEVATOR_FLOOR))
            for _ in range(total_steps):
                # Get inputs for the NEAT network
                current_time = floor_system.time  # Get the current time
                elevator_locations = [convert_input(loc) for loc in floor_system.getElevatorLocation()]
                elevator_directions = [convert_input(dir) for dir in floor_system.getElevatorDirection()]
                floor_requests = floor_system.getFloorRequests()
                waiting_passengers = [len(floor) for floor in floor_system._floors]

                inputs = [convert_input(current_time)] + elevator_locations + elevator_directions + [convert_input(item) for sublist in floor_requests for item in sublist] + waiting_passengers
                # Get NEAT outputs
                outputs = convert_output(net.activate(inputs), elevator_locations)

                # Map outputs to actions (e.g., set directions, decide to pick up passengers)
                elevator_actions: list[Literal["up", "down", "idle"]] = outputs[:len(elevator_locations)]
                take_ins = outputs[len(elevator_locations):]

                # Update the elevator system with the actions
                floor_system.setElevatorDirection(elevator_actions)
                floor_system.setTakeIns(take_ins)

                # Simulate the next time step
                wait_time = floor_system.next()
            total_wait_time += wait_time
        # Assign fitness score to the genome
        genome.fitness = -total_wait_time
    # store the curr best in temp.pkl



# Configure the NEAT algorithm
def run_neat():
    """
    Set up and run the NEAT algorithm.
    """
    # Initialize the floor system to determine dynamic input/output sizes
    floor_system = Floors()
    num_elevators = len(floor_system.getElevatorLocation())
    num_floors = len(floor_system._floors)

    # Calculate the number of inputs and outputs dynamically
    num_inputs = 1 + (2 * num_elevators) + (2 * num_floors) + num_floors  # time + elevator states + floor requests + waiting passengers
    num_outputs = num_elevators * 2  # Directions and take-in actions for each elevator

    # Dynamically update the NEAT configuration under [DefaultGenome]
    with open("neat_config", "r") as f:
        config_data = f.readlines()

    default_genome_index = None
    for i, line in enumerate(config_data):
        if line.strip() == "[DefaultGenome]":
            default_genome_index = i
            break

    if default_genome_index is None:
        raise RuntimeError("[DefaultGenome] section is missing in the NEAT config file.")

    # Check for num_inputs, num_outputs, and add num_hidden
    num_inputs_exists = any("num_inputs" in line for line in config_data[default_genome_index:])
    num_outputs_exists = any("num_outputs" in line for line in config_data[default_genome_index:])

    with open("neat_config", "w") as f:
        for i, line in enumerate(config_data):
            if i == default_genome_index:
                f.write(line)  # Write [DefaultGenome] header
                if not num_inputs_exists:
                    f.write(f"num_inputs              = {num_inputs}\n")
                if not num_outputs_exists:
                    f.write(f"num_outputs             = {num_outputs}\n")
            else:
                f.write(line)

    config_path = "neat_config"
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    do_restore: bool = False
    i = input("Do you want to restore the last best genome? (y/n): ")
    if i == "y":
        do_restore = True
    else:
        do_restore = False
    if do_restore:
        # find the last temp file
        # load the genome

        # list all temp files
        import os
        temp_files = []
        for file in os.listdir():
            if file.startswith("temp"):
                temp_files.append(file)
        temp_files.sort(key=lambda x: int(b if (b := x.split("temp")[1].split(".")[0] != "") else 0))
        if len(temp_files) == 0:
            print("No temp files found")
            return
        last_temp_file = temp_files[-1]
        print("Restoring from", last_temp_file)
        pop = Checkpointer.restore_checkpoint(last_temp_file)
        population = pop
    else:
        population = neat.Population(config, initial_state=None)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    checkpointer = Checkpointer(generation_interval=4, time_interval_seconds=None, filename_prefix="temp")
    population.add_reporter(checkpointer)

    # Run the NEAT algorithm
    winner = population.run(evaluate_genomes, n=700)

    # Display the best genome
    print("\nBest genome:\n", winner)

    # Save the winner for later use
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)

    # Plot the fitness over generations
    plot_fitness(stats)

# Run the training
if __name__ == "__main__":
    run_neat()