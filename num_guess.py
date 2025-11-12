guess_num = int(input("guess the number>>>"))
secret_num = 7
tries = 1
if guess_num == secret_num:
    print("you got it!")
else:
    while guess_num != secret_num:
        tries += 1
        if guess_num > secret_num:
            print(f"you guessed {guess_num}")
            guess_num = int(input("you guessed too high, try again>>> "))
        elif secret_num > guess_num:
            print(f"you guessed {guess_num}")
            guess_num = int(input("you guessed too low, try again>>> "))
print(f"you guessed correct! it took you {tries} tries!")
