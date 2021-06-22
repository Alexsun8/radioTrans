from calculatePrRec import iterate
from pathlib import Path
import csv
import pickle


def getTestData():

    dataDir = Path('/home/alexsun8/streamlabs/radio/data/Список радио сравнения трансляций')

    testDict = iterate(dataDir, True)
    print(testDict)
    with open('testPrint.p', 'wb') as fp:
        pickle.dump(testDict, fp, protocol=pickle.HIGHEST_PROTOCOL)
    # with open("test_Results.json", 'w') as fp:
    #     json.dump(dict, fp)

def test_prRecPoint():

    getTestData()
    # testDict = json.load(open("test_Results.json", 'r'))
    with open('testPrint.p', 'rb') as fp:
        testDict = pickle.load(fp)

    num_of_good = 0
    total = 0

    TP = 0
    FP = 0
    TN = 0
    FN = 0
    notClose = 0

    with open('./data/answers.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            print(row)
            fileStem = Path(row[0]).stem
            print(fileStem)
            if row[1][:3] != '!!!':
                time = '.'.join(row[1].split(':'))
                time = time.replace("‘", '')
                time = time.replace("’", '')
                time = time.replace("'", '')
                test =testDict.get(fileStem)
                print(time)
                print(test)
                if test:
                    if time == '-' and test == '-8':
                        TN += 1
                        num_of_good += 1
                    elif time == '-':
                        FP += 1
                    elif test == '-8':
                        # print((floor(float(time)) * 60 + float(time) - floor(float(time))) * 210)
                        FN += 1

                    elif abs(float(time) - float(testDict[fileStem])) <= 1.5:
                        # print((floor(float(time)) * 60 + float(time) - floor(float(time))) * 210)
                        TP += 1
                        num_of_good += 1
                    else:
                        notClose += 1
                    total += 1
                else:
                    print(f'\033[31m {fileStem}   \033[0m')

    print(f'right: {num_of_good}; total: {total}')
    print(f'TP={TP}; FP={FP}; TN={TN}; FN={FN}')
    print(f'Precision={TP/(TP+FP)}')
    print(f'Recall={TP/(TP+FN)}')
    print(f'notClose = {notClose}; {notClose*100/(total-TP-FN)}%')
    # self.assertGreater(0.5, num_of_good / total)

if __name__ == '__main__':
    test_prRecPoint()