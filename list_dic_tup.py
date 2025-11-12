# this shows lists, tuples within a list, and a dictionary

car_makes = ["kia", "mitsubishi", "toyota", "honda", "nissan"]
car_makes_models = [("kia", "forte"), ("mitsubishi", "galant"),
                    ("toyota", "corrola"), ("honda", "civic"), ("nissan", "altima")]
car_makes_models_dic = {"kia": "forte", "mitsubishi": "galant",
                        "toyota": "corola", "honda": "civic", "nissan": "altima"}

# this shows a dictionary with tuples as values and strings as keys

car_dic = {"toyota": ["camry", "corolla", "4runner"],
           "nissan": ("maxima", "altima", "versa"),
           "honda": ("civic", "accord", "pilot")}

# this code shows a set

car_set = {"toyota", "honda", "mercedes"}
car_set.add("jeep")
jap_car_set = {"toyota", "honda"}
print(car_set)
print(jap_car_set.issubset(car_set))
print(type(car_dic))
