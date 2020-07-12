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