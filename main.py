import os

from categories import *
from info_banco import BankMovements

import datetime
from dateutil.relativedelta import relativedelta
pd.set_option('display.expand_frame_repr', False)

def main():
    files = [x for x in os.listdir() if "xls" in x]
    bank_movements = BankMovements(files)
    data_table = bank_movements.get_frame()

    # We take a slice of the frame based on the dates we want
    # ini_date = datetime(2022, 10, 1)
    # end_date = datetime(2026, 2, 1)
    end_date = datetime.datetime.now()
    ini_date = end_date + relativedelta(months=-1)

    data_table, days = dates_slice(data_table, ini_date, end_date)

    # We get the expenses and income entries and we get the totals
    expenses = sort_expenses(data_table)
    income = sort_income(data_table)

    for key in income:
        tmp = income[key].copy()
        tmp["amount"] = tmp["amount"]/100
        # print("{n}{key}{n}".format(key=key, n="-"*(37-int(len(key)/2))))
        # print(tmp)
        # print()
        tmp.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", key+".csv"), index=False)
            

    total_expenses = {key: expenses[key]["amount"].sum() for key in expenses if key!= "other"}
    total_expenses = sum({key: value for key, value in total_expenses.items() if key != "misc"}.values())
    print()
    print(
        f"Period from {ini_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}" + \
        f"\n----------------------------------\n" + \
        
        f"Total: {total_expenses/100:.2f}\n" + \
        f"Per person: {total_expenses/(100*2):.2f}\n" + \
        f"Per person per day: {total_expenses/(2*100*days):.2f}\n"
        f"Per person per month (30 days): {total_expenses/(2*100*days)*30:.2f}"
    )

main()