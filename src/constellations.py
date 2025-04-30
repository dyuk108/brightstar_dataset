# -*- coding: utf-8 -*-
#
# Класс Constellations, содержащщий список созвездий и их границ.
# Дмитрий Клыков, 2025. dyuk108.ru

from shapely import geometry # модуль для работы с геометрией
import os

class Constellations:
    # Функция, читающая из файла filename точки, обозначающие границы созвездий,
    # и выдающая их в виде списка.
    # Читаем файлы из папки boundaries . Имя файла: краткое название созвездия .txt
    # Источник: https://iau.org/public/themes/constellations/
    # Сграбены скриптом getBoundaries.py , нужно запустить, чтобы в папке появились 89 файлов .txt
    def getPolygon(self, filename):
        polygon = [] # список точек, который надо прочитать
        
        f = open(filename, 'r')
        counter = 0 # счётчик строк
        for s in f: # по строкам
            counter += 1
            # строка имеет вид: 22 57 51.6729| 35.1682358|AND 
            dataPoint = s.rstrip().split('|')
            dataRA = dataPoint[0].strip().split()
            try:
                RA = (int(dataRA[0]) + int(dataRA[1])/60 + float(dataRA[2])/3600) * 15 # переводим Ч М С в градусы
                Dec = float(dataPoint[1])
            except:
                # print(f'Ошибка данных в строке {counter} файла {filename}')
                # В реальности в двух файлах ошибки вылезают из-за пустых строк. Игнорируем их.
                continue
            polygon.append((RA, Dec))
        f.close()
        return polygon
    
    # Функция проверки, проходит ли через созвездие нулевой мередиан. Кроме полярных (М. Медведица, Октант).
    # По результатам получились созвездия: Андромеда, Кассиопея, Цефей, Кит, Пегас, Феникс, Рыбы, Скульптор, Тукан.
    # Если проходит, возвращает истину.
    def check0RA(self, shortname):
        if shortname == 'UMa' or shortname == 'Oct':
            return False # для них отдельная коррекция
        minRA = 360
        maxRA = 0
        polygon = self.clist[shortname]['polygon']
        for i in range(len(polygon)):
            minRA = min(minRA, polygon[i][0])
            maxRA = max(maxRA, polygon[i][0])
        if minRA < 90 and maxRA > 270:
            return True
        else:
            return False

    # Функция "нормализации" координат точек по RA.
    # Для того, чтобы к массиву можно было применять функции модулей, работающих с декартовой
    # системой координат, нужно преодолеть проблему "разрыва" RA в мередиане 0.
    # То есть есть созвездия, по которым проходит этот меридиан (Кассиопея, Андромеда, Пегас и др.),
    # нужно, чтобы не было перехода от 360 градусов к 0 градусам по RA.
    # Решение: перевести для этих созвездий координаты с RA > 180 в отрицательные (-360).
    # Для остальных созвездий изменения не производятся.
    # Функция возвращает копию (!) списка точек.
    def normPolygon(self, shortname):
        polygon = self.clist[shortname]['polygon']
        norm = polygon.copy()

        # Отдельная коррекция для созвездий, содержащий полюса мира: М.Медведецы и Октанта.
        # Отображая в декартовых координатах (в них работает )
        if shortname == 'UMi':
            line = [(360, polygon[15][1]), (360, 90), (0, 90), (0, polygon[15][1])]
            norm = norm[:16] + line + norm[16:]
        elif shortname == 'Oct':
            line = [(360, polygon[10][1]), (360, -90), (0, -90), (0, polygon[10][1])]
            norm = norm[:11] + line + norm[11:]
        elif self.check0RA(shortname): # Проверка, проходит ли нулевой мередиан через созвездие (кроме двух полярных).
            # print('0-й мередиан проходит:', shortname)
            # Заменяем точку на точку с отрицательным RA.
            for i in range(len(norm)): # пробегаемя по точкам
                if norm[i][0] > 270: # заменяем точки с координатами, близкими к RA = 360, на отрицательные
                    norm[i] = (norm[i][0] - 360, norm[i][1])
        return norm

    # Конструктор.
    def __init__(self):
        # Список созвездий clist - словарь словарей. Первый ключ - сокращённое (3 буквы) название маленькими буквами.
        # Второй ключ - одна из характеристик созвездия. Они перечислены в заголовке файла
        # 'short_name', 'lat_name', 'rus_name' . Можно добавить в файл ещё столбцы и они отобразятся в словаре.
        # Затем будет добавлена характеристика 'polygon' с границами созвездия.
        self.clist = dict()

        f = open('src/my_data/constellations.csv', 'r', encoding='utf-8')
        headers = f.readline().rstrip().split(',') # первая строка - заголовок таблицы, ключи для словарей
        # Можно добавить ещё столбец во всю таблицу и он встанет в словарь сам.
        lenCons = len(headers) # кол-во столбцов таблицы
            
        for i in range(88): # по кол-ву созвездий
            dataCons = f.readline().rstrip().split(',') # в стандартных csv разделитель запятая
            if len(dataCons) != lenCons: # битая строка (такого не может быть :-))
                print(f'Строка файла constellations.csv {i+2} битая. Пропущена.')
                continue
                        
            # Трёхбуквеннве обозначения созвездий - для имён файлов.
            #self.clist[dataCons[0].lower()] = {headers[i]: dataCons[i] for i in range(lenCons)}
            self.clist[dataCons[0]] = {headers[i]: dataCons[i] for i in range(lenCons)}
            
        f.close()

        # Для Змеи имена ser1.txt и ser1.txt (два участка).
        for key in self.clist: # по созвездиям
            if key != 'Ser': # Змея
                filename = 'src/boundaries/' + key.lower() + '.txt'
            else:
                filename = 'src/boundaries/ser1.txt' # второй кусок Змеи добавим после
            if not os.path.isfile(filename):
                print(f'Не найден файл {filename} . Пропуск.')
                continue
            self.clist[key]['polygon'] = self.getPolygon(filename) # добавляем в словарь массив точек
            self.clist[key]['polygon_norm'] = self.normPolygon(key) # добавляем в словарь массив точек

            if key == 'Ser' and os.path.isfile('src/boundaries/ser2.txt'): # ох уж эта Змея, добавляем второй кусок
                self.clist[key]['polygon2'] = self.getPolygon('src/boundaries/ser2.txt') # добавляем в словарь массив точек
                self.clist[key]['polygon2_norm'] = self.clist[key]['polygon2'].copy() # здесь просто копия

    
    # Функция, определяющая принадлежность точке с указанными координатами, тому или иному созвездию.
    # Выдаёт строку из краткого названия созвездия (маленькими буквами).
    # Если необязательный параметр ser установлен в True, то для Змеи выдаётся 'ser1' или 'ser2'
    # в зависимости от участка. В противном случае просто 'ser'.
    def whatCons(self, RA, Dec, ser = False):
        sCons = None # Возвращаемое значение. None не должно остаться, должно определиться.

        # Проходим циклом по созвездиям, на какой участок попадёт, тот и будет ответом.
        # Для начала каждый раз будем прогонять полным циклом, вдруг будет ошибка и определится более одного созвездия.
        for key in self.clist:
            RA_norm = RA
            # Если по созвездию проходит 0-й мередиан, корректируем RA.
            if self.check0RA(key) and RA > 270:
                RA_norm = RA - 360

            # Работа с библиотекой shapely.
            line = geometry.LineString(self.clist[key]['polygon_norm'])
            point = geometry.Point(RA_norm, Dec)
            polygon = geometry.Polygon(line)
            if polygon.contains(point): # если точка внутри фигуры
                sCons = key # краткое название
                if key == 'Ser' and ser:
                    sCons = 'Ser1' # если нужно знать, какая часть; ser1 - "правая" Змея 
                break # нашли - больше не ищем

        # Вторая Змея ("левая")
        if sCons is None: # если ни один перечисленный участок не подошёл, проверм левую Змею
            line = geometry.LineString(self.clist['Ser']['polygon2_norm'])
            point = geometry.Point(RA, Dec)
            polygon = geometry.Polygon(line)
            if polygon.contains(point): # если точка внутри фигуры
                sCons = 'Ser' # краткое название
                if ser:
                    sCons = 'Ser2' # если нужно знать, какая часть; ser2 - "левая" Змея 

        if sCons is None: # если ни один участок не опознан (такого не должно быть)
            print(f'Для точки {RA} {Dec} не найдено ни одно созвездие.')
        return sCons
