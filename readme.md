# Elevator Optimization with NEAT

## Project Overview

This project aims to optimize the operation of a multi-elevator system using the NEAT (NeuroEvolution of Augmenting Topologies) algorithm. The goal is to minimize the total wait time for passengers by evolving neural networks that control the elevators' movements and decisions.

## Background on NEAT

NEAT is a genetic algorithm that evolves neural networks. It starts with simple networks and gradually increases their complexity by adding new nodes and connections through mutations. NEAT maintains a balance between exploring new structures and optimizing existing ones, making it effective for complex tasks like controlling multiple elevators.

## Elevator Optimization Goal

The primary objective of this project is to develop a neural network that can efficiently manage a system of elevators. The network should:

- Minimize the total wait time for passengers.
- Make decisions on elevator directions and passenger pickups.
- Adapt to varying passenger demands and floor requests.

## NEAT Configuration

The NEAT configuration is defined in the `neat_config` file. This file includes parameters such as population size, mutation rates, and network structure. Key sections in the configuration file include:

- **\[DefaultGenome\]**: Defines the structure of the genomes, including the number of inputs, outputs, and hidden nodes.
- **\[DefaultReproduction\]**: Parameters for the reproduction process.
- **\[DefaultSpeciesSet\]**: Parameters for species management.
- **\[DefaultStagnation\]**: Parameters for handling stagnation in the population.

### Example Configuration

```ini
[DefaultGenome]
num_inputs              = 129
num_outputs             = 8
num_hidden              = 0
...
```

## Running the Simulation
To run the NEAT algorithm and train the elevator control system, execute the train_neat.py script. This script initializes the NEAT population, runs the evolution process, and saves the best genome.
```
python train_neat.py
```

## Conclusion
This project demonstrates the application of NEAT to optimize a multi-elevator system. By evolving neural networks, we aim to minimize passenger wait times and improve the overall efficiency of elevator operations.
