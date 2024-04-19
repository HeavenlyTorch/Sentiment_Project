weight = float(input("weight: "))
unit = input("Is that kg (k) or LBS (l)?: ")
if unit.lower() == "k":
    converted = weight * 2.2
    print("Weight in KG: " + str(weight))
    print("weight in LBS: " + str(converted))
elif unit.lower() == "l":
    converted = weight / 2.2
    print("Weight in KG: " + str(converted))
    print("weight in LBS: " + str(weight))
