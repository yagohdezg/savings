import os
import re
import xlrd
import datetime
import numpy as np
import pandas as pd

CATEGORIES = [
    "Lupa",
    "Mercadona",
    "McDonald",
    "Bazar",
    "Bizum",
    "Parking",
    "HBO Max",
    "Ufg32-ciencias",
    "Shell",
    "TotalEnergies",
    "Easygas",
    "Farmacia",
    "Supermercado",
    "Bar",
    "Telpark",
    "Telefonica",
    "Matricula",
    "Kraken",
    "Alisal",
    "E3055",
    
    
    "Contactless",
    "Other"
]

class MoneyManager(object):
    """_summary_
    Class to manage, save and load bank information in a .csv format
    """
    # Default save folder
    __default_save_folder: str = './data'
    
    def __init__(self, user: str) -> None:
        """_summary_
        Initializes the class with a given user and loads a saved file
        with the name of said user

        Args:
            user (str): Name of the user
        """
        self.user = user
        self.__save_folder = os.path.abspath(self.__default_save_folder)
        self.__save_file = os.path.join(self.__save_folder, self.user + '.csv')

        # Create save folder in case it doesn't exist
        if not os.path.isdir(self.__save_folder):
            os.makedirs(self.__save_folder)    

        # Dictionary of all transactions    
        self.transactions = pd.DataFrame({
            "date": [],
            "description": [],
            "amount": []
        })
        
        self.__load_save()
        
    def save(self) -> None:
        """_summary_
        Saves current dataframe in a file with the username as the save file
        """

        self.transactions.to_csv(self.__save_file, index=False)
               
    def get_data(self) -> pd.DataFrame:
        """
        Returns the current dataframe
        
        Returns:
            pd.DataFrame: Current data of the class in a dataframe format
        """
        self.transactions = self.transactions.sort_values(by=["date"])

        if self.transactions['date'].dtype != 'datetime64[ns]':
            self.transactions['date'] =  pd.to_datetime(self.transactions['date'], format='%Y-%m-%d')
        
        return self.transactions

    def add_data(self, src_files: list) -> None:
        """
        Adds new data via an excel / csv file to the current
        dataframe

        Args:
            src_file (str): File to add the data from
        """
        # Read excel
        df = pd.concat([self.__read_excel(file) for file in src_files])
            
        # - Find out which bank we are working with
        banks = {
            "0049": {
                "name": "Santander",
                "row": 8,
                "col": "B:D"
            }
        }
        
        # - Get specific rows and columns from said bank
        IBAN = self.__get_IBAN(df)
        bank = str(IBAN[4:8])
        df = pd.concat([self.__read_excel(file, banks[bank]["row"] - 1, 
                               banks[bank]["col"]) for file in src_files])
        
        # - Rename excels columns to match the transactions ones
        for old, new in zip(df, self.transactions):
            df = df.rename(columns={old: new})
                
        # Join frames
        self.transactions = pd.concat([self.transactions, df], 
                                      ignore_index=True)

        # Format dates
        self.transactions["date"] = pd.to_datetime(self.transactions["date"], 
                                                   dayfirst=True)
        
        # Fix numbers
        self.transactions["amount"] = (self.transactions["amount"] * 100)
        self.transactions["amount"] = [round(x) for x 
                                       in self.transactions["amount"]]
        self.transactions["amount"] = self.transactions["amount"].astype(int)
        
        # Remove duplicates
        self.transactions = self.transactions.drop_duplicates()
      
    def set_date(self, start_date: str = "", end_date: str = "") -> None:
        if not self.get_data().empty:
            if start_date == "":
                start_date = datetime.datetime(1970, 1, 1)
            
            if end_date == "":
                end_date = datetime.datetime.now()
                
            first_day = np.datetime64(start_date)
            last_day = np.datetime64(end_date)
            
            self.transactions = self.transactions[self.transactions["date"] >= first_day]
            self.transactions = self.transactions[self.transactions["date"] <= last_day]
      
    def __load_save(self) -> None:
        """
        Loads an existing frame from a save
        """
        if os.path.isfile(self.__save_file):
            df = pd.read_csv(self.__save_file)
            self.transactions = pd.concat([self.transactions, df])
        
    def __get_IBAN(self, df: pd.DataFrame) -> str:
        """
        Finds the IBAN present in the excel

        Args:
            df (pd.DataFrame): Dataframe to search the IBAN in

        Returns:
            str: IBAN
        """
        for col in df:
            for cell in df[col]:
                if isinstance(cell, str):
                    match = re.match(r'[a-zA-Z]{2}\d{22}', cell)

                    if match:
                        return match.group(0)
        
        return None
    
    def __read_excel(self, file: str, header: int = 0, 
                     cols: str = "") -> pd.DataFrame:
        """
        Reads an excel file

        Args:
            file (str): File path
            header (int, optional): Line in which the header of the frame 
                                    is located. Defaults to 0.
            cols (str, optional): Columns to read. Defaults to "".

        Returns:
            pd.DataFrame: _description_
        """
        if cols == "":
            cols = pd.read_excel(file, nrows=1).columns

        if '.xls' == os.path.splitext(os.path.basename(file))[1]:
            wb = xlrd.open_workbook(file, logfile=open(os.devnull, 'w'))
            df = pd.read_excel(wb, engine='xlrd', header=header, usecols=cols)

        else:
            df = pd.read_excel(file, header=header, usecols=cols)
            
        return df
    
    @staticmethod
    def dict_walker(_dict: dict, pre = None):
        pre = pre if pre else []
        
        if isinstance(_dict, dict):
            for key, value in _dict.items():
                if isinstance(value, dict):
                    for d in MoneyManager.dict_walker(value, pre + [key]):
                        yield d
                    
                elif isinstance(value, list) or isinstance(value, tuple):
                    for i, v in enumerate(value):
                        for d in MoneyManager.dict_walker(v, pre + [key, i]):
                            yield d
                    
                else:
                    yield pre + [key, value]
                    
        else:
            yield pre + [_dict]
    
    def group_expenses(self, ignore_income: bool = False) -> dict:
        _dict = {category: [] for category in CATEGORIES}
        for i in range(len(self.transactions)):
            transaction = self.transactions.iloc[i]
            
            if ignore_income:
                if transaction["amount"] > 0:
                    continue
            
            for category in CATEGORIES:
                if category == "Other":
                    _dict["Other"].append(transaction)
                else:
                    # Buscamos la categoria
                    match = re.search(f'(?i){category}', transaction["description"])
                    if match:
                        # Si hay match la guardamos y PARAMOS
                        _dict[category].append(transaction)
                        break
                    
        return _dict