import battery_parser as bp
import pandas as pd
import os

if __name__ == '__main__':
    directory = r'D:\Matlab_projects\RC-simulation\data\n7_rerun'
    files = bp.importing.list_files(directory=directory, filetype='xls')
    for filename in files:
        data = bp.importing.import_xls(filename)
        print(data)