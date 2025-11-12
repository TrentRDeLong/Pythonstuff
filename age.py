name = input("Type name here >>>")
age_int = int(input("Type age here >>"))
age_str = str(age_int)
if age_int <= 10:
    print("you are a child")

elif age_int > 10 and age_int < 20:
    print("you are a teen")

elif age_int > 20:
    print(f"you are in your {age_str[0]}0's")
