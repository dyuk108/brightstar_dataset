# -*- coding: utf-8 -*-
#
# Построение карты всего неба со звёздами до 6,5m в картографической проекции Моллвейде.
# Используется датасет 'dataset_bright_stars.csv' https://github.com/dyuk108/brightstar_dataset
# Клыков Д.Ю., 2025.

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# Для преобразования координат нужно использовать модуль Astropy https://www.astropy.org/
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table

from star_colors import * # функции для получения RGB цвета звёзд, см. https://github.com/dyuk108/star_colors

# Читаем датасет dataset_bright_stars.csv
# Индексы столбцов: 0 - Vmag, 1 - RA, 2 - Dec, 3 - B-V .
df = pd.read_csv('dataset_bright_stars.csv', usecols=[0, 6, 9, 10, 14])
df['B-V'].fillna(0, inplace=True) # замена отсутствующих значений B-V на 0 (белый цвет) в исходном фрейме
#df.set_index('HIP', inplace=True) # индекс - номер HIP

# Читаем датасет по линиям созведий constellations.csv
# 0 - HIP1, 1 - HIP2, 3 - созвездие
df_lines = pd.read_csv('examples/cst_lines.csv')

# Преобразование в галактические координаты. Удобнее это делать векторной операцией.
df2 = Table.from_pandas(df)
c = SkyCoord(ra = df2['RAdeg'] * u.degree, dec = df2['DEdeg'] * u.degree, frame = "icrs")
c_galactic = c.transform_to("galactic")
df['l'] = c_galactic.l.degree # галакт. долготы
df['b'] = c_galactic.b.degree # галакт. широты

df.set_index('HIP', inplace=True) # индекс - номер HIP

# Преобразум координаты для построения графика.

# RA. У нас градусы от 0 до 360 в обратную сторону. Надо: 0 посередине, -pi слева, pi справа.
# Определяем векторную функцию для преобразования.
l_convert = lambda RA: -np.pi * RA / 180 if RA <= 180 else -np.pi * (RA-360) / 180
df['l_map'] = df['l'].apply(l_convert)

# Dec. Здесь просто превращаем в радианы.
df['b_map'] = np.radians(df['b'])

# Vmag. Преобразование в диаметр кружка
gamma = 1.6 # коэффициент уменьшения диаметров звёзд "средних" (3-4m) зв. величин, "гамма-коррекция"
smax = 15 # диаметр кружка звезды 0m
df['Vmag_map'] = df['Vmag'].apply(lambda Vmag: ((6.6 - Vmag)/6.6)**gamma * smax)

# Цвет звёзд определяется из показателя B-V. Требуется получить цвет RGB.
df['BV_Teff'] = df['B-V'].apply(bv2t) # сначала определяется цветовая температура
df['BV_map'] = df['BV_Teff'].apply(t2rgb) # по ней определяется цвет RGB

# Рисуем карту.
fig = plt.figure()
ax = fig.add_subplot(111, projection='mollweide')
im=ax.scatter(df['l_map'], df['b_map'], s=df['Vmag_map'], c = df['BV_map'], edgecolors='none')

# Рисуем линии созвездий.
for i in range(df_lines.shape[0]):
    HIP1 = df_lines.loc[i]['HIP1']
    HIP2 = df_lines.loc[i]['HIP2']
    l1 = l_convert(df.loc[HIP1]['l'])
    l2 = l_convert(df.loc[HIP2]['l'])
    if abs(l1-l2) < np.pi: # точки не лежат по обе стороны от нулевого меридиана
        b1 = np.radians(df.loc[HIP1]['b'])
        b2 = np.radians(df.loc[HIP2]['b'])
        ax.add_line(plt.Line2D((l1, l2), (b1, b2), c='#ffffff', alpha=0.4, linewidth = 0.5))

plt.grid(True) # координатная сетка включена
ax.tick_params(colors='#507090', grid_color='#507090', grid_alpha=0.5, labelsize=7) # параметры сетки
ax.set_facecolor('#203050') # цвет фона

# Замена подписей по RA.
axes_old = [np.radians(x) for x in range(-180, 210, 30)]
axes_new = [str(x) + '°' for x in range(180, -30, -30)] + [str(x) + '°' for x in range(330, 150, -30)]
plt.xticks(axes_old, axes_new)

plt.show()