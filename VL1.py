from numpy import double
import random

# Base Island class


class Island():
    def __init__(self, size: float, isolation: bool):
        self.temperature = random.randrange(22, 40)
        self.weathercon = random.choice(["storm", "windy", "normal"])
        self.size = size
        self.isolation = isolation


# Ecosystem and its lifeforms


class Ecosystem(Island):
    def __init__(self, temperature, weathercon):
        super().__init__(temperature, weathercon)
        self.area = 50
        self.day = 0
        self.flora = []
        self.fauna = []

    def add_organism(self, organism):
        organism.island = self
        if isinstance(organism, Flora):
            self.flora.append(organism)
        elif isinstance(organism, Fauna):
            self.fauna.append(organism)
    
    def available_area(self) -> float:
        used_area = sum(
            plant.population * plant.maxIndividualArea
            for plant in self.flora
        )
        return max(0, self.size - used_area)

    def environment(self):
        self.temperature = random.randrange(22, 40)
        if random.random() < 0.3:
            self.weathercon = "windy"
        elif 0.3 < random.random() < 0.4:
            self.weathercon = "storm"
        else:
            self.weathercon = "normal"

    def apply_environment_effects(self):
        # --- WINDY ---
        if self.weathercon == "windy":
            for plant in self.flora:
                plant.current_expand_modifier = 1.5

        # --- STORM ---
        if self.weathercon == "storm":
            if self.flora:
                random.choice(self.flora).die()
            if self.fauna:
                random.choice(self.fauna).die()

        # --- HIGH TEMPERATURE ---
        if self.temperature >= 36:
            for animal in self.fauna:
                if hasattr(animal, "huntSuccessRate"):
                    animal.current_hunt_modifier = 0.5

    def simulate_step(self):
        self.day += 1
        new_organisms = []
        
        # Age all organisms
        for plant in self.flora:
            plant.age += 1
        for animal in self.fauna:
            animal.age += 1
        
        # Reset daily modifiers
        for plant in self.flora:
            plant.current_expand_modifier = 1.0
        for animal in self.fauna:
            animal.current_hunt_modifier = 1.0

        self.environment()

        self.apply_environment_effects()

        # Plants grow and reproduce
        total_free_area = self.available_area()

        # Collect requests
        requests = []
        for plant in self.flora:
            requested = plant.expansion_request()
            if requested > 0:
                requests.append((plant, requested))

        random.shuffle(requests)  # fairness

        for plant, requested in requests:
            max_possible = int(total_free_area // plant.maxIndividualArea)
            granted = min(requested, max_possible)

            for _ in range(granted):
                new_plant = plant.__class__()
                new_plant.island = self
                self.flora.append(new_plant)

            total_free_area -= granted * plant.maxIndividualArea
            if total_free_area <= 0:
                break
        for plant in self.flora:
            plant.grow()
        """ offspring = plant.reproduce()
            new_organisms.extend(offspring)"""

        # Animals eat
        for animal in self.fauna:
            if isinstance(animal, Herbivore):
                animal.forage(self.flora)
            elif isinstance(animal, Carnivore):
                animal.hunt(self.fauna)
            elif isinstance(animal, Omnivore):
                if random.random() < 0.5:
                    animal.forage(self.flora)
                else:
                    animal.hunt(self.fauna)

            # Animal reproduces
            offspring = animal.reproduce()
            new_organisms.extend(offspring)
        
        # Add all newborns
        for organism in new_organisms:
            self.add_organism(organism)
        
        # Remove dead
        self.flora = [p for p in self.flora if p.is_alive()]
        self.fauna = [a for a in self.fauna if a.is_alive()]
        
        # Print stats
        print(f"Day {self.day}: {len(self.flora)} plants, {len(self.fauna)} animals")
    # each spaces is measured with unit
    # def init(self):

class Lifeforms():
    def __init__(self, starting_population: int, minsize: int, maxsize: int, growrate: float, reproducerate: float, island=None, creatures= None):
        self.population = starting_population
        self.age = 0
        self.minsize = minsize
        self.currentsize = minsize
        self.maxsize = maxsize
        self.growrate = growrate
        self.reproducerate = reproducerate
        self.island = island
        self.alive = True
    
    def grow(self):
        """Individual organism grows"""
        if self.is_alive():
            self.currentsize = min(self.currentsize * (1 + self.growrate), self.maxsize)
        return self.currentsize

    def populationReduce(self, amount):
        hunted = min(amount, self.population)
        self.population -= hunted

    def die(self):
        """Kill the organism"""
        self.alive = False


# Flora base class


class Flora(Lifeforms):
    def __init__(self, starting_population, minsize, maxsize, growrate, reproducerate, needSunlight: bool, expandRate: float, maxIndividualArea: int):
        super().__init__(starting_population, minsize, maxsize, growrate, reproducerate)
        self.needSunlight = needSunlight
        self.expandRate = expandRate
        self.maxIndividualArea = maxIndividualArea
        self.current_expand_modifier = 1.0

    def expand_population(self):
        """Adds new individuals based on expandRate"""
        offspring = []
        
        # Only expand if mature enough
    
        if self.currentsize >= self.maxsize * 0.5:
            # Calculate exact number (can be fractional)
            exact_new_plants = 1 * self.expandRate * self.current_expand_modifier  # Each plant can spawn based on expandRate
            
            # Guaranteed new plants (integer part)
            guaranteed_plants = int(exact_new_plants)
            
            # Fractional part (0.0 to 0.99...)
            fractional_part = exact_new_plants - guaranteed_plants
            
            # Probabilistically add one more based on fraction
            bonus_plant = 1 if random.random() < fractional_part else 0
            
            total_new_plants = guaranteed_plants + bonus_plant
            
            """" Create the new plants
            for _ in range(total_new_plants):
                new_plant = self.__class__()  # Create instance of same species
                offspring.append(new_plant)"""""

        return total_new_plants

    def die(self):
        if self.currentsize < self.minsize:
            self.population -= 1

    def beEaten(self, amount, eater=None):
        """Plants lose size when eaten, die if size drops below minsize"""
        eaten = min(amount, self.currentsize)
        self.currentsize -= eaten
        
        # Plants die if they shrink below minimum size
        if self.currentsize < self.minsize:
            self.die()
        
        return eaten

# Species of flora


class MangoTree(Flora):
    def __init__(self, starting_population=10, minsize=1, maxsize=10, growrate=0.1, reproducerate=0.05, needSunlight=True, expandRate=0.02, maxIndividualArea=5,
             isFruiting: bool = False, fruitRate: float = 0.1, fruitYield: int = 20):
        super().__init__(starting_population, minsize, maxsize, growrate,
                     reproducerate, needSunlight, expandRate, maxIndividualArea)
        self.isFruiting = isFruiting
        self.fruitRate = fruitRate
        self.fruitYield = fruitYield

    def fruiting(self):
        if self.isFruiting:
            self.fruitYield += int(self.population * self.fruitRate)


class Elderberry(Flora):
    def __init__(self, starting_population=15, minsize=1, maxsize=8, growrate=0.15, reproducerate=0.07, needSunlight=True, expandRate=0.03, maxIndividualArea=4,
             isFruiting: bool = False, fruitRate: float = 0.12, berryYield: int = 25):
        super().__init__(starting_population, minsize, maxsize, growrate,
                     reproducerate, needSunlight, expandRate, maxIndividualArea)
        self.isFruiting = isFruiting
        self.fruitRate = fruitRate
        self.berryYield = berryYield

    def fruiting(self):
        if self.isFruiting:
            self.berryYield += int(self.population * self.fruitRate)


class Grass(Flora):
    def __init__(self, starting_population=100, minsize=0.1, maxsize=1, growrate=0.2, reproducerate=0.1, needSunlight=True, expandRate=0.05, maxIndividualArea=1):
        super().__init__(starting_population, minsize, maxsize, growrate,
                     reproducerate, needSunlight, expandRate, maxIndividualArea)


# Fauna base class
class Fauna(Lifeforms):
    def __init__(self, starting_population, minsize, maxsize, growrate, reproducerate, nutrientNeed: str, starveRate: float, health: float, selfHarmEffect: float,
             healEffect: float):
        super().__init__(starting_population, minsize, maxsize, growrate, reproducerate)
        self.nutrientNeed = nutrientNeed
        self.starveRate = starveRate
        self.health = health
        self.selfHarmEffect = selfHarmEffect
        self.healEffect = healEffect
        self.current_hunt_modifier = 1.0
    
    def is_alive(self):
        """Override: fauna dies if health <= 0 or size <= 0"""
        return self.alive and self.health > 0 and self.currentsize > 0

    def consume(self):
        pass

    def starvation(self):
        """Check if animal is starving"""
        self.hunger += 1
        if self.hunger > 3:  # Hasn't eaten in 3 days
            self.health -= self.starveRate * 10
            if self.health <= 0:
                self.die()

    def reproduce(self):
        """Adds new individuals based on reproducerate"""
        offspring = []
        
        # Only reproduce if healthy and mature
        if self.health > 60 and self.currentsize >= self.maxsize * 0.7:
            # Calculate exact number (can be fractional)
            exact_new_animals = 1 * self.reproducerate
            
            # Guaranteed new animals (integer part)
            guaranteed_animals = int(exact_new_animals)
            
            # Fractional part
            fractional_part = exact_new_animals - guaranteed_animals
            
            # Probabilistically add one more
            bonus_animal = 1 if random.random() < fractional_part else 0
            
            total_new_animals = guaranteed_animals + bonus_animal
            
            # Create the new animals
            for _ in range(total_new_animals):
                baby = self.__class__()
                baby.currentsize = self.minsize
                baby.health = 50  # Babies start with lower health
                offspring.append(baby)
        
        return offspring

# Classes of fauna


class Carnivore(Fauna):
    def __init__(self, starting_population, minsize, maxsize, growrate, reproducerate, nutrientNeed, starveRate,
             health, selfHarmEffect, healEffect, eatMeat: bool, huntSuccessRate: float, selfHarmRate: float):
        super().__init__(starting_population, minsize, maxsize, growrate, reproducerate,
                     nutrientNeed, starveRate, health, selfHarmEffect, healEffect)
        self.eatMeat = eatMeat
        self.huntSuccessRate = huntSuccessRate
        self.selfHarmRate = selfHarmRate

    def hunt(self, fauna_list):
        """Hunt other animals"""
        if not self.is_alive():
            return
        
        # Find potential prey (smaller animals)
        prey_list = [animal for animal in fauna_list 
                     if animal.is_alive() 
                     and animal != self 
                     and animal.currentsize < self.currentsize]
        
        if prey_list:
            target = random.choice(prey_list)
            if random.random() < (self.huntSuccessRate * self.current_hunt_modifier):
                # Successful hunt
                #meat_gained = target.beEaten(target.currentsize, eater=self)
                self.health = min(100, self.health + self.healEffect)
                self.hunger = 0
            else:
                # Failed hunt - self harm
                if random.random() < self.selfHarmRate:
                    self.health -= self.selfHarmEffect


class Herbivore(Fauna):
    def __init__(self, starting_population, minsize, maxsize, growrate, reproducerate, nutrientNeed, starveRate,
             health, selfHarmEffect, healEffect, eatPlants: bool):
        super().__init__(starting_population, minsize, maxsize, growrate, reproducerate,
                     nutrientNeed, starveRate, health, selfHarmEffect, healEffect)
        self.eatPlants = eatPlants
    
    def forage(self, flora_list):
        """Eat plants"""
        if not self.is_alive():
            return
        
        # Find edible plants
        edible_plants = [plant for plant in flora_list if plant.is_alive()]
        
        if edible_plants:
            target = random.choice(edible_plants)
            amount_eaten = target.beEaten(1, eater=self)
            if amount_eaten > 0:
                self.health = min(100, self.health + self.healEffect)
                self.hunger = 0



class Omnivore(Fauna):
    def __init__(self, starting_population, minsize, maxsize, growrate, reproducerate, nutrientNeed, starveRate,
             health, selfHarmEffect, healEffect, eatAll: bool, huntSuccessRate: float, selfHarmRate: float):
        super().__init__(starting_population, minsize, maxsize, growrate, reproducerate,
                     nutrientNeed, starveRate, health, selfHarmEffect, healEffect)

    def hunt(self, fauna_list):
        """Hunt other animals (same as Carnivore)"""
        if not self.is_alive():
            return
        
        prey_list = [animal for animal in fauna_list 
                     if animal.is_alive() 
                     and animal != self 
                     and animal.currentsize < self.currentsize]
        
        if prey_list:
            target = random.choice(prey_list)
            if random.random() < self.huntSuccessRate * self.current_hunt_modifier:
                # Successful hunt - prey dies immediately
                meat_gained = target.beEaten(target.currentsize, eater=self)
                self.health = min(100, self.health + self.healEffect)
                self.hunger = 0
            else:
                if random.random() < self.selfHarmRate:
                    self.health -= self.selfHarmEffect
    
    def forage(self, flora_list):
        """Eat plants (same as Herbivore)"""
        if not self.is_alive():
            return
        
        edible_plants = [plant for plant in flora_list if plant.is_alive()]

        if edible_plants:
            target = random.choice(edible_plants)
            amount_eaten = target.beEaten(1, eater=self)
            if amount_eaten > 0:
                self.health = min(100, self.health + self.healEffect)
                self.hunger = 0


# Species of fauna


class Leopard(Carnivore):
    def __init__(self, starting_population=5, minsize=1, maxsize=3, growrate=0.1, reproducerate=0.05, nutrientNeed=0.08, starveRate=0.1,
             health=100, selfHarmEffect=5, healEffect=10, eatMeat=True, huntSuccessRate=0.6, selfHarmRate=0.05):
        super().__init__(starting_population, minsize, maxsize, growrate, reproducerate, nutrientNeed, starveRate,
                     health, selfHarmEffect, healEffect, eatMeat, huntSuccessRate, selfHarmRate)


class Rabbit(Herbivore):
    def __init__(self, starting_population=30, minsize=0.2, maxsize=0.5, growrate=0.2, reproducerate=0.1, nutrientNeed=0.01, starveRate=0.15,
             health=80, selfHarmEffect=3, healEffect=8, eatPlants=True):
        super().__init__(starting_population, minsize, maxsize, growrate, reproducerate, nutrientNeed, starveRate,
                     health, selfHarmEffect, healEffect, eatPlants)

class Koala(Herbivore):
    def __init__(self, starting_population=25, minsize=0.5, maxsize=1.2, growrate=0.15, reproducerate=0.07, nutrientNeed="plants", starveRate=0.12,
                 health=100, selfHarmEffect=4, healEffect=9, eatPlants=True):
        super().__init__(starting_population, minsize, maxsize, growrate, reproducerate, nutrientNeed, starveRate,
                         health, selfHarmEffect, healEffect, eatPlants)

    def eat(self, plant):
        """To check if the Koala can eat the given plant(Eucalyptus)."""
        amount = plant.beEaten(1, eater=self)
        if amount > 0:
            if self.health < 100:
                self.health = min(100, self.health + self.healEffect)
                self.hunger = 0

            

class Fox(Omnivore):
    def __init__(self, starting_population=15, minsize=0.5, maxsize=1.5, growrate=0.15, reproducerate=0.07, nutrientNeed="all", starveRate=0.12,
             health=90, selfHarmEffect=4, healEffect=9, eatAll=True, huntSuccessRate=0.5, selfHarmRate=0.04):
        super().__init__(starting_population, minsize, maxsize, growrate, reproducerate, nutrientNeed, starveRate,
                     health, selfHarmEffect, healEffect, eatAll, huntSuccessRate, selfHarmRate)