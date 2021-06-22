from pathlib import Path
from Levenshtein import distance
import matplotlib.pyplot as plt
from math import floor
import pandas as pd
from collections import deque
from comp_Synch import compare_dicts


def compare_txt_one_line(path1, path2, graph=True, save_folder_path=None):
    """
    функция находит расстояние Ливенштейна между двумя файлами, не разделяя на секунды/кадры и тд...
    :param path1: путь к 1 файлу
    :param path2: путь ко 2 файлу
    :param graph: Рисовать график или нет
    :param save_folder_path: путь к файлу с результатами
    :return:
    """
    slice_window = 14
    diff_len = 0
    memory_diff = deque()  # 0=same, 1=dif
    graph_array = []
    with open(path1) as f1, open(path2) as f2:
        if save_folder_path:
            save_path = Path(save_folder_path) / Path(path1).name
            with open(save_path, 'w'):
                pass
        for line1, line2 in zip(f1, f2):
            num_words1 = len(line1.split())
            num_words2 = len(line2.split())
            dist_ = distance(line1, line2)
            proc_dist = dist_ / len(line1)

            if graph:
                the_same = bool(proc_dist >= 0.5)
                if len(memory_diff) == slice_window:
                    last = memory_diff.popleft()
                    diff_len -= last
                memory_diff.append(the_same)
                diff_len += the_same
                graph_array.append(diff_len)

            if not save_folder_path:
                continue

            with open(save_path, 'a') as sFile:
                print(f"dist = {proc_dist}, lev = {dist_}, len1 = {num_words1}, len2 = {num_words2}", file=sFile)
                print(f'{line1.strip() if line1.strip() else "-"}', f'{line2.strip() if line2.strip() else "-"} \n',
                      sep='\n', file=sFile)

        if graph:
            plt.plot(graph_array)
            plt.show()


def compare_txt(path1, path2, save_folder_path=None, graph=True):
    """
    Сравнивает два файла покадрово, на вход должны подаваться файлы, где каждый новый кадр - новая строка
    (в строке только слова из этого кадра)
    :param path1: путь к 1 файлу
    :param path2: путь ко 2 файлу
    :param save_folder_path: не сохранять/путь к папке для сохранения результата
    :param graph: рисовать график/нет
    :return:
    """
    different_strs = 0
    num_of_strs = 0

    graphInfo = [0]  # четные индексы - накоплаение схожих, нечет - различных

    with open(path1) as f1, open(path2) as f2:
        if save_folder_path:
            save_path = Path(save_folder_path) / Path(path1).name
            with open(save_path, 'w'):
                pass

        for line1, line2 in zip(f1, f2):
            # print(line1.strip() if line1.strip() else "-")
            num_of_strs += 1
            num_words1 = len(line1.split())
            num_words2 = len(line2.split())
            if num_words1 < 5 and num_words2 < 5:
                if graph:
                    if len(graphInfo) % 2 == 0:  # если расхождение сейчас, сделать схожесть
                        graphInfo.append(0)

                    graphInfo[-1] += 1

                if not save_folder_path:
                    continue

                with open(save_path, 'a') as sFile:
                    print('music', file=sFile)
                continue

            dist_ = distance(line1, line2)
            proc_dist = dist_ / len(line1)
            if proc_dist > 0.5:
                different_strs += 1

                if graph:
                    if len(graphInfo) % 2 == 1:
                        graphInfo.append(0)

            elif graph and len(graphInfo) % 2 == 0:
                graphInfo.append(0)

            if graph:
                graphInfo[-1] += 1

            if not save_folder_path:
                continue

            with open(save_path, 'a') as sFile:
                print(f"dist = {proc_dist}, lev = {dist_}, len1 = {num_words1}, len2 = {num_words2}", file=sFile)
                print(f'{line1.strip() if line1.strip() else "-"}', f'{line2.strip() if line2.strip() else "-"} \n',
                      sep='\n', file=sFile)

    if graph:
        if len(graphInfo) % 2 == 1:
            graphInfo.append(0)

        print(graphInfo)

        index = range(floor(len(graphInfo) / 2) + 1)
        data = {'Схожие': graphInfo[::2],
                'Различные': graphInfo[1::2]}
        df = pd.DataFrame(data)
        df.plot(kind='bar')
        plt.show()

    return different_strs


def ARV_iteration(folder_path):
    """
    для итерации по файлам с названиями 'json_ЦРВ_*{time_date}.*'| 'json_AРВ_*{time_date}.*'
    :param folder_path: путь к папке с файлми
    :return:
    """
    for file in folder_path.iterdir():
        extension = str(file.name).split('.')[-1]
        if not extension == 'json':
            continue

        # data_class = str(file.stem)[:3]
        # if not data_class == 'АРВ':
        #     continue
        data_class = str(file.stem)[:8]
        if not data_class == 'json_АРВ':
            continue

        time_date = file.stem.split('[')[1]

        sec_path_variants = [f for f in file.parent.glob(f'json_ЦРВ_*{time_date}.*')]  # todo add re contain data & црв
        # sec_path_variants = [f for f in file.parent.glob(f'ЦРВ_*{time_date}.*')]  # todo add re contain data & црв
        if len(sec_path_variants) != 1:
            print(f'\033[35m ERROR!!!!!!!!!! {file.stem}\033[0m')
            print(sec_path_variants)
            continue

        sec_path = sec_path_variants[0]

        yield file, sec_path


def iter_alexData(folder_path):
    """
    Для итерации данных с названиями 'json_mono{i}_2.wav.json'
    :param folder_path: папка, по которой итерируются
    :return:
    """
    for file in folder_path.iterdir():
        extension = str(file.name).split('.')[-1]
        if not extension == 'json':
            continue

        data_class = str(file.stem)[9:12]
        if not data_class[2] == '1':
            continue

        i = data_class[0]
        print(f'i={i}')

        sec_file = f'json_mono{i}_2.wav.json'  # todo add re contain data & црв
        print(file, sec_file)
        yield file, sec_file, i


def iter_in_folder_with_txt(root_folder, func, save_in_folder=False, iteration_func=ARV_iteration):
    """
    Сравнение преобразованных txt,итерация по папке с трансрибированными txt, сравнение попарное арв/црв или mono|... файлов
    вариант поиска пар определяется функцикй iteration_func
    :param root_folder: папка с файлами
    :param func: функция для сравнения файлов
    :param save_in_folder: папка для сохраненя результатов
    :param iteration_func: функция, с помощью которой итерируемся и ищем пары. фозвращает пару файлов для сравнения
    :return:
    """
    root_folder_path = Path(root_folder)
    folder_path = root_folder_path / 'json_txt'
    res_path = str(root_folder_path / 'res.txt')
    img_dir = root_folder_path / 'img'
    if save_in_folder:
        save_folder_path = str(root_folder_path / 'results')

    with open(res_path, 'w'):
        pass

    for file, sec_path,i in iteration_func(folder_path):
        img_name = img_dir / f'mono{i}.png'
        sec_path = str(folder_path / sec_path)
        print(sec_path)
        func(str(file), str(sec_path), save_folder_path=save_folder_path, img_name=img_name)
        # res = func(str(file), str(sec_path))
        # res = func(str(file), str(sec_path), save_folder_path=save_folder_path)
        #

        print(f'\033[32m  \n {file.stem}\033[0m')
        with open(res_path, 'a') as sFile:
            print(f' \n {file.stem} \n', file=sFile)


if __name__ == '__main__':
    # diff_strs = compare_txt(
    #     "/home/alexsun8/streamlabs/radioTrans/beautiRes/ЦРВ_РАДИО 7 Ямал 402 11265 V_0d ["
    #     "2021-02-12T16_59_00..2021-02-12T17_02_00].ts.txt",
    #     "/home/alexsun8/streamlabs/radioTrans/beautiRes/АРВ_Радио 7_1f ["
    #     "2021-02-12T16_59_00..2021-02-12T17_02_00].ts.txt")

    # diff_strs = compare_txt('/home/alexsun8/streamlabs/radioTrans/beautiRes/ЦРВ_40E, 3665 МГЦ, левая пол. ВЕСТИ FM_f8 '
    #                         '[2021-02-01T11_56_00..2021-02-01T12_01_00].ts.txt',
    #                         '/home/alexsun8/streamlabs/radioTrans/beautiRes/АРВ_Вести ФМ 90.9 МГц_72 ['
    #                         '2021-02-01T11_56_00..2021-02-01T12_01_00].ts.txt')

    # diff_strs = compare_txt(
    #     '/home/alexsun8/Downloads/Telegram Desktop/Анадырь_ЦРВ_Радио_Маяк_2021_04_24T04_00_00_2021_04_24T08_00_00.ts',
    #     '/home/alexsun8/Downloads/Telegram Desktop/Анадырь_АРВ_Радио_Маяк_2021_04_24T04_00_00_2021_04_24T08_00_00.ts')

    iter_in_folder_with_txt('/home/alexsun8/streamlabs/radioTrans/alekseyData/', compare_dicts, save_in_folder=True,
                            iteration_func=iter_alexData)
    # iter_in_folder_with_txt('/home/alexsun8/streamlabs/radioTrans/dictsFromJson/', compare_dicts,
    #                         res_path='/home/alexsun8/streamlabs/radioTrans/jsonResCompare.txt',
    #                         save_folder_path='/home/alexsun8/streamlabs/radioTrans/jsonCompareRes')

    # compare_txt_one_line(
    #     '/home/alexsun8/streamlabs/radioTrans/bigdata/transcrib/smart_Анадырь_ЦРВ_Радио_Маяк_2021_04_24T04_00_00_2021_04_24T08_00_00.ts.txt',
    #     '/home/alexsun8/streamlabs/radioTrans/bigdata/transcrib/smart_АРВ_Радио_Маяк_2021_04_24T04_00_00_2021_04_24T08_00_00.ts.txt',
    #     save_folder_path='/home/alexsun8/streamlabs/radioTrans/bigdata/res/')
