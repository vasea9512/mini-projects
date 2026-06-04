import random

number = random.randint(1, 10)

while True:
    guess = int(input("Ghiceste un numar de la 1 la 10: "))

    if guess == number:
        print("Corect!!! ")
        break
    elif guess < number:
        print("Numărul este mai mare.")
    else:
        print("Numărul este mai mic.")