class toyota:
    # class variables apply to all instances of this class
    make = "Toyota"
    origin = "japan"
    cars_onlot = 0

    # instance variables only apply to the specific instance that is created from the class
    def __init__(self, model, year, color):
        self.model = model
        self.year = year
        self.color = color
        toyota.cars_onlot += 1

    # class mathods are things that this class can do, similar to functions
    def car_info(self):
        print(f"This is a {self.year} toyota {self.model} in {self.color}")


car_1 = toyota("camry", 2016, "white")
car_2 = toyota("corrola", 2025, "black")
car_3 = toyota("4runner", 2012, "grey")

car_1.car_info()
car_2.car_info()
car_3.car_info()


print(toyota.cars_onlot)
