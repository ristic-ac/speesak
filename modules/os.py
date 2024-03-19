import os

# Get all filenames from xlsx/
def get_xlsx_files():
    xlsx_files = []
    for root, dirs, files in os.walk("./xlsx"):
        for file in files:
            if file.endswith(".xlsx"):
                xlsx_files.append(file)
    return xlsx_files