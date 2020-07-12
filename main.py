# With this program, you can calculate the profit
# or loss incurred for several transactions done by you

# Ask for user input
print("What should we call you?")
nameinput = input()
print("Welcome,", nameinput)

# Ask to specify the purpose of this budget
print("Give this budget a title. E.g. Kitchen repairs, monthly expenses")
projtitleinput = input()
print("You have named this budget as " + projtitleinput)

# Ask for choice of currency
print("Type the code of currency of choice. E.g. for US dollar type USD")
currencyinput = input()
print("You have selected " + currencyinput + " as your currency")

# Ask for budget amount
print("Please enter the total budget amount")
budgetinput = input()
print("The budget amount you selected for this budget is " +
      budgetinput + " " + currencyinput)

result = 0
entry = 0
i = 0
# Take inputs of transactions from the user
print("If you want to quit, press any letter")
print("Specify the number of entries:")
myinput = input()
letter_input = myinput.isalpha()

if letter_input == True:
    exit
else:
    print("Enter positive values for incomes and negative values for expenses.")
    for i in range(1, int(myinput) + 1):
        print("Input your transaction number " + str(i) + ":")
        entry = input()
        result = result + round(int(entry))
diff = 0
# # Profit, Loss or Balanced budget?
if result > 0:
    print("You have incurred a profit of " + str(result) + " " + str(currencyinput))
    if int(budgetinput) > result:
        diff = int(budgetinput) - result
        print("You have spent " + str(diff) + " " + currencyinput + " less than your estimate")
    elif int(budgetinput) == result:
        diff = 0
        print("You have spent the same amount that you estimated")
    else:
        diff = result - int(budgetinput)
        print("You have spent " + str(diff) + " " + currencyinput + " more than your estimate")

elif result < 0:
    print("You have incurred a loss of " + str(abs(result)) + " " + str(currencyinput))
else:
    pass