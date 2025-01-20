from collections.abc import Iterable
from typing import Literal

import neat
from floor import Floors

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



# Define the fitness function
def evaluate_genomes(genomes, config):
    """
    Evaluate the performance of each genome in the population.
    """
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        floor_system = Floors()  # Initialize the floors system
        total_steps = 300  # Number of simulation steps
        total_wait_time = 0  # Track cumulative wait time

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
            floor_system.setDropOffs(take_ins)

            # Simulate the next time step
            total_wait_time += floor_system.next()
        # Assign fitness score to the genome
        genome.fitness = -total_wait_time
    # store the curr best in temp.pkl
    current_best = max(genomes, key=lambda x: x[1].fitness)
    with open("temp.pkl", "wb") as f:
        import pickle
        pickle.dump(current_best, f)
    print("Current best genome:", current_best)

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

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run the NEAT algorithm
    winner = population.run(evaluate_genomes, n=100)

    # Display the best genome
    print("\nBest genome:\n", winner)

    # Save the winner for later use
    with open("winner.pkl", "wb") as f:
        import pickle
        pickle.dump(winner, f)

# Run the training
if __name__ == "__main__":
    run_neat()