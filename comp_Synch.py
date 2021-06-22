import json
from cfg import lineDuration, MusFILTER_MINWORDSINSEC, WIN_DUR_FOR_SYNCH
from pathlib import Path
from Levenshtein import distance
import matplotlib.pyplot as plt
from math import floor
from collections import deque


def music_with_sec_file(comp_path, line_time, offset) -> [bool, str]:
    """
    При определении, что эталонный кадр является песней/музыкой, сравнивается с  временем во 2 файле
    :param comp_path: путь ко 2 файлу
    :param line_time: время начала эталонного фрагмента
    :param offset: сдвиг двух файлов временной относительно друг друга
    :return: [Есть вставка? ; сравниваемая строка из 2 файла]
    """
    # return insert, comp_line
    # ???? норм если чисто также
    # вресенно абивваю на offset, конкретно в данной минуте мерием по методу 1, offset сохраняется
    # проходим, ищем начало то же по времени ближайшее. нашли, по длительности строку составили количество слов.
    # вернули true- если много, не музыка. Иначе - false
    comp_line = []
    with open(comp_path) as f2:
        comp_data = json.load(f2)

        for word_time, words in comp_data.items():
            word_time = float(word_time) - offset

            if floor(word_time) < line_time:
                continue

            if word_time > line_time + lineDuration:
                break

            for word in words:
                comp_line.append(word)

    comp_line = ' '.join(comp_line)

    if len(comp_line.split()) < MusFILTER_MINWORDSINSEC * lineDuration:
        return False, comp_line

    return True, comp_line


def compare_with_sec_file(line, comp_path, line_time, offset) -> [float, float, str]:
    """
    В случае, если в кадре первого файла обозначилось, что кадр не песня, а речь, происходит сравнение со 2 файлом
    (сравнивается не только фрагмент в этот же временной момент, но и кадры +- WIN_DUR_FOR_SYNCH секунд)
    При нахождении максимального совпадения сохраняется сдвиг новый
    :param line: эталонный кадр
    :param comp_path: файл, в котором ищем совпадение максимальное
    :param line_time: время кадра в эталонном файле
    :param offset: сдвиг двух файлов относительно друг друга
    :return: [расстояние между двумя кадрами; временной сдвиг(для синхронизации);
    кадр из допустимого окна, максимально совпавший с эталонным]
    """
    # return dist_, offset, comp_line
    min_dist_ = len(line)
    best_start_time = 0
    best_comp_line = ''
    with open(comp_path) as f2:
        comp_data = json.load(f2)
        comp_data = list(comp_data.items())

        # print(f' line = {line}, line_time = {line_time}')

        for i, (word_time, word) in enumerate(comp_data):
            word_time = float(word_time) - offset
            if not abs(line_time - word_time) <= WIN_DUR_FOR_SYNCH:
                continue
            # todo beak add for end of data. Remember, that offset can be <0

            comp_line = word

            for time, temp_word in comp_data[i + 1:]:
                time = float(time) - offset
                if time - word_time > lineDuration:
                    break
                comp_line.append(temp_word[0])
                # for t_w in temp_word:
                #     comp_line.append(t_w)

            comp_line = ' '.join(comp_line)

            # print(f'comp i = {i}; line = {comp_line}, line_time = {word_time}, dist_ = {distance(line, comp_line)}')

            dist_ = distance(line, comp_line)
            if dist_ < min_dist_:
                best_start_time = word_time
                best_comp_line = comp_line
                min_dist_ = dist_

    # print(f'best_start_time={best_start_time}; best_comp_line = {best_comp_line}')
    offset = (best_start_time + offset - line_time)

    return min_dist_, offset, best_comp_line


def compare_dicts(path1, path2, save_folder_path=None, graph=True, img_name=None):
    """
        На вход поступают два файла, каждая строка которых является кадром.
    По количеству слов фильтруется содержит ли этот кадр музыку/песню или речь.
    Для каждого кадора вызывается функция `compare_with_sec_file`
    :param path1: путь к 1 файлу
    :param path2: путь ко 2 файлу
    :param save_folder_path: сохранять ли результат, и если да, то путь к нему
    :param graph: рисовать ли график
    :param img_name: сохранять ли графиу, и если да - название файла
    :return:
    """
    slice_window = 14
    diff_len = 0
    memory_diff = deque()  # 0=same, 1=dif
    graph_array = []
    # append, popleft
    with open(path1) as f1:
        if save_folder_path:
            save_path = Path(save_folder_path) / Path(path1).name
            with open(save_path, 'w'):
                pass
        ref_data = json.load(f1)
        line_time = 0
        offset = 0
        words_in_line = []
        line = ''
        # print(ref_data)
        for word_time, word in ref_data.items():
            if floor(float(word_time)) < floor(line_time) + lineDuration:
                for w in word:
                    words_in_line.append(w)
            else:
                if len(words_in_line) < MusFILTER_MINWORDSINSEC * lineDuration:
                    words_in_line = word
                    print('mus')
                    insert, comp_line = music_with_sec_file(path2, line_time, offset)
                    line_time = float(word_time)
                    proc_dist = float(insert)

                else:
                    line = ' '.join(words_in_line)
                    dist_, offset, comp_line = compare_with_sec_file(line, path2, line_time, offset)
                    print(f'offset = {offset}')
                    # dist_ = distance(line1, line2)
                    line_time = float(word_time)
                    proc_dist = dist_ / len(line)

                print(word_time)
                words_in_line.clear()

                num_words1 = len(words_in_line)
                num_words2 = len(comp_line.split())
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
                    print(f"dist = {proc_dist}, len1 = {num_words1}, len2 = {num_words2}", file=sFile)
                    print(f'{line.strip() if line.strip() else "-"}',
                          f'{comp_line.strip() if comp_line.strip() else "-"} \n',
                          sep='\n', file=sFile)

        if graph:
            plt.plot(graph_array)
            if img_name:
                plt.savefig(img_name)
            plt.show()


def compare_prRec(path1, path2) -> [bool, float]:
    """
    На вхож поступают два файла, каждая строка которых является кадром.
    По количеству слов фильтруется содержит ли этот кадр музыку/песню или речь.
    Для каждого кадора вызывается функция `compare_with_sec_file`
    :param path1: путь к 1 файлу
    :param path2: путь ко 2 файлу
    :return: None - если встаки нет, [True, time] - если есть. !!!time не доделано
    """
    # slice_window = 5
    diff_len = 0
    slice_window = deque([0, 0, 0, 0, 0])
    diff_start_point = 0
    getting_down = 0

    with open(path1) as f1:
        ref_data = json.load(f1)
        line_time = 0
        offset = 0
        words_in_line = []
        line = ''
        for word_time, word in ref_data.items():
            if floor(float(word_time)) < floor(line_time) + lineDuration:
                for w in word:
                    words_in_line.append(w)
            else:
                if len(words_in_line) < MusFILTER_MINWORDSINSEC * lineDuration:
                    words_in_line = word
                    print('mus')
                    insert, comp_line = music_with_sec_file(path2, line_time, offset)
                    line_time = float(word_time)
                    proc_dist = float(insert)

                else:
                    line = ' '.join(words_in_line)
                    dist_, offset, comp_line = compare_with_sec_file(line, path2, line_time, offset)
                    print(f'offset = {offset}')
                    line_time = float(word_time)
                    proc_dist = dist_ / len(line)

                # print(word_time)
                words_in_line.clear()

                num_words1 = len(words_in_line)
                num_words2 = len(comp_line.split())
                the_same = bool(proc_dist >= 0.5)

                diff_len -= slice_window.popleft()
                diff_len += int(the_same)
                slice_window.append(int(the_same))

                if diff_len < 2:
                    diff_start_point = line_time


                if diff_len >= 4:
                    return False, diff_start_point

                print(f"dist = {proc_dist}, len1 = {num_words1}, len2 = {num_words2}")
                print(f'{line.strip() if line.strip() else "-"}',
                      f'{comp_line.strip() if comp_line.strip() else "-"} \n', sep='\n')

        return True, -1


if __name__ == '__main__':
    compare_dicts(
        '/home/alexsun8/streamlabs/radioTrans/bigdata/json_txt/json_Анадырь_ЦРВ_Радио_Маяк_2021_04_24T04_00_00_2021_04_24T08_00_00.ts.json',
        '/home/alexsun8/streamlabs/radioTrans/bigdata/json_txt/json_АРВ_Радио_Маяк_2021_04_24T04_00_00_2021_04_24T08_00_00.ts.json',
        save_folder_path='/home/alexsun8/streamlabs/radioTrans/bigdata/json_txt/res', graph=True)
