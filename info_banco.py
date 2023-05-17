import os
import re
import xlrd
import json
import string
import pandas as pd
import numpy as np

from datetime import datetime


class BankMovements(object):
    def __init__(self, files) -> None:
        self.frame: pd.DataFrame = pd.DataFrame({})

        # Metadata
        self.iban = ""
        self.bank = ""

        self.__read_files(files)

    def get_frame(self):
        return self.frame

    def __read_files(self, files: list):
        
        for file in files:
            print(f"Reading file '{file}'")
            df = {}

            workbook: xlrd.book.Book = xlrd.open_workbook(file)
            worksheet: xlrd.sheet.Sheet = workbook.sheet_by_index(0)

            iban = self.__get_IBAN(worksheet)
            bank_scheme = self.__bank_identifier(iban)
            
            row_range = range(bank_scheme["row"], len(worksheet.col_values(0)))
            col_range = self.__parse_column_ranges(bank_scheme["col"])
            col_names = worksheet.row_values(row_range.start - 1)
            
            for col in col_range:
                col_name = col_names[col]
                df[col_name] = []
                for row in row_range:
                    cell = worksheet.cell(row, col).value

                    if isinstance(cell, float):
                        cell = int(cell*100)

                    elif re.search("\d{2}[\:\/-]\d{2}[\:\/-]\d{4}", cell) and len(cell) <= 10:
                        match = "/".join(re.findall("\d+", cell))
                        cell = datetime.strptime(match, '%d/%m/%Y')


                    df[col_name] += [cell]

            df = pd.DataFrame(df)

            for col in df:
                col_type = df[col].dtype
                if pd.api.types.is_int64_dtype(col_type):
                    df = df.rename({col: "amount"}, axis="columns")

                elif pd.api.types.is_datetime64_any_dtype(col_type):
                    df = df.rename({col: "date"}, axis="columns")

                elif pd.api.types.is_object_dtype(col_type) or pd.api.types.is_string_dtype(col_type):
                    df = df.rename({col: "description"}, axis="columns")
            
            self.frame = pd.concat([self.frame, df])
        
        self.frame = self.frame.drop_duplicates()
        self.frame = self.frame.sort_values(by=["date"])
        self.frame = self.frame.reset_index(drop=True)

    def __get_IBAN(self, worksheet: xlrd.sheet.Sheet) -> str:
        for row in worksheet:
            for cell in row:
                iban = re.match(r'[a-zA-Z]{2}\d{22}', str(cell.value))
                if iban:
                    return iban.group()
                
        self.iban = iban
                    
        return None

    def __bank_identifier(self, iban: str, personal_accont: bool = True) -> dict:
        with open("banks_format.json", "r+") as file:
            banks_format = json.loads(file.read())

        bank_scheme = banks_format[iban[4:8]]
        self.bank = bank_scheme["name"]

        if personal_accont:
            return bank_scheme["personal_account"]
        else:
            return bank_scheme["business_account"]

    def __parse_column_ranges(self, columns: str) -> range:
        columns = columns.upper().split(":")
        ini, end = [string.ascii_uppercase.index(x) for x in columns]

        return range(ini, end + 1)


