# # With this program, you can calculate the profit
# # or loss incurred for several transactions done by you

# # Ask for user input
# print("What should we call you?")
# nameinput = input()
# print("Welcome,", nameinput)

# # Ask to specify the purpose of this budget
# print("Give this budget a title. E.g. Kitchen repairs, monthly expenses")
# projtitleinput = input()
# print("You have named this budget as " + projtitleinput)

# # Ask for choice of currency
# print("Type the code of currency of choice. E.g. for US dollar type USD")
# currencyinput = input()
# print("You have selected " + currencyinput + " as your currency")

# # Ask for budget amount
# print("Please enter the total budget amount")
# budgetinput = input()
# print("The budget amount you selected for this budget is " +
#       budgetinput + " " + currencyinput)

# Input all incomes and expenses
total_income, total_expense = 0.0,  0.0
income, expense = 0.0, 0.0

# Ask whether you want to enter all expenses, all incomes or quit the program
print("Press I or i if you want to add an expense and press E or e if you want to add income.")
print("If you want to finalise, press Q or q")
myinput = str(input())


# After you press E (Has problems out here)
if myinput == 'E' or myinput == 'e':
    while(True):
        if income == 'n':
            break
        while(True):
            if expense == 'n':
                break
            print("Input Expense entry. Input n to quit: ")
            expense = input()
            total_expense = total_expense + float(expense)
            print("Total:", total_income)

        print("Input Income entry. Input n to quit: ")
        income = input()
        total_income = total_income + float(income)
        print("Total:", total_income)


# elif myinput == 'Q' or myinput == 'q':
#     exit
# else:
#     print("Invalid input")

# # Profit, Loss or Balanced budget?
# if total_expense > total_income:
#     loss = total_expense - total_income
#     print("You have incurred a loss of:" + loss + " " + currencyinput)
# elif total_income > total_expense:
#     profit = total_income - total_expense
#     print("You have incurred a profit of:" + profit + " " + currencyinput)
# else:
#     pass
