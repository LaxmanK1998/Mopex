#Ask for user input
print("What should we call you?")
nameinput = input()
print("Welcome,", nameinput)

#Ask to specify the purpose of this project
print("Give this project a title. E.g. Kitchen repairs, monthly expenses")
projtitleinput = input()
print("You have named this project as "+projtitleinput)

#Ask for choice of currency
print("Type the code of currency of choice. E.g. for US dollar type USD")
currencyinput = input()
print("You have selected " + currencyinput + " as your currency")

#Ask for budget amount
print("Please enter the total budget amount")
budgetinput = input()
print("The budget amount you selected for this project is " + budgetinput + " " + currencyinput)