import json
from pathlib import Path
import subprocess
from math import floor
from collections import OrderedDict
from cfg import transToDictWindow, musFilter, dictToTxtWindow


def json_to_txt(json_path):
    """
    Функция берет слова из одного кадра транскрибирования и сохраняет их новой строкой в txt файле
    :param json_path: directory with json files
    :return: create new file from "text" values from json
    """
    data_path = Path(json_path)

    for file in data_path.iterdir():
        with open(str(file)) as json_file:
            data = json.load(json_file)
            for jsString in data:
                with open(f'/home/alexsun8/streamlabs/radioTrans/bigdata/transcrib/{file.stem}.txt',
                          "a") as file_object:
                    # print(jsString['text'], out=file_object)
                    file_object.write(f'{jsString["text"]} \n')


def json_to_dict(json_path, save_dir='/home/alexsun8/streamlabs/radioTrans/bigdata/json_txt'):
    """
    Функция преобразует полученный в результате транскрибирования файл в словарь, где ключом является время,
    а значением - слово/несколько слов. Данный файл удобнее для дальнейщей работы.
    :param json_path: directory path with json files
    :param save_dir: dir with new files
    :return: -
    """
    data_path = Path(json_path)
    time_words_dict = OrderedDict()
    for file in data_path.iterdir():
        time_words_dict.clear()
        if file.suffix != '.json':
            continue

        with open(str(file)) as json_file:
            data = json.load(json_file)
            for jsString in data:
                if 'result' not in jsString.keys():
                    continue

                for wordInfo in jsString['result']:
                    time = wordInfo['start']
                    time_words_dict[time] = [wordInfo['word']]

        txt_path = Path(save_dir) / Path(f'json_{file.stem}.json')
        with open(str(txt_path), "w") as file_object:
            json.dump(time_words_dict, file_object)


def smart_json_to_txt(json_path, save_dir='/home/alexsun8/streamlabs/radioTrans/bigdata/smartTxt'):
    """
    По функционалу близко к `json_to_dict`, но в отличии от последней ключом является какой-то отрезок времени:
    вся звуковая дорожка разбивается на кардры длины transToDictWindow.
    В последствии происходит обработка полученного словаря. кадры проверяются по количеству слов: являются ли они
     песней/музыкой или нет. Для этого число слов в кадре должно превосходить MusFILTER_MINWORDSINSEC.
    :param json_path: directory path with json files
    :param save_dir: dir with new files
    :return: -
    """
    data_path = Path(json_path)
    time_words_dict = OrderedDict()
    for file in data_path.iterdir():
        time_words_dict.clear()
        if file.suffix != '.json':
            continue

        with open(str(file)) as json_file:
            data = json.load(json_file)
            for jsString in data:
                if 'result' not in jsString.keys():
                    continue

                for wordInfo in jsString['result']:
                    time = floor(wordInfo['start'])
                    if not len(time_words_dict):
                        time_words_dict[time] = [wordInfo['word']]
                        continue

                    last_time = list(time_words_dict.items())[-1][0]
                    if 0 <= time - last_time < transToDictWindow:
                        time_words_dict[last_time].append(wordInfo['word'])
                    else:
                        time_words_dict[time] = [wordInfo['word']]

                    # todo груничные слова time_words_dict[wordInfo['end']] =wordInfo['word']  or end time??
        txt_path = Path(save_dir) / Path(f'smart_{file.stem}.txt')
        with open(str(txt_path), "w") as file_object:
            num_of_written_items = 0
            for item in time_words_dict.items():
                if len(item[1]) <= musFilter and (not num_of_written_items or num_of_written_items == dictToTxtWindow):
                    # file_object.write(f'music\n')
                    pass
                elif len(item[1]) <= musFilter:
                    print(f'', file=file_object)
                    num_of_written_items = 0
                elif num_of_written_items < dictToTxtWindow:
                    # file_object.write(f'{" ".join(filter(None, item[1]))}')
                    print(f'{" ".join(filter(None, item[1]))}', file=file_object, end='\n')
                    num_of_written_items += 1
                else:
                    print(f'{" ".join(item[1])}', file=file_object, end=' ')
                    num_of_written_items = 1
                    # file_object.write(f'{" ".join(item[1])}\n')


def transcrib(data_path):
    """
    Функция была написана для данных из тестового отдела, в которых в каждой папке лежало два файла - црв и арв.
    Проиходит итерация по директории, содержащей подддериктории с файлами ары и црв.
    :param data_path:
    :return:
    """
    dataPath = Path(data_path)

    for folder in dataPath.iterdir():
        if not folder.is_dir():
            continue
        transcrib_files_in_folder(folder)


def transcrib_files_in_folder(folder, suffix='ts'):
    """
    Функция проходится по всем файлам из папки и транскрибирует их
    (транскрибирование созраняется в папке, заданной в файлике transcribe_mpeg.py)
    :param folder: директория, содержащая файлы
    :param suffix: раширение файлов, которые транскрибируются
    :return:
    """
    for file in folder.iterdir():
        extension = str(file).split('.')[-1]
        if not extension == suffix:
            continue
        print(f'\033[32m {file} \033[0m')
        proc = subprocess.Popen(['python', 'transcribe_mpeg.py', f'{file}'])
        proc.wait()


if __name__ == '__main__':
    # transcrib(Path('/home/alexsun8/streamlabs/radio/data/Список радио сравнения трансляций//'))

    json_to_dict('/home/alexsun8/streamlabs/radioTrans/newTranscribRes/',
                 save_dir='/home/alexsun8/streamlabs/radio/data/json/')
    # json_to_кdict('/home/alexsun8/streamlabs/radioTrans/results/',
    #              save_dir='/home/alexsun8/streamlabs/radioTrans/dictsFromJson')
    # json_to_txt('/home/alexsun8/streamlabs/radioTrans/bigdata/transcrib/')
    # smart_json_to_txt('/home/alexsun8/streamlabs/radioTrans/results',
    #                   '/home/alexsun8/streamlabs/radioTrans/smartTxt')

    # transcrib('/home/alexsun8/streamlabs/radio/data/Список радио сравнения трансляций/')
    # json_to_txt('/home/alexsun8/streamlabs/radioTrans/results')
