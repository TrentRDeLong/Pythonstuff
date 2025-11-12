# go through a list alter the values and insert them into a new list

# pre-existing list
prices = [10, 20, 25, 30, 45, 67]
# empty list
prices_half = []
# for loop the grabs one value at a time from the pre-existing list, divides it by 2, stores it in a variable then add that variable to the empty list
for price in prices:
    halved_price = price/2
    prices_half.append(halved_price)

print(prices_half)

# list comprehension way (shorter version of doing the same thing)

# make a variable, use square brackets like a list, first write what operation you want to do to the counter variable, then write a for loop like regualar all inside the brackets
lc_prices_half = [price/2 for price in prices]
print(lc_prices_half)
