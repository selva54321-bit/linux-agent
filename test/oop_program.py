# Basic OOP Program Example
class Animal:
    """Base class for animals."""
    def __init__(self, name):
        self.name = name
        print(f"{self.name} created.")
	
def make_sound(self):
    """Abstract method to make a sound."""
    raise NotImplementedError("Subclass must implement abstract method")

class Dog(Animal):
    """Represents a dog."""
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed
	
def make_sound(self):
    return f"{self.name} says Woof! (I am a {self.breed})."

class Cat(Animal):
    """Represents a cat."""
    def __init__(self, name):
        super().__init__(name)
	
def make_sound(self):
    return f"{self.name} says Meow! (I am graceful)."

# Client code
if __name__ == "__main__":
    print("--- Testing OOP Concepts ---")
    doggo = Dog("Buddy", "Golden Retriever")
    catty = Cat("Whiskers")

    print(f"Dog sound: {doggo.make_sound()}")
    print(f"Cat sound: {catty.make_sound()}")
