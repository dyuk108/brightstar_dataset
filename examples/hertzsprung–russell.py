# -*- coding: utf-8 -*-
#
# Построение диаграммы Герцшпрунга-Рассела ("спектр-светимость") со звёздами всего неба до 6,5m.
# Используется датасет 'dataset_bright_stars.csv' https://github.com/dyuk108/brightstar_dataset
# Клыков Д.Ю., 2025.

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from star_colors import * # функции для получения RGB цвета звёзд, см. https://github.com/dyuk108/star_colors

# Читаем датасет dataset_bright_stars.csv
# Индексы столбцов: 0 - Vmag, 1 - RA, 2 - Dec, 3 - B-V .
df = pd.read_csv('dataset_bright_stars.csv', usecols=[0, 6, 9, 10, 14])
df['B-V'].fillna(0, inplace=True) # замена отсутствующих значений B-V на 0 (белый цвет) в исходном фрейме
df.set_index('HIP', inplace=True) # индекс - номер HIP

# Vmag. Преобразование в диаметр кружка
gamma = 1.6 # коэффициент уменьшения диаметров звёзд "средних" (3-4m) зв. величин, "гамма-коррекция"
smax = 12 # диаметр кружка звезды 0m
df['Vmag_map'] = df['Vmag'].apply(lambda Vmag: ((6.6 - Vmag)/6.6)**gamma * smax)

# Цвет звёзд определяется из показателя B-V. Требуется получить цвет RGB.
df['BV_Teff'] = df['B-V'].apply(bv2t) # сначала определяется цветовая температура
df['BV_map'] = df['BV_Teff'].apply(t2rgb) # по ней определяется цвет RGB

# Не для всех звёзд есть значения цветовой температуры. Если отсутствует - определяем по сп. классу.
# Допишу позже...

# Рисуем карту.
fig = plt.figure()
ax = fig.add_subplot(111, projection='mollweide')
im=ax.scatter(df['RA_map'], df['Dec_map'], s=df['Vmag_map'], c = df['BV_map'], edgecolors='none')
plt.grid(True) # координатная сетка включена
ax.tick_params(colors='#507090', grid_color='#507090', grid_alpha=0.5, labelsize=7) # параметры сетки
ax.set_facecolor('#203050') # цвет фона

# Замена подписей по RA.
axes_old = [np.radians(x) for x in range(-180, 210, 30)]
axes_new = [str(x) + '°' for x in range(180, -30, -30)] + [str(x) + '°' for x in range(330, 150, -30)]
plt.xticks(axes_old, axes_new)

plt.show()