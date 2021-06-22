import pathlib
from comp_Synch import compare_prRec as compare
import csv

dataDir = pathlib.Path('/home/alexsun8/streamlabs/radio/data/Список радио сравнения трансляций')
resFile = pathlib.Path('/home/alexsun8/streamlabs/radio/data/PrRec_New.txt')


def iterate(data_dir, printRes=True):
    num = 0
    sameNum = 0
    resultsDict = {}

    for folder in data_dir.glob('*'):
        file1 = file2 = ""

        for fileBase in folder.glob(r'json_ЦРВ_*.ts'):
            file1 = fileBase
        for fileNew in folder.glob(r'json_АРВ_*.ts'):
            file2 = fileNew

        if file1 and file2 and printRes:
            print(str(file1))
            print(str(file2))

            istheSame, inclTime = compare(str(file1), str(file2))
            if istheSame:
                resultsDict[str(file1.stem)] = -8
                if printRes:
                    print(f'\033[32m {str(folder.stem):20} ==========> {str(istheSame)} \033[0m')
                sameNum += 1
            else:
                resultsDict[str(file1.stem)] = inclTime
                if printRes:
                    print(f'\033[33m {str(folder.stem):20} ==========> {str(istheSame)} \033[0m')
                    print(f'\033[36m {str(folder.stem):20} ===time===> {inclTime} \033[0m')

            num += 1

        elif printRes:
            print('\033[31m ERRROR!!!!')
            print(f' {str(file1)}')
            print(f'\033[31m {str(file2)}')
            print('\033[31m ERRROR!!!! \033[0m')

    if printRes:
        print(f"sameNum = {sameNum * 100 / num}%")
        print(f"sameNum = {sameNum}")
        print(f"num = {num}")
    return resultsDict


if __name__ == '__main__':
    iterate("/home/alexsun8/streamlabs/radio/data/json/")
