# -*- coding: utf-8 -*-
#
# Построение диаграммы кол-ва звёзд до 6,5m по спектральным классам.
# Используется датасет 'dataset_bright_stars.csv' https://github.com/dyuk108/brightstar_dataset
# Клыков Д.Ю., 2025.

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from star_colors import * # функции для получения RGB цвета звёзд, см. https://github.com/dyuk108/star_colors

# Читаем датасет dataset_bright_stars.csv
# Индексы столбцов: 0 - Vmag, 1 - RA, 2 - Dec, 3 - B-V .
df = pd.read_csv('dataset_bright_stars.csv', usecols=[21])

# Спектральные классы.
sp_types = ['O', 'B', 'A', 'F', 'G', 'K', 'M', 'Misc'] # Misc - прочие.

# Цвета звёзд соответствующих классов (с цифрой 5).
colors = []
for i in range(7):
    colors.append(t2rgb(sptype2t(sp_types[i] + '5')))
colors.append('#909090') # для прочих классов - серый цвет

# Создаём столбец с обработанным значением 
crop_sp_type = lambda sp_type: sp_type[0].upper() if sp_type[0].upper() in sp_types else 'Misc'
df['SpType_crop'] = df['SpType'].apply(crop_sp_type)

# Количественное распределение по классам.
df_sptypes = df['SpType_crop'].value_counts()
# Упорядочим в соответствии со списком сп. классов.
data_sptypes = []
for sp_type in sp_types:
    data_sptypes.append(int(df_sptypes[sp_type]))

# Построение диаграммы.
sns.set_style("darkgrid", {"axes.facecolor": "#404040"})
sns.barplot(x=sp_types, y=data_sptypes, palette=colors)
plt.xlabel('Спектральные классы')
plt.ylabel('Кол-во звёзд')
plt.title('Распределение спектральных классов звёзд до 6,5m')

plt.show()
