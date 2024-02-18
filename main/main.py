import os

from categories import *
from BankManager import BankMovements
import Constants

import datetime
from dateutil.relativedelta import relativedelta
pd.set_option('display.expand_frame_repr', False)

def main():
    # We take a slice of the frame based on the dates we want
    ini_date = datetime.datetime(2023, 6, 1)
    # end_date = datetime.datetime(2023, 5, 1)
    end_date = datetime.datetime.now()
    # ini_date = end_date + relativedelta(months=-1)

    bank_movements = read_files()
    yago = bank_movements["yago"]
    # abril = bank_movements["abril"]

    movements_yago = get_expenses_and_income(yago.get_frame(), ini_date, end_date)
    movements_abril = get_expenses_and_income(abril.get_frame(), ini_date, end_date)

    # Print
    total_expenses(movements_yago["expenses"], ini_date, end_date)
    # total_expenses(movements_abril["expenses"], ini_date, end_date)

    # Save
    for frame in movements_yago:
        save_frame(movements_yago[frame], frame, yago.get_IBAN())
        # save_frame(movements_abril[frame], frame, abril.get_IBAN())


def get_expenses_and_income(frame: pd.DataFrame(), ini_date, end_date):
    frame = dates_slice(frame, ini_date, end_date)

    # We get the expenses and income entries and we get the totals
    expenses = sort_expenses(frame)
    income = sort_income(frame)

    return {"expenses": expenses, "income": income}


def save_frame(frame: pd.DataFrame, name: str, IBAN: str):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", IBAN)
    os.makedirs(path, exist_ok=True)
    for key in frame:
        tmp = frame[key].copy()
        tmp["amount"] = tmp["amount"]/100
        tmp.to_csv(os.path.join(path, key + ".csv"), index=False)


def total_expenses(expenses: pd.DataFrame, ini_date, end_date):
    GASTOS_CASA = ["food", "internet", "electric_gas", "casa"]
    days = (end_date - ini_date).days

    print(expenses["food"])
    total_expenses = {key: expenses[key]["amount"].sum() for key in expenses if key in GASTOS_CASA}
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


def read_files():
    files_path = Constants.INPUT_FILES
    yago = [os.path.join(files_path, file) for file in os.listdir(files_path) if "xls" in file]
    abril = [os.path.join(files_path, file) for file in os.listdir(files_path) if "csv" in file]
    bank_movements = {
        "yago": BankMovements(yago),
        # "abril": BankMovements(abril)
    }
    
    return bank_movements

main()