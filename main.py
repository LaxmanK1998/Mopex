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

income_total, expense_total = 0, 0
entry = 0
i = 0
# Take inputs of transactions from the user
print("If you want to quit, press any letter")
print("Specify the number of entries:")
myinput = input()
letter_input = myinput.isalpha()
narrations = {}

if letter_input == True:
    exit
else:
    print("Enter positive values for incomes and negative values for expenses.")
    for i in range(1, int(myinput) + 1):
        print("Input your transaction number " + str(i) + ":")
        entry = input()
        print("Enter the narration for transaction number " + str(i) + ":")
        narrations[i - 1] = input()
        if round(int(entry)) < 0:
            expense_total = expense_total + round(int(entry))
        else:
            income_total = income_total + round(int(entry))

print("\n")
#Print all narrations
#Start from here next and add dictionary keys to respective entries
for i in range(1, int(myinput)+1):
    print(narrations[i-1])
diff = 0
result = income_total - abs(expense_total) # Calculate difference between total incomes and expenses
print('\n')
print("Income total: " + str(income_total))
print("Expense total: " + str(abs(expense_total)))

# Profit, Loss or Balanced budget?
if result > 0:
    print("You have incurred a profit of " + str(result) + " " + str(currencyinput))
    if int(budgetinput) > result:
        diff = int(budgetinput) - result
        print("You have spent " + str(diff) + " " + currencyinput + " less than your budget estimate. You saved " + str(diff) + " " + currencyinput)
    elif int(budgetinput) == result:
        diff = 0
        print("You have spent the same amount that you estimated")
    else:
        diff = result - int(budgetinput)
        print("You have earned " + str(diff) + " " + currencyinput + " more than your budget estimate.")

elif result < 0:
    print("You have incurred a loss of " + str(abs(result)) + " " + str(currencyinput))
else:
    pass