import os
import re
import xlrd
import json
import string
import pandas as pd
import numpy as np
from datetime import datetime

import Constants


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
            # print(file)
            df = {}
            if ".xls" in file:
                workbook: xlrd.book.Book = xlrd.open_workbook(file)
                worksheet: xlrd.sheet.Sheet = workbook.sheet_by_index(0)

                iban = self.__get_IBAN(worksheet)
                self.iban = iban
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

            elif ".csv" in file:
                with open(file, "r") as f:
                    data = f.read()
                    separator = {x: data.count(x) for x in [",", ";"]}
                    separator = max(separator, key=separator.get)
                
                    try:
                        self.iban = re.search(r'[a-zA-Z]{2}\d{22}', data).group(0)
                    except AttributeError as error:
                        self.iban = ""
                
                bank_scheme = self.__bank_identifier(self.iban)

                csv = pd.read_csv(file, delimiter=separator, on_bad_lines='skip', skiprows=bank_scheme["row"])

                columns = self.__transform_interval_to_indexes(bank_scheme["col"])
                columns = [csv.columns[x] for x in columns]
                csv = csv[columns]
                
                for col in csv:
                    df[col] = []
                    for cell in csv[col]:
                        euro = re.search(r"(.+)EUR\b", cell)
                        if euro != None:
                            cell = int(float(euro.group(0).replace("EUR", "").replace(".", "").replace(",", "."))*100)

                        elif re.search("\d{2}[\:\/-]\d{2}[\:\/-]\d{4}", cell) and len(cell) <= 10:
                            match = "/".join(re.findall("\d+", cell))
                            cell = datetime.strptime(match, '%d/%m/%Y')

                        df[col] += [cell]
                
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

        pd.set_option('display.max_rows', None)  # or 1000
        self.frame = self.frame.sort_values(by=["date"])
        self.frame = self.frame.drop_duplicates()
        self.frame = self.frame.reset_index(drop=True)


    def __get_IBAN(self, worksheet: xlrd.sheet.Sheet) -> str:
        for row in worksheet:
            for cell in row:
                iban = re.match(r'[a-zA-Z]{2}\d{22}', str(cell.value))
                if iban:
                    return iban.group()

        return iban

    def __transform_interval_to_indexes(self, interval: str):
        start, end = interval.split(':')
        start_index = string.ascii_uppercase.index(start.upper())
        end_index = string.ascii_uppercase.index(end.upper())
        indexes = list(range(start_index, end_index + 1))

        return indexes

    def __bank_identifier(self, iban: str, personal_accont: bool = True) -> dict:
        bank_scheme = Constants.BANK_FORMATS[iban[4:8]]
        
        self.bank = bank_scheme["name"]

        if personal_accont:
            return bank_scheme["personal_account"]
        else:
            return bank_scheme["business_account"]

    def __parse_column_ranges(self, columns: str) -> range:
        columns = columns.upper().split(":")
        ini, end = [string.ascii_uppercase.index(x) for x in columns]

        return range(ini, end + 1)

    def get_IBAN(self):
        return self.iban

