# -*- coding: utf-8 -*-
#
# Скрипт генерирует датасет CSV из нескольких звёздных каталогов, 
# основной из которых - Hipparcos. Ограничение - до 6,5m.
#
# Предназначен для учебных целей. На основе такого датасета можно
# тренироваться в работе с даннами при помощи библиотек наподобие pandas,
# и СУБД, наподобие DuckDB, строить карты и диаграммы.
# Можно сделать просто справочник по ярким звёздам и созвездиям.
#
# Дмитрий Клыков, 2025. dyuk108.ru

# Имена файлов используемых каталогов.
filename_hip = 'src/hipparcos/hip_main.dat' # Hipparcos
filename_hip_var = 'src/hipparcos/ident5.doc'# файл из комплекта Hip с обозначениями переменных звёзд
filename_cross = 'src/cross/catalog.dat' # IV/27A HD-DM-GC-HR-HIP-Bayer-Flamsteed Cross Index (Kostjuk, 2002)
filename_constell = 'src/my_data/constellations.csv' # список созвездий с сокращёнными названиями
filename_pastel = 'src/pastel/pastel.dat' # обработанный каталог PASTEL
filename_proper_names = 'src/my_data/star_names_wiki_rus.csv' # список собственных названий звёзд, в т.ч. на русском

# -----------------------------------
# Полезные запчасти.
# -----------------------------------
# Функция убирает нули в начале строки (незначащие нули чисел).
def ins_zeros(s):
    sw = ''
    for i in range(len(s)):
        if not(0 <= i <= 1 and s[i] == '0' and sw == ''):
            sw += s[i]
    return sw

# Словарь греческих букв - написание латиницей как в доп файле ident4.doc для Hip.
greek_hip = {'alf': 'α', 'bet': 'β', 'gam': 'γ', 'del': 'δ', 'eps': 'ε', 'zet': 'ζ', \
        'eta': 'η', 'the': 'θ', 'iot': 'ι', 'kap': 'κ', 'lam': 'λ', 'mu.': 'μ', \
        'nu.': 'ν', 'ksi': 'ξ', 'omi': 'ο', 'pi.': 'π', 'rho': 'ρ', 'sig': 'σ', \
        'tau': 'τ', 'ups': 'υ', 'phi': 'φ', 'chi': 'χ', 'psi': 'ψ', 'ome': 'ω' }

# Массив сокращённых названий созвездий (с большими и мал буквами).
constellations = []
fc = open(filename_constell, encoding='utf-8')
for s in fc:
    l = s.split(',')
    if len(l) < 3 or l[0] == 'short_name':
        continue
    constellations.append(l[0])
fc.close()

# Объект для работы с созвездиями.
from constellations import Constellations
cons = Constellations() # объект с каталогом созвездий

# ----------------------------------------------------------------------------
# Сформируем окончательный список полей, который нам нужен на основе keys_hip.
# ----------------------------------------------------------------------------
keys_compiled = [
            'HIP', # номер по HIP
            'HD', # номер по HD
            'Fl', # обозначение по Флемстиду (номер)
            'Bayer', # обозначение по Байеру (греч. буква, компонент (если есть))
            'Bayer_cst', # созвездие в обозначении по Байеру (три буквы)
            'Cst', # созвездие в настоящую эпоху (три буквы)
            'Vmag', # Magnitude in Johnson V
            'VarFlag', # Var star: < 0.06mag ; 2: 0.06-0.6mag ; 3: >0.6mag
            'VarID', # Variable star name
            'RAdeg', # alpha, degrees (ICRS, Epoch=J1991.25)
            'DEdeg', # delta, degrees (ICRS, Epoch=J1991.25)
            'Plx', # Trigonometric parallax
            'pmRA', # Proper motion mu_alpha.cos(delta), ICRS
            'pmDE', # Proper motion mu_delta, ICRS
            'B-V', # Johnson B-V colour
            'V-I', # Johnson B-V colour
            'Period', # Variability period (days)
            'HvarType', # [CDMPRU]? variability type
            #'CCDM', # CCDM identifier
            'Ncomp', # Number of components in this entry
            'MultFlag', #  Double/Multiple Systems flag
            'm_HIP', # Component identifiers
            #'theta', # Position angle between components
            #'rho', # Angular separation between components
            #'dHp', # Magnitude difference of components
            'SpType', # Spectral type
            'Teff', # Эффективная температура
            'Name', # Оригинальное собственное имя
            'Name_r'] # Русское собственное имя

# -----------------------------------------------------------
# Hipparcos - основной каталог.
# -----------------------------------------------------------
# Почему не Tycho или Tycho-2? Они практически совпадают до 6,5m. 
# В Hipparcos больше данных о звёздах, например, есть спектральные классы.
fields_hip = (('HIP', 9, 14), # Identifier (HIP number)
            #('RAhms', 18, 28), # Right ascension in h m s, ICRS (J1991.25)
            #('DEdms', 30, 40), # Declination in deg ' ", ICRS (J1991.25)   (H4)
            ('Vmag', 42, 46), # Magnitude in Johnson V
            ('VarFlag', 48, 48), # Var star: < 0.06mag ; 2: 0.06-0.6mag ; 3: >0.6mag
            ('RAdeg', 52, 63), # alpha, degrees (ICRS, Epoch=J1991.25)
            ('DEdeg', 65, 76), # delta, degrees (ICRS, Epoch=J1991.25)
            ('Plx', 80, 86), # Trigonometric parallax
            ('pmRA', 88, 95), # Proper motion mu_alpha.cos(delta), ICRS
            ('pmDE', 97, 104), # Proper motion mu_delta, ICRS
            #('BTmag', 218, 223),  # Mean BT magnitude
            #('VTmag', 231, 236), # Mean VT magnitude
            ('B-V', 246, 251), # Johnson B-V colour
            ('V-I', 261, 264), # Johnson B-V colour
            ('Period', 314, 320), # Variability period (days)
            ('HvarType', 322, 322), # [CDMPRU]? variability type
            #('CCDM', 328, 337), # CCDM identifier
            #('Nsys', 341, 342), # Number of entries with same CCDM
            ('Ncomp', 344, 345), # Кол-во компонентов в этой строке
            ('MultFlag', 347, 347), #  Double/Multiple Systems flag
            ('m_HIP', 353, 354), # Буквенные обозначения компонентов (если два)
            #('theta', 356, 358), # Position angle between components
            #('rho', 360, 366), # Angular separation between components
            #('dHp', 374, 378), # Magnitude difference of components
            ('HD', 391, 396), # [1/359083]? HD number <III/135>
            ('SpType', 436, 447)) # Spectral type

# Создаём словарь для окончательного датасета. Ключ - номер HIP.
# Значение - словарь полей строки каталога.
df_compiled = dict()
# Кросс-словарь, ключ - номер HD, значение - номер HIP
cross_hd_hip = dict()

f = open(filename_hip)
for s in f:
    if len(s) < 5: # пустые строки
        continue

    data = dict() # строка каталога
    for field in fields_hip: # по полям данных строки
        data[field[0]] = s[field[1]-1 : field[2]].strip()

    # Нужно разобраться с Vmag: ограничиваем до 6.5m.
    try:
        Vmag_float = float(data['Vmag'])
    except:
        continue # только странный объект HIP 120412 без Vmag, координат и много чего.

    if Vmag_float <= 6.5:
        HIP = data['HIP']
        # Координаты в градусах RAdeg и DEdeg почему-то не во всех строках есть. 
        # поэтому в случае отсутствия считаем из 
        if data['RAdeg'] == '':
            RA = round((int(s[17:19]) + int(s[20:22])/60 + float(s[23:28])/3600) * 15, 8) # RA в градусах
            data['RAdeg'] = str(RA)
        else: # уберём незначащие нули
            data['RAdeg'] = ins_zeros(data['RAdeg'])
            RA = float(data['RAdeg']) # в виде числа с плавающей точкой тоже будет нужно

        if data['DEdeg'] == '':
            Dec = round(int(s[29:32]) + int(s[33:35])/60 + float(s[36:40])/3600, 8) # Dec в градусах
            data['DEdeg'] = str(Dec)
        else:
            Dec = float(data['DEdeg']) # в виде числа с плавающей точкой тоже будет нужно

        # Формируем строку окончательного датасета и помещаем туда имеющиеся данные из Hip.
        data_compiled = dict.fromkeys(keys_compiled, '')
        for key in data_compiled:
            if key in data:
                data_compiled[key] = data[key]

        # Автоматическое определение созвездия.
        data_compiled['Cst'] = cons.whatCons(RA, Dec)

        df_compiled[HIP] = data_compiled # записываем в окончательный датасет

        # Кросс-словарь HD -> HIP
        HD = data['HD']
        if HD != '':
            if not(HD in cross_hd_hip):
                cross_hd_hip[HD] = HIP
            else:
                print(f'HD {HD} дублируется, было HIP {cross_hd_hip[HD]}, записываетя {HIP}')
        # Оказалось, что до 6,5m дубликатов HD нет.
f.close()
# Единственное исправление, которое я себе позволю в данных Hip, это спектральный класс эпсилон Волопаса.
# Указано A0 - класс слабого (5m) компонента. Яркий компонент (2,7m) имеет класс K0.
df_compiled['72105']['SpType'] = 'K0II-III'

# --------------------------------------------------------------------
# Оббозначение звёзд по Байеру и Флемстиду.
# Нужно а) дополнить словарь каталога HIP;
# б) сделдать словарь, ключ - обозначение по Байеру/Флемстиду, значение - HIP.
# --------------------------------------------------------------------
cross_bayer_hip = dict() # словарь для работы с каталогом PASTEL

fields_cross = (('HD', 1, 6), #  Henry Draper Catalog Number <III/135>
    ('HIP', 32, 37), # Hipparcos Catalog <I/196> number
    ('Fl', 65, 67), # Flamsteed number (G1)
    ('Bayer', 69, 73), # Bayer designation (G1)
    ('Bayer_cst', 75, 77)) # Constellation abbreviation (G1)

f = open(filename_cross)
for s in f:
    if len(s) < 3: # пустая строка
        continue

    data = dict() # строка каталога
    for field in fields_cross: # по полям данных строки
        data[field[0]] = s[field[1]-1 : field[2]].strip()
    HIP = data['HIP']
    
    if data['HIP'] in df_compiled: # запись в основной датасет
        # Созвездие.
        df_compiled[HIP]['Bayer_cst'] = data['Bayer_cst']

        # Обозначения по Байеру.
        if data['Bayer'] != '':
            # Разрешаем конфликты.
            if HIP == '40167':
                # HIP 40167 zet02 Cnc и zet01 Cnc
                # Это система из 5 компонентов, zet01 Cnc - более яркая пара.
                df_compiled['40167']['Bayer'] = 'zet'
                cross_bayer_hip['zet01 Cnc'] = '40167'
            elif HIP == '76669':
                # HIP 76669 zet01 CrB и zet02 CrB .
                # Здесь более яркая звезда zet02 CrB.
                df_compiled['76669']['Bayer'] = 'zet'
                cross_bayer_hip['zet02 CrB'] = '76669'
            else:
                df_compiled[HIP]['Bayer'] = data['Bayer']
                df_compiled[HIP]['Bayer_cst'] = data['Bayer_cst']
                key = data['Bayer'] + ' ' + data['Bayer_cst']
                cross_bayer_hip[key] = HIP

        # Обозначения по Флемстиду.
        if data['Fl'] != '':
            df_compiled[HIP]['Fl'] = data['Fl']
            key = data['Fl'] + ' ' + data['Bayer_cst']
            cross_bayer_hip[key] = HIP

        # Конфликты, обнаруженные ранее.
        # HIP 33485 по Байеру - пси Возничего, по Флемстиду - 16 Рыси. Реально на границе,
        # но всё же на территории Рыси. В данном каталоге конфликт уже разрешён в пользу Флемстида.

        # HIP 7607 по Байеру - упсилон Персея, по Флемстиду - 51 And. Находится даже не на границе,
        # а вполне себе внутри территории созвездия Андромеды.
        # В данном каталоге конфликт уже разрешён в пользу Флемстида.
f.close()

# -------------------------------------
# Добавляем в основной датасет обозначение VarID.
# -------------------------------------
f = open(filename_hip_var)
for s in f:
    if len(s) < 3: # пустая строка
        continue

    var_id, HIP = s.split('|')
    var_id = var_id.strip().replace('_', ' ')
    var_id = var_id.replace('  ', ' ')
    HIP = HIP.strip()

    if HIP in df_compiled:
        df_compiled[HIP]['VarID'] = var_id

        # Добавляем и в кросс-словарь ключами VarID, значения - HIP.
        if not(var_id in cross_bayer_hip):
            cross_bayer_hip[var_id] = HIP
f.close()

fw = open('cross_bayer_hip.csv', 'w')
for key in cross_bayer_hip:
    fw.write(key + ',' + cross_bayer_hip[key] + '\n')
fw.close()
# ------------------------------------------------------------------
# PASTEL - каталог, откуда можно взять температуру поверхности Teff.
# ------------------------------------------------------------------
# Исключения в номерах HD. Иногда указаны буквы компонента, которых нет в Hip.
except_hd = {'123A': '518',
'26015B': '19261', # 5250 F3V
'28255B': '20552', # 5658 G4V+...
'75289A': '43177', # 5963 G0Ia0:
'97334B': '54745', # 5905 G0V
'101177A': '56809', # 5964 G0V
'115404B': '64797', # 3903 K2V
'176051A': '93017', # 5922 G0V
'216172B': '112670'} # 6983 F5

except_bayer = {
'iot Tri': '10280', # 4.952 5.741 5082
'192 Gem': '37636', # 6.229 7.167 4922
'65 Psc B': '3885', # 6.276 6.692 6671
'ups Per': '7607', # 3.57 4.85 4310
'eps Equ A': '103569', # 5.96 6.48 6223
'TX Pic': '26300', # 6.100 7.261 4435
'gam02 Cae': '23596', # 6.314 6.607 6973
'zet Her A': '81693', # 2.88 3.52 5764
'16 Cyg B': '96901', # 6.20 6.86 5783
'24 Sex': '50887', # 6.441 7.400 5061
'zet Cnc': '40167', #  5.20 6192
'gam Leo': '50583', # 2.37 3.79 4341
'mu. Cyg': '107310', # 4.50 4.97 6366
'zet Aqr': '110960', # 3.65 4.06 6651
'lam Tuc': '4293', # 5.454 6.537 4631
'zet Psc A': '5737', #   7177
'zet Psc B': '5743', # 6.32 6.80 5663
'DT Psc': '5772', # 6.347 8.016 3600
'p Eri A': '7751', # 5.685 6.549 4970
'59 And B': '10176', # 6.10 6.03 9226
'30 Ari A': '12189', # 6.48 6.86 6695
'eps Ari A': '13914', # 5.16 5.21 8954
'52 Ari A': '14376', # 5.470 5.438 12912
'V521 Per': '14544', # 6.375 6.492 8570
'alf For A': '14879', # 3.98 4.51 6195
'32 Eri A': '18255', # 4.79 5.73 4900
'ome02 Tau': '19990', # 4.914 5.170 7541
'del02 Tau': '20542', # 4.80 4.95 7840
'kap01 Tau': '20635', # 4.201 4.366 8204
'kap02 Tau': '20641', # 5.264 5.544 7360
'del03 Tau': '20648', # 4.298 4.369 7754
'228 Eri': '20922', # 5.41 5.23 24210
'V1116 Tau': '21459', # 6.019 6.418 6745
'c Tau': '21589', # 4.27 4.39 7990
'EX Eri': '22192', # 6.173 6.347 7798
'omi Ori': '22667', # 4.721 6.458 3452
'iot Pic A': '22531', # 5.23 5.56 7014
'ome Aur': '23179', # 4.989 5.008 9230
'V1649 Ori': '25205', # 6.334 6.455 8730
'psi01 Ori': '25302', # 4.96 4.76 25293
'psi02 Ori': '25473', # 4.611 4.398 24130
'AF Lep': '25486', # 6.295 6.832 6100
'lam Ori A': '26207', # 3.47 3.48 34000
'29 Dor': '26368', # 6.274 6.221 10116
'AC Lep': '28434', # 6.195 6.548 6816
'eps Mon A': '30419', # 4.398 4.583 7762
'V350 CMa': '32144', # 6.23 6.56 6952
'87 Gem': '32968', # 5.671 7.142 4061
'V415 Car': '32761', # 4.408 5.323 5044
'psi10 Aur': '33485', # 4.893 4.919 9204
'19 Lyn A': '35785', # 5.78 5.69 12078
'ups01 Pup': '35363', # 4.67 4.57 22828
'alf Gem A': '36850', # 1.9  10069
'n Pup A': '36817', # 5.770 6.200 6409
'k01 Pup': '37229', # 4.50 4.33 15996
'DD Lyn': '38723', # 6.221 6.478 6968
'ome02 Cnc': '39263', # 6.297 6.328 9354
'mu.02 Cnc': '39780', # 5.30 5.93 4755
'phi02 Cnc B': '41404', # 6.186 6.31 8147
'30 Mon': '41307', # 3.90 3.88 9663
'pi.02 Cnc': '45410', # 5.348 6.664 4291
'128 Car': '45571', # 5.38 5.795 6639
'BF Ant': '48776', # 6.312 6.481 7745
'HN Leo': '48895', # 6.460 6.800 6893
'39 Leo A': '50384', # 5.81 6.30 6128
'ksi UMa A': '55203', # 4.264 4.81 5793
'17 Crt A': '56280', # 5.58 6.11 6240
'12 Mus': '56862', # 5.095 5.863 5282
'IQ Vir': '58002', # 6.290 6.489 7223
'UY UMi': '59767', # 6.259 6.590 6920
'24 Com A': '61418', # 5.02 6.17 4480
'gam Vir A': '61941', # 3.440 3.80 6811
'DT CVn': '62641', # 5.872 6.025 7600
'MO Hya': '62788', # 6.141 6.358 7450
'alf Com A': '64241', # 4.85 5.34 6365
'zet01 UMa': '65378', # 2.220 2.271 9340
'alf Cen A': '71683', # 0.01 0.72 5519
'alf Cen B': '71681', # 1.33 2.21 4970
'zet Boo B': '71795', # 4.51 4.59 8990
'26 Cir': '72773', # 5.96 6.66 5648
'ksi Boo A': '72659', # 4.675 5.40 5480
'kap Lup': '74376', # 3.70 3.67 10280
'iot02 Lib': '74493', # 6.066 6.190 8511
'eta CrB A': '75312', # 5.577 6.123 6037
'zet01 Lib': '75730', # 5.626 7.161 4230
'zet03 Lib': '75944', # 5.806 6.858 4935
'HR Lib': '78078', # 6.117 6.345 7240
'ome Sco': '78933', # 3.97 3.92 27460
'kap Her A': '79043', # 4.994 5.927 4990
'sig CrB A': '79607', # 5.55 6.14 5923
'V872 Ara': '81650', # 6.29 6.58 7100
'17 Dra A': '81290', # 5.387 5.318 10568
'V2542 Oph': '82693', # 6.24 6.52 7345
'VX UMi': '83317', # 6.180 6.480 7000
'36 Oph A': '84405', # 5.08 5.93 5091
'alf Her A': '84345', # 3.350 4.51 3271
'41 Ara': '84720', # 5.48 6.28 5131
'omi Oph A': '84626', # 5.20 6.30 4849
'psi01 Dra A': '86614', #  5.00 5928
'psi02 Dra': '86620', # 5.430 5.750 6874
'tau Oph A': '88404', # 5.27 5.70 6545
'gam01 Sgr': '88567', # 4.69 5.47 6632
'gam02 Sgr': '88635', # 2.99 4.00 4760
'b Her A': '88745', # 5.13 5.67 5943
'100 Her A': '88817', # 5.819 5.966 8204
'V346 Pav': '90304', # 6.122 6.313 7471
'd Ser A': '90441', # 5.322 5.839 5780
'eps01 Lyr A': '91919', # 4.991 5.111 7943
'V1691 Aql': '95453', # 6.499 6.831 6955
'iot01 Cyg': '95656', # 5.75 5.75 9683
'bet Cyg B': '95951', # 5.11 5.01 11429
'chi Aql A': '96957', # 5.66 6.66 6203
'16 Cyg A': '96895', # 5.95 6.59 5670
'57 Aql A': '97966', # 5.71 5.63 13552
'b Sgr': '98162', # 4.528 5.980 4350
'60 Sgr A': '98353', # 4.846 5.735 5060
'omi Cap A': '101123', # 5.897 5.969 8913
'61 Cyg A': '104214', # 5.21 6.39 4236
'61 Cyg B': '104217', # 6.03 7.40 3652
'V372 Peg': '107558', # 6.174 6.507 6873
'kap01 Ind': '108478', # 6.141 6.607 6401
'53 Aqr B': '110778', # 6.32 6.96 5727
'8 Lac B': '111546', # 5.67 5.52 18836
'DQ Gru': '115510', # 6.108 6.364 7191
'V1022 Cas': '118077', # 5.561 6.033 6327
}
dict_hip_teff = dict() # словарь, ключ: HIP, значение: массив температур Teff

fields_pastel = (
    ('ID', 1, 33),  # ID звезды
    #('RAdeg', 35, 49), # Right Ascension (J2000)
    #('DEdeg', 51, 65), # Declination (J2000)
    #('Bmag', 69, 74), # Johnson B magnitude from Simbad
    #('Vmag', 83, 88),  # Johnson V magnitude from Simbad
    ('Teff', 141, 145) )  # Effective temperature

f = open(filename_pastel)
for s in f:
    if len(s) < 5: # пустые строки
        continue

    data = dict() # строка каталога
    for field in fields_pastel: # по полям данных строки
        data[field[0]] = s[field[1]-1 : field[2]].strip()

    if data['Teff'] == '': # без эффективной температуры строка не нужна
        continue

    # Обнаружено три строки, где Teff - не цифра или слишком маленькое (7 и 1). Убираем.
    try:
        Teff_float = float(data['Teff'])
    except:
        continue
    if Teff_float < 2000:
        continue

    # Переводим обозначение ID, которые записывались авторами как попало, в HIP.
    ID = data['ID']
    HIP = ''
    
    if ID[:3] == 'HIP':  # Номер по HIP.
        HIP = ID[3:].strip()
    
    elif ID[:2] == 'HD': # Номер по HD.
        HD = ID[2:].strip()
        if HD in cross_hd_hip:
            HIP = cross_hd_hip[HD]
        elif HD in except_hd: # бывает, что указана буква компонента
            HIP = except_hd[HD] # смотрим в исключениях
        # Остальные HD игнорируются, их нет в нашем датасете.

    elif ID[0] == '*' or ID[:2] == 'V*':  # обозначение по Байеру или обозн-е переменной звезды
        Bayer = ID[2:].strip()
        while '  ' in Bayer: # избавляемся от лишних пробелов
            Bayer = Bayer.replace('  ', ' ')
        if Bayer[:3] == 'tet': # в этом каталоге тэта пишется как tet
            Bayer = 'the' + Bayer[3:]
    
        if Bayer in cross_bayer_hip:
            HIP = cross_bayer_hip[Bayer]
        elif Bayer in except_bayer: # в исключениях
            HIP = except_bayer[Bayer]
            # Поиск похожей звезды в Hip.
            # Критерии: координаты, зв. вел-на.
            # for H in df_compiled:
            #     dRA = abs(float(data['RAdeg']) - float(df_compiled[H]['RAdeg']))
            #     dDec = abs(float(data['DEdeg']) - float(df_compiled[H]['DEdeg']))
            #     dVmag = abs(float(data['Vmag']) - float(df_compiled[H]['Vmag']))
            #     if dRA < 0.2 and dDec < 0.2 and dVmag < 0.8 and not(ID in problem):
            #         print(data['ID'], '|', data['Vmag'], '|', data['Teff'])
            #         print(df_compiled[H]['Fl'], df_compiled[H]['Bayer'], df_compiled[H]['Bayer_cst'], '|', df_compiled[H]['Vmag'], '|', df_compiled[H]['SpType'], '|', 'HIP', H, '\n')
            #         problem.append(ID)
            #     if counter > 20:
            #         break

    # Запись в специальный словарь dict_hip_teff . Дело в том, что в каталоге PASTEL
    # к одной звезде много измерений, и они отличаются. Нужно вычислить среднее значение
    # в случае нескольких. Ключ: HIP, значение: массив Teff.
    if HIP in df_compiled:
        if not(HIP in dict_hip_teff): # новая звезда
            dict_hip_teff[HIP] = [float(data['Teff'])]
        else:
            dict_hip_teff[HIP].append(float(data['Teff']))
f.close()

# Запись Teff в датасет.
for HIP in dict_hip_teff:
    if len(dict_hip_teff[HIP]) == 1: # одно значение Teff
        Teff = str(int(dict_hip_teff[HIP][0]))
    else: # вычисляется среднее значение
        Teff = str(int(sum(dict_hip_teff[HIP]) / len(dict_hip_teff[HIP])))
    df_compiled[HIP]['Teff'] = Teff

# ------------------------------------------------------------------------------------------
# Собственные имена звёзд взяты c Википедии.
# Сформирован файл csv, который здесь читается.
# ------------------------------------------------------------------------------------------
f = open(filename_proper_names, encoding='utf-8')
doub = []
for s in f:
    if len(s) < 3 or s[:3] == 'HIP': # пустая строка или заголовок
        continue
    l = s.split(',')
    HIP = l[0].strip()
    Name_r = l[1].strip()
    Name = l[2].strip()
    Bayer = l[3].strip()

    if HIP in df_compiled:
        df_compiled[HIP]['Name'] = Name
        df_compiled[HIP]['Name_r'] = Name_r
f.close()

# ---------------------------------
# Запись датафрейма в файл.
# ---------------------------------
fw = open('dataset_bright_stars.csv', 'w', encoding='utf-8')
fe = open('dataset_bright_stars_excel.csv', 'w', encoding='cp1251') # для работы в русском Excel-е

fw.write(','.join(keys_compiled) + '\n') # Строка заголовков.
fe.write(';'.join(keys_compiled) + '\n') # Строка заголовков.

for HIP in df_compiled:
    data = df_compiled[HIP]
    sw = '' # строка записи в датасет
    se = ''
    for key in keys_compiled: # цикл по последнему объеденённому словарю
        sw += data[key] + ',' # для нормального датасета
        # для Экселя
        if '.' in data[key] and key != 'SpType':
            se += data[key].replace('.', ',') + ';' # для Экселя десятичная часть отделяется ","
        else:
            se += data[key] + ';'
    sw = sw[:-1] + '\n'
    se = se[:-1] + '\n'

    # Для Экселя - удаление символов, не входящих в кодировку 1251.
    se2 = ''
    for sym in se:
        if 40 <= ord(sym) <= 125 or 1040 <= ord(sym) <= 1103 or sym == '\n': # если разрешённый символ
            se2 += sym
    
    fw.write(sw)
    fe.write(se2)

fw.close()
fe.close()