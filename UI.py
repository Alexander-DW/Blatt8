"""
Docstring for UI
This module is made to serve as a User-Interface
which the user can use to start the simulation such as
the number of rounds the user want to simulate, the size of the
island or ecosystem, the number of population of each organism,
the speed of the process, and the mode of the process, which is
Auto-run to only show the information at the last round of the simulation or
Step-by-step to show the information of each round of the simulation.
The simulation can be paused with the key "p" and could be resumed also with
the key "p"
"""

__author__ = "8407548, Winata, 8655943, Quan"
import time
import threading
from blatt8 import Ecosystem, Eucalyptus, MangoTree
from blatt8 import Elderberry, Grass, Rabbit, Koala, Fox, Leopard


class SimulationRunner:
    """
    Docstring for SimulationRunner
    Manages and runs ecosystem simulation with pause/resume functionality.

    The SimulationRunner handles the simulation loop, user interaction,
    and controls the pace of the simulation through speed settings.

    Attributes:
    pause_flag (bool): Current pause state of the simulation
    """

    def __init__(self):
        self.pause_flag = False

    def toggle_pause(self):
        """
        Docstring for toggle_pause
        Toggle the pause state between paused and running.

        Flips pause_flag and prints status message to console.
        :return: None
        """
        self.pause_flag = not self.pause_flag
        if self.pause_flag:
            print("\n--- Simulation Paused ---")
        else:
            print("\n+++ Simulation Resumed +++")

    def pause_reciever(self):
        """
        Docstring for pause_reciever
        Background thread that continuously listens for 'p' key
        to pause/resume.

        This method runs in a daemon thread and blocks waiting for user input.
        When 'p' or 'P' is entered, it calls toggle_pause()
        """
        while True:
            key = input()
            if key.lower() == "p":
                self.toggle_pause()

    def simulate(self, rounds, speed, runmode, organism_counts, size):
        """
        Docstring for simulate
        Run the ecosystem simulation with specified parameters.

        Args:
        rounds (int): Number of simulation days to run
        speed (str): Simulation speed - 'slow', 'normal', or 'fast'
        runmode (str): Run mode - 'auto' or 'step'
        organism_counts (dict): Dictionary mapping organism names to counts
        Example: {'Rabbit': 5, 'Grass': 10, 'Fox': 2}
        size (int): Size of the island ecosystem

        The simulation:
        - Creates an ecosystem with specified size
        - Adds organisms according to organism_counts
        - Runs for the specified number of rounds
        - Supports pause/resume via 'p' key input
        - Displays progress based on runmode

        Speed settings:
        - 'slow': 1.0 second delay between steps
        - 'normal': 0.5 second delay between steps
        - 'fast': 0.1 second delay between steps

        Run modes:
        - 'step': Shows day-by-day progress messages
        - 'auto': Runs without detailed progress output
        """

        # Start pause listener thread
        threading.Thread(target=self.pause_reciever, daemon=True).start()

        island = Ecosystem(size, days=int(rounds), temperature=25)

        organism_classes = {
            "Eucalyptus": Eucalyptus,
            "Mango Tree": MangoTree,
            "Elderberry": Elderberry,
            "Grass": Grass,
            "Rabbit": Rabbit,
            "Koala": Koala,
            "Fox": Fox,
            "Leopard": Leopard
        }

        # Add organisms based on counts
        for name, count in organism_counts.items():
            for _ in range(count):
                island.add_organism(organism_classes[name]())

        # Speed delays
        delays = {"slow": 1.0, "normal": 0.5, "fast": 0.1}
        delay = delays.get(speed, 0.5)

        print("\nSimulation in progress...\n"
              "Press 'p' at any time to pause/resume.\n")

        # Simulation loop
        for day in range(int(rounds)):
            island.simulate_step()

            if runmode == "step":

                island.message()

                # Pause handling
                while self.pause_flag:
                    time.sleep(0.1)

                # Auto delay
                time.sleep(delay)

            elif runmode == "auto":
                # Pause handling
                while self.pause_flag:
                    time.sleep(0.1)

                # Auto delay
                time.sleep(delay)

        island.message()
        print(f"\nSimulation complete after {rounds} days.")
        print(f"Final result: {len(island.flora)} plants,"
              f" {len(island.fauna)} animals")


def ask_user_input():
    """
    Docstring for ask_user_input
    Asking and storing the value from the user such as:
    number of rounds, island/ecosystem size, number of population
    of each organism, speed mode, run mode.
    Speed mode allows the user to choose between 3 option:
    slow, normal, or fast, which effects the processing speed of the
    simulation.
    Run mode is a choice between 2 options: Auto-run and Step-by-step
    Auto-run skips all the information inbetween the simulation and only
    shows the result when the number of rounds is reached.
    Step-by-step shows the information of each round until
    the number of rounds is reached
    """
    print("=== Ecosystem Simulation Configuration ===")

    # Number of rounds
    while True:
        rounds = input("Enter number of rounds: ")
        if rounds.isdigit() and int(rounds) >= 1:
            rounds = int(rounds)
            break
        print("Invalid input. Please enter a number!")

    # --- Island size ---
    while True:
        size = input("What is the size of the island"
                     "[min 10000]: ")
        if size.isdigit() and int(size) >= 10000:
            break
        print("Invalid input. Please enter a number[min 10000]!")

    # Number of organisms
    organism_counts = {}

    # Plants
    print("\n--- Plants ---")
    for plant in ["Eucalyptus", "Mango Tree", "Elderberry", "Grass"]:
        while True:
            amount = input(f"How many {plant} (0-50): ")
            if amount.isdigit() and 0 <= int(amount) <= 50:
                organism_counts[plant] = int(amount)
                break
            print("Invalid input. Please enter a number between 0 and 50.")

    print("\n--- Animals ---")
    for animal in ["Rabbit", "Koala", "Fox", "Leopard"]:
        while True:
            amount = input(f"How many {animal} (0-50): ")
            if amount.isdigit() and 0 <= int(amount) <= 50:
                organism_counts[animal] = int(amount)
                break
            print("Invalid input. Please enter a number between 0 and 50.")

    # Speed mode
    speed_options = {"1": "slow", "2": "normal", "3": "fast"}
    print("\nChoose speed mode:")
    print("1. Slow")
    print("2. Normal")
    print("3. Fast")

    while True:
        choice = input("Select speed (1–3): ")
        if choice in speed_options:
            speed = speed_options[choice]
            break
        print("Invalid choice.")

    # Run mode
    run_options = {"1": "auto", "2": "step"}
    print("\nChoose run mode:")
    print("1. Auto-run")
    print("2. Step-by-step")

    while True:
        choice = input("Select run mode (1–2): ")
        if choice in run_options:
            runmode = run_options[choice]
            break
        print("Invalid choice. Please enter 1 or 2.")

    print("\nConfiguration complete!")
    return rounds, speed, runmode, organism_counts, int(size)


if __name__ == "__main__":
    rounds, speed, runmode, organism_counts, size = ask_user_input()
    sim_run = SimulationRunner()
    sim_run.simulate(rounds, speed, runmode, organism_counts, size)
