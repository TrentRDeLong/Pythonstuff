class car:
    wheels = 4
    engine = 1

    def __init__(self, make, model):
        self.make = make
        self.model = model
    
    def start_up(self):
        print("Vroom")

4runner = car("Toyota", "4runner")

