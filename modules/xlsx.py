import os
from openpyxl import load_workbook
import pandas as pd

def xlsx_to_array(xlsx_file):
    xlsx_file = os.path.join("xlsx", xlsx_file)
    workbook = load_workbook(xlsx_file)
    row_no = 1
    data = []
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        if sheet_name == "Worksheet":
            continue
        group = sheet_name.split(" ")[1]

        for row in sheet.iter_rows(min_row=7, values_only=True):
            row = (row_no,) + row[1:]
            row = (group,) + row
            data.append(row)
            row_no += 1
    return pd.DataFrame(data, columns=["Grupa", "Redni_broj", "Broj indeksa", "Prezime", "Ime"])


def xlsx_k_to_array(workbook_path):
    workbook_path = os.path.join("xlsx", workbook_path)
    df = pd.read_excel(workbook_path, sheet_name='dhtmlxGrid')
    df = df[["Broj indeksa", "Prezime", "Ime", "Način polaganja"]]
    print(df.columns)
    return df