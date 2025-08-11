import os
from openpyxl import load_workbook
import pandas as pd

# Funkcija za ucitavanje grupa iz xlsx fajla u DataFrame
def convert_xlsx_groups_to_dataframe(xlsx_file):
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

# Funkcija za ucitavanje kompletnog spiska studenata iz xlsx fajla u DataFrame
def convert_xlsx_complete_to_dataframe(workbook_path):
    workbook_path = os.path.join("xlsx", workbook_path)
    df = pd.read_excel(workbook_path, sheet_name='dhtmlxGrid')
    df = df[["Broj indeksa", "Prezime", "Ime", "Način slušanja"]]
    return df