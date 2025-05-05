# -*- coding: utf-8 -*-
#
# Построение диаграммы Герцшпрунга-Рассела звёзд до 6,5m.
# Используется датасет 'dataset_bright_stars.csv' https://github.com/dyuk108/brightstar_dataset
# Клыков Д.Ю., 2025.

#import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from star_colors import * # функции для получения RGB цвета звёзд, см. https://github.com/dyuk108/star_colors

# Словарь греческих букв - написание латиницей как в доп файле ident4.doc для Hip.
greek_hip = {'alf': 'α', 'bet': 'β', 'gam': 'γ', 'del': 'δ', 'eps': 'ε', 'zet': 'ζ', \
        'eta': 'η', 'the': 'θ', 'iot': 'ι', 'kap': 'κ', 'lam': 'λ', 'mu.': 'μ', \
        'nu.': 'ν', 'ksi': 'ξ', 'omi': 'ο', 'pi.': 'π', 'rho': 'ρ', 'sig': 'σ', \
        'tau': 'τ', 'ups': 'υ', 'phi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'ome': 'ω' }

# Функция, заменяющая обозначения по Байеру, сделанные лат. буквами, на греческие.
def to_greek(s):
    s1 = '' # Буквы.
    s2 = '' # Цифры.
    for sym in s:
        if sym.isdigit(): # Могут встретиться цифры - их отделяем.
            s2 += sym
        else:
            s1 += sym
    if s1.lower() in greek_hip:
        s1 = greek_hip[s1.lower()]
    s2 = s2.lstrip('0') # Убираем незначащий 0.
    return s1 + s2

# Читаем датасет dataset_bright_stars.csv
df = pd.read_csv('dataset_bright_stars.csv', usecols=[0, 2, 3, 4, 6, 11, 14, 21, 22, 24])
# Заменяем пропущенные значения Teff типичной температурой этого спектрального класса.
df['Teff'] = df['Teff'].fillna(df['SpType'].map(sptype2t))

# Вычисляем абсолютную зв. величину.
# Нам не нужны строки с отсутствующими параллаксами.
df = df.dropna(subset=['Plx']) # таких 4
# Есть небольшое кол-во звёзд, у которых отрицательный параллакс. То есть
# ошибка больше, чем его небольшое значение. Убираем такие строки.
df = df.drop(df[df['Plx'] <= 10].index) # также и для очень маленького параллакса получается очень большое расстояние. Избавляемся
df['Plx'] = df['Plx'].astype(float)
df['Vmag'] = df['Vmag'].astype(float)
df['M'] = df['Vmag'] + 5 + 5 * np.log10(df['Plx'] * 0.001) # Параллакс дан в угл. миллисекундах.

# Цвет звёзд определяется из показателя B-V. Требуется получить цвет RGB.
df['B-V'] = df['B-V'].fillna(0) # есть несколько строк, где нет B-V. Поставим 0 - белый цвет.
df['BV_Teff'] = df['B-V'].apply(bv2t) # сначала определяется цветовая температура
df['Color'] = df['BV_Teff'].apply(t2rgb) # по ней определяется цвет RGB

# Диаметры кружков
df['Vmag_r'] = (6.6 - df['Vmag']) * 2

df['Teff'] = df['Teff'].astype(float)
df['M'] = df['M'].astype(float)
df['Fl'] = df['Fl'].astype(str)
df['Bayer'] = df['Bayer'].astype(str)
df['Bayer_cst'] = df['Bayer_cst'].astype(str)
df['Name_r'] = df['Name_r'].astype(str)

# Всплывающие названия звёзд. Если есть - обозначение по Байеру, нет - по Флемстиду. И если есть - собственное название.

# Заменяем обозначения в 'Bayer' на греческие буквы.
df['Bayer'] = df['Bayer'].apply(to_greek)

# Добавляем колонку с Bayer + созвездие
label_bayer = lambda Bayer, Bayer_cst: Bayer + ' ' + Bayer_cst if Bayer != 'nan' and Bayer_cst != 'nan' else ''
df['Label'] = df.apply(lambda x: label_bayer(x['Bayer'], x['Bayer_cst']), axis =  1)

# Добавляем в строки этой колонки название звезды, если есть.
label_name = lambda Label, Name: f'{Label} ({Name})' if Name != 'nan' else Label
df['Label'] = df.apply(lambda x: label_name(x['Label'], x['Name_r']), axis =  1)

# И уж если нет никаких названий-обозначений, указывается номер по HIP.
label_name = lambda Label, HIP: Label if Label != '' else f'HIP {HIP}'
df['Label'] = df.apply(lambda x: label_name(x['Label'], x['HIP']), axis =  1)

# Построение диаграммы.
# Параметры, которые нужны для построения: Teff, M (абс. зв. вел-на), цвет RGB по B-V, Vmag (размер кружка).
fig = go.Figure(data=go.Scatter(
    x = df['Teff'],
    y = df['M'],
    mode = 'markers',
    marker = dict(size=df['Vmag_r'], color = df['Color'], line=dict(width=0)),
    text = df['Label']
))

fig.update_layout(
    xaxis=dict(type='log', autorange='reversed', gridcolor='#404040', zeroline=False, title_text = "Эффективная температура Teff"),
    yaxis=dict(autorange='reversed', gridcolor='#404040', zeroline=False, title_text = "Абсолютная зв. величина M"),
    plot_bgcolor='#101010'
)

fig.show()
