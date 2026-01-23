"""
Docstring for blatt8
this module is made for storing classes such as
Ecosystem, Lifeforms, Flora, Fauna, Carnivore,
Herbivore, Omnivore, Leopard, Koala, Rabbit,
Fox, MangoTree, Elderberry, Eucalyptus, Grass
which have it's own methods. These classes and
methods will be used to start a simulation.
"""
__author__ = "8407548, Winata, 8655943, Quan"
import random

# Ecosystem and its lifeforms


class Ecosystem():
    """
    Docstring for Ecosystem
    Represents an island ecosystem.
    Manages flora and fauna populations, environmental
    conditions, and daily simulation steps.

    var size: Total available area of the ecosystem
    :vartype size: int
    :var day: Current simulation day
    :vartype day: int
    :var temperature: Current temperature
    :vartype temperature: int
    :var weathercon: Current weather condition
    :vartype weathercon: str
    :var flora: List of all plant organisms
    :vartype flora: list[Flora]
    :var fauna: List of all animal organisms
    :vartype fauna: list[Fauna]
    """

    def __init__(self, size: int, days: int, temperature: int):
        self.size = size
        self.day = 0
        self.weathercon = None
        self.temperature = temperature
        self.flora = []
        self.fauna = []

    def add_organism(self, organism):
        """
        Docstring for add_organism
        used to add the newborns and new plants to the
        list of organism and the ecosystem

        :param organism: Organism to be added to the ecosystem
        :type organism: Lifeforms
        :return: None

        Test 1: Adding a plant places it in flora
        >>> eco = Ecosystem(100, 10, 25)
        >>> g = Grass()
        >>> eco.add_organism(g)
        >>> len(eco.flora)
        1
        >>> len(eco.fauna)
        0

        Test 2: Adding an animal places it in fauna
        >>> r = Rabbit()
        >>> eco.add_organism(r)
        >>> len(eco.fauna)
        1

        Test 3: Organism receives correct island reference
        >>> eco2 = Ecosystem(50, 5, 20)
        >>> e = Eucalyptus()
        >>> eco2.add_organism(e)
        >>> e.island is eco2
        True
        """
        organism.island = self
        if isinstance(organism, Flora):
            self.flora.append(organism)
        elif isinstance(organism, Fauna):
            self.fauna.append(organism)

    def available_area(self) -> int:
        """
        Docstring for available_area
        Calculate the total unoccupied area in the ecosystem.
        Returns the amount of free space available for plants to expand into.

        :return: Total unoccupied area
        :rtype: int

        Test 1: Empty ecosystem → full area
        >>> eco = Ecosystem(size=100, days=10, temperature=25)
        >>> eco.available_area()
        100

        Test 2: Adding one plant took area
        >>> g = Grass()
        >>> eco.add_organism(g)
        >>> eco.available_area() <= 100
        True

        Test 3: Area available never be negative
        >>> eco.size = 0
        >>> eco.available_area()
        0
        """
        used_area = sum(p.maxIndividualArea for p
                        in self.flora if p.is_alive())
        return max(0, self.size - used_area)

    def environment(self):
        """
        Docstring for environment
        Create the weather and temperature of the ecosystem
        Weather(con) has 3 modes: windy, storm and normal
        Temperature can vary between 22 to 40
        Both weather and temperature are randomized

        :return: None

        >>> eco = Ecosystem(100, 10, 25)
        >>> eco.environment()
        >>> eco.weathercon in ['windy', 'storm', 'normal']
        True
        >>> 22 <= eco.temperature <= 40
        True
        """

        self.temperature = random.randrange(22, 40)
        r = random.random()
        if r < 0.3:
            self.weathercon = "windy"
        elif r < 0.4:
            self.weathercon = "storm"
        else:
            self.weathercon = "normal"

    def apply_environment_effects(self):
        """
        Docstring for apply_environment_effects
        Applying the effects of the method environment
        When the weather(con) is normal then no special effects happen
        When the weather(con) is windy then the plants can
        reproduce(expand) more than normal
        When the weather(con) is storm then one random fauna and
        one random flora dies
        When the temperature is atleast 36 then huntSuccessRate for
        carnivore and omnivore will be cut half

        :return: None

        >>> eco = Ecosystem(100, 10, 25)
        >>> eco.flora = [Grass()]
        >>> eco.fauna = [Rabbit()]
        >>> eco.weathercon = 'windy'
        >>> eco.apply_environment_effects()
        >>> all(plant.current_expand_modifier == 1.5 for plant in eco.flora)
        True
        >>> eco.weathercon = 'storm'
        >>> eco.apply_environment_effects()
        >>> a = any(not plant.is_alive() for plant in eco.flora)
        >>> b = any(not animal.is_alive() for animal in eco.fauna)
        >>> a or b
        True
        >>> eco.temperature = 36
        >>> leopard = Leopard()
        >>> eco.fauna.append(leopard)
        >>> eco.apply_environment_effects()
        >>> leopard.current_hunt_modifier
        0.5
        """

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
        """
        Docstring for simulate_step
        Advances the simulation by a day

        This method performs a full simulation step, including:
        - Aging all organisms
        - Resetting daily modifiers
        - Randomizing and applying environmental conditions
        - Growing and expanding plants based on available area
        - Handling animal foraging, hunting, and starvation
        - Processing reproduction for plants and animals
        - Removing dead organisms from the ecosystem

        The ecosystem state is modified in place.

        :return: None
        """
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

        for plant in self.flora:
            plant.fruiting()
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

            # make the animals starve
            animal.starvation()

            # Animal reproduces
            offspring = animal.reproduce()
            new_organisms.extend(offspring)

        # Add all newborns
        for organism in new_organisms:
            self.add_organism(organism)

        # Remove dead
        self.flora = [p for p in self.flora if p.is_alive()]
        self.fauna = [a for a in self.fauna if a.is_alive()]

    def message(self):
        """
        Docstring for message
        Used for printing the current condition of the
        ecosystem such as:
        - Number of each organisme
        - Current day
        - Current temperature
        - Current weather condition

        :return: None
        """
        # Count each organism type
        eucalyptus_num = sum(1 for plant in self.flora
                             if isinstance(plant, Eucalyptus))

        mango_num = sum(1 for plant in self.flora
                        if isinstance(plant, MangoTree))

        elderberry_num = sum(1 for plant in self.flora
                             if isinstance(plant, Elderberry))

        grass_num = sum(1 for plant in self.flora
                        if isinstance(plant, Grass))

        rabbit_num = sum(1 for animal in self.fauna
                         if isinstance(animal, Rabbit))

        koala_num = sum(1 for animal in self.fauna
                        if isinstance(animal, Koala))

        fox_num = sum(1 for animal in self.fauna
                      if isinstance(animal, Fox))

        leopard_num = sum(1 for animal in self.fauna
                          if isinstance(animal, Leopard))

        print(f"Day {self.day}:")
        print(f"Weather = {self.weathercon},"
              f" Temperature = {self.temperature}")
        print(f"  Plants: Eucalyptus={eucalyptus_num},"
              f" Mango={mango_num}, Elderberry={elderberry_num},"
              f" Grass={grass_num}")
        print(f"  Animals: Rabbit={rabbit_num}, Koala={koala_num},"
              f" Fox={fox_num}, Leopard={leopard_num}")
        print(f"  Total: {len(self.flora)} plants,"
              f" {len(self.fauna)} animals\n")


class Lifeforms():
    """
    Docstring for Lifeforms
    Base class representing a generic lifeform in the ecosystem.

    Tracks the organism's size, growth,
    reproduction potential(mainly for flora), age, and alive status.

    Attributes:
        age (int): Current age of the organism in simulation days.
        minsize (float): Minimum size for the organism(flora)
        to be considered alive.
        currentsize (float): Current size of the organism.
        maxsize (float): Maximum possible size of the organism.
        growrate (float): Daily growth rate applied to currentsize.
        island (Ecosystem or None): Reference to the ecosystem
        the organism belongs to.
        alive (bool): Whether the organism is alive.
    """
    def __init__(self, minsize: int, maxsize: int, growrate: float,
                 island=None):
        self.age = 0
        self.minsize = minsize
        self.currentsize = minsize
        self.maxsize = maxsize
        self.growrate = growrate
        self.island = island
        self.alive = True

    def grow(self):
        """
        Docstring for grow
        Method for maturing the organism in the ecosystem

        :return: self.currentsize
        :rtype: int

        Test 1: normal growth
        >>> lf = Lifeforms(1, 10, 0.5, 0.1)
        >>> lf.currentsize
        1
        >>> lf.grow()
        1.5
        >>> lf.grow()
        2.25

        Test 2: maxsize cap
        >>> lf.currentsize = 9
        >>> lf.grow()
        10

        Test 3: dead organism does not grow
        >>> lf2 = Lifeforms(1, 10, 0.5, 0.1)
        >>> lf2.die()
        >>> lf2.grow()
        1
        """
        if self.is_alive():
            self.currentsize = min(self.currentsize * (1 + self.growrate),
                                   self.maxsize)
        return self.currentsize

    def is_alive(self):
        """
        Check whether the organism is alive.

        Returns True if the organism is alive
        and meets the minimum requirements
        (e.g., minimum size for Flora, health/size for Fauna),
        otherwise False.

        :return: True if alive, False otherwise
        :rtype: bool

        Test 1:
        >>> lf = Lifeforms(1, 5, 0.1, 0.1)
        >>> lf.is_alive()
        True

        Test 2:
        >>> lf.die()
        >>> lf.is_alive()
        False

        Test 3:
        >>> lf2 = Lifeforms(1, 5, 0.1, 0.1)
        >>> lf2.alive = False
        >>> lf2.is_alive()
        False
        """
        return self.alive

    def die(self):
        """
        Docstring for die
        Change the value of alive to False

        :return: None

        Test 1:
        >>> lf = Lifeforms(1, 5, 0.1, 0.1)
        >>> lf.is_alive()
        True
        >>> lf.die()
        >>> lf.is_alive()
        False

        Test 2:
        >>> lf.die()
        >>> lf.is_alive()
        False

        Test 3:
        >>> lf2 = Lifeforms(1, 5, 0.1, 0.1)
        >>> lf2.die()
        >>> lf2.is_alive()
        False
        """
        self.alive = False

# Flora base class


class Flora(Lifeforms):
    """
    Docstring for Flora
    Base class for plant life in the ecosystem.

    Represents a plant with attributes for growth, size, sunlight requirements,
    ability to expand, and potential to produce fruits or berries.

    :var minsize: Minimum size of the plant for survival
    :vartype minsize: float
    :var maxsize: Maximum achievable size of the plant
    :vartype maxsize: float
    :var growrate: Daily growth rate of the plant
    :vartype growrate: float
    :var needSunlight: Whether the plant requires sunlight to grow
    :vartype needSunlight: bool
    :var expandRate: Rate at which the plant can create new individuals
    :vartype expandRate: float
    :var maxIndividualArea: Area occupied by one plant
    :vartype maxIndividualArea: int
    :var current_expand_modifier: Temporary modifier applied to expansion
    :vartype current_expand_modifier: float
    :var fruitYield: Amount of fruit currently available
    :vartype fruitYield: int
    :var berryYield: Amount of berries currently available
    :vartype berryYield: int
    :var isFruiting: Whether the plant can produce fruits
    :vartype isFruiting: bool
    :var isBerrying: Whether the plant can produce berries
    :vartype isBerrying: bool
    """
    def __init__(self, minsize, maxsize, growrate,
                 expandRate: float, maxIndividualArea: int):
        super().__init__(minsize, maxsize, growrate)
        self.expandRate = expandRate
        self.maxIndividualArea = maxIndividualArea
        self.current_expand_modifier = 1.0
        self.fruitYield = 0
        self.berryYield = 0
        self.isFruiting = False
        self.isBerrying = False

    def expansion_request(self):
        """
        Docstring for expansion_request
        Request expansion of the plant population.

        If the plant is sufficiently mature, this method calculates
        how many new individuals this plant attempts to create.
        The result is probabilistic and influenced by expansion rate
        and environmental modifiers.

        The ecosystem decides how many of the requested expansions
        are actually granted based on available area.

        :return: Number of new plant individuals requested
        :rtype: int

        Test 1: Cannot expand when too small
        >>> f = Flora(minsize=1, maxsize=10, growrate=0.1,
        ... expandRate=1.0, maxIndividualArea=2)
        >>> f.currentsize = 4
        >>> f.expansion_request()
        0

        Test 2: Can expand when mature enough:
        >>> f.currentsize = 6
        >>> isinstance(f.expansion_request(), int)
        True

        Test 3: Cannot expand when expandRate is 0:
        >>> f.expandRate = 0
        >>> f.expansion_request()
        0
        """
        # Only expand if mature enough

        total_new_plants = 0
        if self.currentsize >= self.maxsize * 0.5:
            # Calculate exact number (can be fractional)
            exact_new_plants = (1 * self.expandRate *
                                self.current_expand_modifier)
            # Each plant can spawn based on expandRate

            # Guaranteed new plants (integer part)
            guaranteed_plants = int(exact_new_plants)

            # Fractional part (0.0 to 0.99...)
            fractional_part = exact_new_plants - guaranteed_plants

            # Probabilistically add one more based on fraction
            bonus_plant = 1 if random.random() < fractional_part else 0

            total_new_plants = guaranteed_plants + bonus_plant

        return total_new_plants

    def is_alive(self):
        """
        Check whether the organism is alive.

        Returns True if the organism is alive
        and meets the minimum requirements
        (e.g., minimum size for Flora, health/size for Fauna),
        otherwise False.

        :return: True if alive, False otherwise
        :rtype: bool

        Test 1:
        >>> f = Grass()
        >>> f.currentsize = 3
        >>> f.is_alive()
        True

        Test 2:
        >>> f = Grass()
        >>> f.currentsize = 0.05
        >>> f.is_alive()
        False

        Test 3:
        >>> f = Grass()
        >>> f.alive = False
        >>> f.is_alive()
        False
        """
        return self.alive and self.currentsize >= self.minsize

    def fruiting(self):
        """
        Docstring for fruiting
        Create fruit and berry for eligible floras like
        elderberry and mangotree
        The method here do nothing because not all flora
        has either a berry or a fruit.

        :return: None
        """

        # Default: do nothing
        pass

    def beEaten(self, amount, eater=None):
        """
        Docstring for beEaten
        Harvest fruits or berries without reducing plant height

        :param amount: how many units of edible part to eat
        :param eater: optional, for special logic like Koala
        :return: eaten
        :rtype: int

        Test 1: Normal eating
        >>> f = Flora(minsize=2, maxsize=10, growrate=0.1,
        ... expandRate=0.2, maxIndividualArea=3)
        >>> f.currentsize = 5
        >>> f.beEaten(2)
        2
        >>> f.currentsize
        3

        Test 2: Too much eating could kills plant:
        >>> f.beEaten(5)
        3
        >>> f.is_alive()
        False

        Test 3: No eating
        >>> f2 = Flora(minsize=2, maxsize=10, growrate=0.1,
        ... expandRate=0.2, maxIndividualArea=3)
        >>> f2.beEaten(0)
        0
        """
        eaten = 0

        # Check type of plant to decide what to reduce
        if self.__class__.__name__ == "MangoTree" and self.fruitYield >= 2:
            eaten = min(amount*2, self.fruitYield)
            self.fruitYield -= eaten

        elif self.__class__.__name__ == "Elderberry" and self.berryYield >= 5:
            eaten = min(amount*5, self.berryYield)
            self.berryYield -= eaten

        else:
            # Default: reduce plant size if edible
            eaten = min(amount, self.currentsize)
            self.currentsize -= eaten
            if self.currentsize < self.minsize:
                self.die()

        return eaten

# Species of flora


class Eucalyptus(Flora):
    """
    Docstring for Eucalyptus
    Represents a eucalyptus tree in the ecosystem.

    Eucalyptus can only be eaten by Koalas. Other herbivores
    cannot consume this plant. It grows relatively tall and
    expands slowly.

    Inherits all growth and expansion behavior from Flora
    but overrides the eating behavior.

    """
    def __init__(self, minsize=2, maxsize=15, growrate=0.2,
                 expandRate=0.4, maxIndividualArea=6):
        super().__init__(minsize, maxsize, growrate,
                         expandRate, maxIndividualArea)

    def beEaten(self, amount, eater=None):
        """
        Override: Only Koalas can eat Eucalyptus.

        Test 1: Non‑koala cannot eat:
        >>> e = Eucalyptus()
        >>> e.currentsize = 5
        >>> e.beEaten(2)
        0

        Test 2: only Koala can eat:
        >>> k = Koala()
        >>> eaten = e.beEaten(1, eater=k)
        >>> eaten in (0, 1)
        True

        Test 3: Eating cannot kill eucalyptus unless size < minsize:
        >>> e.currentsize = 2
        >>> e.beEaten(1, eater=k) in (0, 1)
        True
        """
        if eater is None or eater.__class__.__name__ != "Koala":
            return 0  # Not edible for other species
        return super().beEaten(amount, eater)


class MangoTree(Flora):
    """
    Docstring for MangoTree
    Represents a mango tree in the ecosystem.

    Mango trees can produce fruits without reducing their size.
    Fruits regenerate over time based on the tree's current size,
    up to a maximum fruit capacity.

    This plant provides a renewable food source for animals
    that can eat fruits.

    """

    def __init__(self, minsize=5, maxsize=40, growrate=0.1,
                 expandRate=0.2, maxIndividualArea=5, isFruiting: bool = True,
                 fruitRate: float = 0.15, maxFruit: int = 30):
        super().__init__(minsize, maxsize, growrate,
                         expandRate, maxIndividualArea)
        self.isFruiting = isFruiting
        self.fruitRate = fruitRate
        self.fruitYield = 0
        self.maxFruit = maxFruit

    def fruiting(self):
        """
        Docstring for fruiting
        Create fruit for mangotree

        :return: None

        Test 1: Normal fruiting
        >>> m = MangoTree()
        >>> m.currentsize = 10
        >>> m.fruitYield = 0
        >>> m.fruiting()
        >>> m.fruitYield > 0
        True

        Test 2: Max fruit cap
        >>> m.fruitYield = m.maxFruit
        >>> m.fruiting()
        >>> m.fruitYield == m.maxFruit
        True

        Test 3: fruiting not possible
        >>> m = MangoTree(isFruiting=False)
        >>> m.currentsize = 10
        >>> m.berryYield = 0
        >>> m.fruiting()
        >>> m.berryYield
        0
        """
        if self.isFruiting:
            # make fruits propotional to it's size
            self.fruitYield = min(self.fruitYield + int(
                self.currentsize * self.fruitRate), self.maxFruit)


class Elderberry(Flora):
    """
    Docstring for Elderberry
    Represents an elderberry plant in the ecosystem.

    Elderberry plants produce berries that can be harvested
    without harming the plant. Berry production depends on
    the plant's size and is capped at a maximum amount.

    Acts as a renewable berry food source for herbivores
    and omnivores.

    """
    def __init__(self, minsize=3, maxsize=12, growrate=0.15,
                 expandRate=0.3, maxIndividualArea=4, isBerrying: bool = True,
                 berryRate: float = 0.9, maxBerry: int = 75):
        super().__init__(minsize, maxsize, growrate,
                         expandRate, maxIndividualArea)
        self.isBerrying = isBerrying
        self.berryRate = berryRate
        self.berryYield = 0
        self.maxBerry = maxBerry

    def fruiting(self):
        """
        Docstring for fruiting
        Create berry for elderberry

        :return: None

        Test 1: normal fruiting
        >>> e = Elderberry()
        >>> e.currentsize = 10
        >>> e.berryYield = 0
        >>> e.fruiting()
        >>> e.berryYield > 0
        True

        Test 2: max berry cap
        >>> e.berryYield = e.maxBerry
        >>> e.fruiting()
        >>> e.berryYield == e.maxBerry
        True

        Test 3: fruiting not possible
        >>> e2 = Elderberry(isBerrying=False)
        >>> e2.currentsize = 10
        >>> e2.berryYield = 0
        >>> e2.fruiting()
        >>> e2.berryYield
        0
        """
        if self.isBerrying:
            # make berries propotional to it's size
            self.berryYield = min(self.berryYield + int(
                self.currentsize * self.berryRate), self.maxBerry)


class Grass(Flora):
    """
    Docstring for Grass
    Represents grass in the ecosystem.

    Grass grows quickly, occupies very little area,
    and can be eaten directly by herbivores.
    Unlike fruiting plants, eating grass reduces
    the plant's size and may kill it if overgrazed.

    """
    def __init__(self, minsize=0.1, maxsize=1, growrate=0.2,
                 expandRate=0.5, maxIndividualArea=1):
        super().__init__(minsize, maxsize, growrate,
                         expandRate, maxIndividualArea)


# Fauna base class


class Fauna(Lifeforms):
    """
    Docstring for Fauna
    Base class for all animal lifeforms in the ecosystem.

    Fauna have health, hunger, and starvation mechanics.
    Animals can grow, starve, reproduce, and die based
    on environmental conditions and food availability.

    This class provides shared behavior for all animal
    types such as starvation, health handling, and
    reproduction logic.

    """
    def __init__(self, minsize, maxsize, growrate, reproducerate,
                 starveRate: float, health: float, selfHarmEffect: float,
                 healEffect: float):
        super().__init__(minsize, maxsize, growrate, reproducerate)
        self.starveRate = starveRate
        self.hunger = 0
        self.health = health
        self.selfHarmEffect = selfHarmEffect
        self.healEffect = healEffect
        self.current_hunt_modifier = 1.0

    def is_alive(self):
        """
        Override: fauna dies if health <= 0 or size <= 0

        Test 1:
        >>> a = Fauna(1, 5, 0.1, 0.1, 0.1, 50, 1, 1)
        >>> a.is_alive()
        True

        Test 2:
        >>> a.health = 0
        >>> a.is_alive()
        False

        Test 3:
        >>> a.health = 50
        >>> a.currentsize = 0
        >>> a.is_alive()
        False
        """
        return self.alive and self.health > 0 and self.currentsize > 0

    def starvation(self):
        """
        Docstring for starvation
        Increases the hunger level by one each day
        If hunger level exceeds 3 then the fauna take damage
        If the damage calculation subtracts the fauna's health to 0
        then the fauna dies
        :return: None

        Test 1: Hunger increases
        >>> a = Fauna(1, 5, 0.1, 0.1, starveRate=1, health=50,
        ... selfHarmEffect=1, healEffect=1)
        >>> a.hunger = 3
        >>> a.starvation()
        >>> a.health < 50
        True

        Test 2: Death due to starvation
        >>> a2 = Fauna(1, 5, 0.1, 0.1, 1, 1, 1, 1)
        >>> a2.hunger = 4
        >>> a2.starvation()
        >>> a2.is_alive()
        False

        Test 3: No starvation if hunger low:
        >>> a3 = Fauna(1, 5, 0.1, 0.1, 1, 100, 1, 1)
        >>> a3.hunger = 0
        >>> a3.starvation()
        >>> a3.health == 100
        True
        """
        self.hunger += 1
        if self.hunger > 3:  # Hasn't eaten in 3 days
            self.health -= self.starveRate * 10
            if self.health <= 0:
                self.die()

    def reproduce(self):
        """
        Docstring for reproduce
        Attempt to reproduce and create offspring.

        Reproduction occurs only if the animal is healthy and
        sufficiently mature. The number of offspring is determined
        probabilistically using the reproduction rate.

        Newborn animals start at minimum size with reduced health.

        :return: List of newly created offspring
        :rtype: list[Fauna]

        Test 1: Too unhealthy → no offspring
        >>> a = Fauna(1, 10, 0.1, reproducerate=0.5,
        ... starveRate=1, health=30, selfHarmEffect=1, healEffect=1)
        >>> a.reproduce()
        []

        Test 2: Too small → no offspring
        >>> a.health = 100
        >>> a.currentsize = 1
        >>> a.reproduce()
        []

        Test 3:
        >>> a.currentsize = 5
        >>> a.reproduce()
        []
        """

        # Fauna is an abstract base class for animals.
        # It cannot create babies because it requires many arguments.
        # Therefore only subclasses (Rabbit, Fox, Koala, Leopard)
        # can reproduce.

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
    """
    Docstring for Carnivore
    Represents carnivorous animals in the ecosystem.

    Carnivores hunt other animals for food. Hunting success
    depends on a success rate and environmental modifiers.
    Failed hunts may cause self-inflicted damage.

    Carnivores cannot eat plants and rely entirely on
    successful hunts to survive.

    """
    def __init__(self, minsize, maxsize, growrate, reproducerate,
                 starveRate, health, selfHarmEffect, healEffect,
                 huntSuccessRate: float, selfHarmRate: float):
        super().__init__(minsize, maxsize, growrate, reproducerate,
                         starveRate, health, selfHarmEffect, healEffect)
        self.huntSuccessRate = huntSuccessRate
        self.selfHarmRate = selfHarmRate

    def hunt(self, fauna_list):
        """
        Docstring for hunt
        Attempt to hunt another animal for food.

        The animal selects a smaller, living prey from the given
        fauna list. A successful hunt restores health and resets
        hunger, while a failed hunt doesn't reset hunger.
        Both successful and failed hunt may cause self-inflicted damage.

        Hunting success can be affected by environmental modifiers.

        :param fauna_list: List of animals in the ecosystem
        :type fauna_list: list[Fauna]
        :return: None

        Test 1: Successful hunt
        >>> prey = Rabbit()
        >>> predator = Leopard(minsize=1, huntSuccessRate=1.0)
        >>> fauna_list = [prey]
        >>> predator.hunt(fauna_list)
        >>> prey.is_alive()
        False
        >>> predator.hunger
        0
        >>> predator.health >= 100
        True

        Test 2: Hunt fails but predator may self-harm
        >>> predator2 = Leopard(huntSuccessRate=0.0,
        ... health=50, selfHarmRate=1.0)
        >>> prey2 = Rabbit()
        >>> fauna_list2 = [prey2]
        >>> predator2.hunt(fauna_list2)
        >>> prey2.is_alive()  # hunt fails
        True
        >>> predator2.health < 50  # predator self-harmed
        True
        """
        if not self.is_alive():
            return

        # Find potential prey (smaller animals)
        prey_list = [animal for animal in fauna_list
                     if animal.is_alive()
                     and animal != self
                     and animal.currentsize < self.currentsize]

        if prey_list:
            target = random.choice(prey_list)
            if random.random() < (self.huntSuccessRate *
                                  self.current_hunt_modifier):
                # Successful hunt else failed hunt
                self.health = min(100, self.health + self.healEffect)
                self.hunger = 0
                target.die()

            # Self harm
            if random.random() < self.selfHarmRate:
                self.health -= self.selfHarmEffect


class Herbivore(Fauna):
    """
    Docstring for Herbivore
    Represents herbivorous animals in the ecosystem.

    Herbivores feed on plants by foraging. They can eat
    fruits, berries, or plant material depending on
    plant-specific rules.

    Successful foraging restores health and resets hunger.

    """
    def __init__(self, minsize, maxsize, growrate, reproducerate, starveRate,
                 health, selfHarmEffect, healEffect):
        super().__init__(minsize, maxsize, growrate, reproducerate,
                         starveRate, health, selfHarmEffect, healEffect)

    def forage(self, flora_list):
        """
        Docstring for forage
        Attempt to consume edible plant material.

        The animal selects a living plant from the given flora list
        and eats an available edible part such as fruits, berries,
        or plant mass depending on plant rules.

        Foraging(always successful) restores health and resets hunger.

        :param flora_list: List of plants in the ecosystem
        :type flora_list: list[Flora]
        :return: None

        Test 1: Plant reduces currentsize (e.g., Grass)
        >>> g = Grass()
        >>> r = Rabbit(health=50)
        >>> flora_list = [g]
        >>> original_size = g.currentsize
        >>> r.forage(flora_list)
        >>> g.currentsize < original_size
        True
        >>> r.hunger
        0
        >>> r.health >= 50
        True

        Test 2: Plant reduces fruit or berry (e.g., MangoTree)
        >>> m = MangoTree()
        >>> m.currentsize = 15
        >>> m.fruiting()  # generate some fruits
        >>> m.fruitYield >= 2
        True
        >>> r.forage([m])
        >>> m.fruitYield <  2  # some fruits were eaten
        True
        >>> m.currentsize == 15 # plant size not reduced
        True
        >>> r.hunger
        0

        Test 3: Plant with berry or fruit reduces size
        >>> e = Elderberry()
        >>> e.currentsize = 3
        >>> e.fruiting() # generate some berries
        >>> e.berryYield >= 5
        False
        >>> r.forage([e])
        >>> e.berryYield >= 0
        True
        >>> e.currentsize < 10 # lack of fruit, so the plant got eaten
        True
        """
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
    """
    Docstring for Omnivore
    Represents omnivorous animals in the ecosystem.

    Omnivores can both hunt animals and forage plants.
    Each simulation step, they randomly decide whether
    to hunt or forage.

    This class combines behaviors from both Carnivore
    and Herbivore.

    """
    def __init__(self, minsize, maxsize, growrate, reproducerate, starveRate,
                 health, selfHarmEffect, healEffect,
                 huntSuccessRate: float, selfHarmRate: float):
        super().__init__(minsize, maxsize, growrate, reproducerate,
                         starveRate, health, selfHarmEffect, healEffect)
        self.huntSuccessRate = huntSuccessRate
        self.selfHarmRate = selfHarmRate

    def hunt(self, fauna_list):
        """
        Docstring for hunt
        Attempt to hunt another animal for food.

        The animal selects a smaller, living prey from the given
        fauna list. A successful hunt restores health and resets
        hunger, while a failed hunt doesn't reset hunger.
        Both successful and failed hunt may cause self-inflicted damage.

        Hunting success can be affected by environmental modifiers.

        :param fauna_list: List of animals in the ecosystem
        :type fauna_list: list[Fauna]
        :return: None

        Test 1: Successful hunt
        >>> prey = Rabbit()
        >>> predator = Fox(health=100, minsize=1, huntSuccessRate=1.0)
        >>> fauna_list = [prey]
        >>> predator.hunt(fauna_list)
        >>> prey.is_alive()
        False
        >>> predator.hunger
        0
        >>> predator.health >= 100
        True

        Test 2: Hunt fails and predator may self-harm
        >>> predator2 = Fox(huntSuccessRate=0.0, health=50, selfHarmRate=1.0)
        >>> prey2 = Rabbit()
        >>> fauna_list2 = [prey2]
        >>> predator2.hunt(fauna_list2)
        >>> prey2.is_alive()  # hunt fails
        True
        >>> predator2.health < 50  # predator self-harmed
        True

        Test 3: Hunt successful but gets harmed
        >>> predator3 = Fox(health=50, huntSuccessRate=1.0,
        ... selfHarmRate=1.0, healEffect=2, selfHarmEffect=5)
        >>> prey3 = Rabbit()
        >>> fauna_list3 = [prey3]
        >>> predator3.hunt(fauna_list3)
        >>> prey3.is_alive() # hunt successful
        False
        >>> predator3.health < 50 # predator self-harmed
        True
        """
        if not self.is_alive():
            return

        prey_list = [animal for animal in fauna_list
                     if animal.is_alive()
                     and animal != self
                     and animal.currentsize < self.currentsize]

        if prey_list:
            target = random.choice(prey_list)
            if random.random() < (self.huntSuccessRate *
                                  self.current_hunt_modifier):
                # Successful hunt - prey dies immediately
                self.health = min(100, self.health + self.healEffect)
                self.hunger = 0
                target.die()
            if random.random() < self.selfHarmRate:
                self.health -= self.selfHarmEffect

    def forage(self, flora_list):
        """
        Docstring for forage
        Attempt to consume edible plant material.

        The animal selects a living plant from the given flora list
        and eats an available edible part such as fruits, berries,
        or plant mass depending on plant rules.

        Foraging(always successful) restores health and resets hunger.

        :param flora_list: List of plants in the ecosystem
        :type flora_list: list[Flora]
        :return: None

        Test 1: Plant reduces currentsize (e.g., Grass)
        >>> g = Grass()
        >>> f = Fox(health=50)
        >>> flora_list = [g]
        >>> original_size = g.currentsize
        >>> f.forage(flora_list)
        >>> g.currentsize < original_size
        True
        >>> f.hunger
        0
        >>> f.health >= 50
        True

        Test 2: Plant reduces fruit or berry (e.g., MangoTree)
        >>> m = MangoTree()
        >>> m.currentsize = 15
        >>> m.fruiting()  # generate some fruits
        >>> m.fruitYield >= 2
        True
        >>> f.forage([m])
        >>> m.fruitYield <  2  # some fruits were eaten
        True
        >>> m.currentsize == 15 # plant size not reduced
        True
        >>> f.hunger
        0

        Test 3: Plant with berry or fruit reduces size
        >>> e = Elderberry()
        >>> e.currentsize = 3
        >>> e.fruiting() # generate some berries
        >>> e.berryYield >= 5
        False
        >>> f.forage([e])
        >>> e.berryYield >= 0
        True
        >>> e.currentsize < 10 # lack of fruit, so the plant got eaten
        True
        """
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
    """
    Docstring for Leopard
    Represents a leopard in the ecosystem.

    Leopards are strong carnivores with a high hunting
    success rate. They rely entirely on hunting smaller
    animals for survival.

    """
    def __init__(self, minsize=2, maxsize=5, growrate=0.1, reproducerate=0.03,
                 starveRate=0.1, health=100, selfHarmEffect=5, healEffect=10,
                 huntSuccessRate=0.6, selfHarmRate=0.05):
        super().__init__(minsize, maxsize, growrate, reproducerate,
                         starveRate, health, selfHarmEffect, healEffect,
                         huntSuccessRate, selfHarmRate)


class Rabbit(Herbivore):
    """
    Docstring for Rabbit
    Represents a rabbit in the ecosystem.

    Rabbits are small herbivores that feed on plants.
    They reproduce relatively quickly but are vulnerable
    to predators due to their small size.

    """
    def __init__(self, minsize=0.2, maxsize=0.5, growrate=0.2,
                 reproducerate=0.1, starveRate=0.15, health=80,
                 selfHarmEffect=3, healEffect=8):
        super().__init__(minsize, maxsize, growrate, reproducerate, starveRate,
                         health, selfHarmEffect, healEffect)


class Koala(Herbivore):
    """
    Docstring for Koala
    Represents a koala in the ecosystem.

    Koalas are specialized herbivores that can eat
    eucalyptus leaves. Other plant types may not
    provide food depending on plant rules.

    Koalas have moderate growth and reproduction rates.

    """
    def __init__(self, minsize=0.3, maxsize=1.2, growrate=0.15,
                 reproducerate=0.09, starveRate=0.12, health=70,
                 selfHarmEffect=4, healEffect=9):
        super().__init__(minsize, maxsize, growrate, reproducerate, starveRate,
                         health, selfHarmEffect, healEffect)


class Fox(Omnivore):
    """
    Docstring for Fox
    Represents a fox in the ecosystem.

    Foxes are omnivores capable of both hunting smaller
    animals and foraging plants. They are adaptable and
    can survive on varied food sources.

    """
    def __init__(self, minsize=0.5, maxsize=3, growrate=0.15,
                 reproducerate=0.05, starveRate=0.12, health=90,
                 selfHarmEffect=4, healEffect=9, huntSuccessRate=0.5,
                 selfHarmRate=0.04):
        super().__init__(minsize, maxsize, growrate, reproducerate, starveRate,
                         health, selfHarmEffect, healEffect, huntSuccessRate,
                         selfHarmRate)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
