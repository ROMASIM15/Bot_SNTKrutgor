
#-------------Запуск Бота----------------


#import token_bot

import dei_json
import gspread #таблица гугл
# from google.oauth2.service_account import Credentials

import json
import os
import asyncio
from maxbot.bot import Bot
#from maxbot import Bot
from maxbot.dispatcher import Dispatcher
from maxbot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton #, Callback
import logging
logging.basicConfig(level=logging.INFO)



nachalo = 0

BOT_TOKEN = os.getenv('TOKEN')#token_bot.TOKEN #записываем токен

bot = Bot(token=BOT_TOKEN)   #создаём тело бота
dp = Dispatcher(bot)  #обработчик команд


# ----- АВТОРИЗАЦИЯ GOOGLE SHEETS -----
creds_json = os.getenv('sntkrutyegorkikod')
if creds_json:
    # try:
    creds_dict = json.loads(creds_json)
    from google.oauth2.service_account import Credentials
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    # creds = Credentials.from_service_account_info(creds_dict)
    gc = gspread.authorize(creds)
    # except Exception as e:
    #     print(f"Ошибка авторизации Google: {e}")
    #     raise
else:
    # fallback – если переменной нет (для локального теста)
    gc = gspread.service_account(filename='sntkrutyegorki-086134b54bc6.json')

# Теперь открываем таблицу по ключу
sh = gc.open_by_key(os.getenv('key'))


# sntkrutyegorkikodpromo = os.getenv('sntkrutyegorkikod'
# gc = gspread.service_account(filename="sntkrutyegorkikodpromo"))
# # creds_json = os.getenv('sntkrutyegorkikod')
# # if creds_json:
# #     creds_dict = json.loads(creds_json)
# #     # Создаём учётные данные
# #     creds = Credentials.from_service_account_info(creds_dict)
# #     # Авторизуемся в Google Sheets
# #     gc = gspread.authorize(creds)
# sh = gc.open_by_key(key=os.getenv('key'))

worksheetneed = [ sh.get_worksheet(4), sh.get_worksheet(3), sh.get_worksheet(2), sh.get_worksheet(1)]
worksheet = [ worksheetneed[0].get_all_values(), worksheetneed[1].get_all_values(), worksheetneed[2].get_all_values(), worksheetneed[3].get_all_values()]
worksheet2need = sh.get_worksheet(5)
worksheet2 = worksheet2need.get_all_values()
# image_path = "qiar.png"
# photo = InputMedia(image_path)
# metadata = sh.fetch_sheet_metadata()
# print(metadata)
# if 'modifiedTime' in metadata:


# if sh.lastUpdateTime: автоматическое опраделение даты обновления таблимцы
#     time_table=str(sh.lastUpdateTime)
#     # print(time_table)
#     clean = time_table.replace("T", " ").replace("Z", "")
#     # time_table
# else:
#     time_table="не удалось загрузить дату обновления"
need = sh.get_worksheet(6)
# print(need.row_values(2))
clean = need.cell(2,5).value

#------------------------------функции -----------------------------------------------------------
def spisok_in_spisok(spisok,nomer):
    ret=[]
    for i in spisok:
        ret.append(i[nomer-1])
    return ret

def is_valid_digit_string(s: str) -> bool:
    return s.isdigit() and len(s) >= 2

def extract_digits(text: str) -> str:
    """Возвращает строку, содержащую только цифры из исходного текста."""
    return ''.join(ch for ch in text if ch.isdigit())

def floatNew(stroka):
    if stroka == None or stroka == "": return 0
    else:
        return float(str(stroka).replace(',','.'))

def dolg (table, god: int, number: float): # возвращает общий долг за данный год
    data = spisok_in_spisok(table,1) # берём первый столбец в этом году(riw)
    r = data.index(number) # узнаем какой по счету в столбце участок
    rows = table[r] # берём строку с этим участком в этом году
    if god <2 or god==4: # c 2024 по 2026 годы
        return int(rows[19])
    elif god == 2: # 2023 год
        return int(rows[18])
    else: return int(rows[15])

def info_dolg (table, god: int, number: float): #вывод подробной информации о долге на конкретный год
    data = spisok_in_spisok(table, 1) # берём первый столбец в этом году(riw)
    r = data.index(number)  # узнаем какой по счету в столбце участок
    rows = table[r]  # берём строку с этим участком в этом году

    if god == 0: #определяем год и тарифы
        res_god="2025 год:\n"
        info={"сотка":1000,"живет":6000, "свет":4000, "вода":2000}
    elif god == 1:
        res_god="2024 год:\n"
        info={"сотка":900,"живет":6000, "свет":4000, "вода":2000}
    elif god == 2:
        res_god="2023 год:\n"
        info={"сотка":800,"живет":5500, "свет":3500, "вода":1750}
    elif god == 3:
        res_god="2022 год:\n"
        info = {"сотка": 700, "живет": 5000, "свет": 3000, "вода": 1500} #примерные значения
    else:
        res_god="2026 год:\n"
        info={"сотка":1500,"живет":6000, "свет":4000, "вода":2000}

    if god <2 or god==4: # c 2024 по 2026 годы
        res_god += f"За землю - {floatNew(rows[2])} соток * {floatNew(info['сотка'])}руб.={floatNew(rows[2])*floatNew(info['сотка'])}\n"#земля
        if (floatNew(rows[9])+floatNew(rows[10]))>0 : res_god += f"Внесено: {floatNew(rows[9])+floatNew(rows[10])}руб.\n {rows[11]}\n"
        else: res_god +="оплаты не было \n"

        if rows[3] == "свет": res_god += f"За свет: {floatNew(info['свет'])}руб.\n"#свет
        elif rows[3] == "живет":  res_god += f"За проживание: {floatNew(info['живет'])}руб.\n"
        elif rows[3] == "вода (0.5)": res_god += f"За воду: {floatNew(info['вода'])}руб.\n"

        if (floatNew(rows[12]) + floatNew(rows[13])) > 0: res_god += f"Внесено: {floatNew(rows[12]) + floatNew(rows[13])}руб.\n  {rows[14]}\n\n"
        else: res_god += "платежи не вносились\n\n"

        res_god += f"Итого, с учетом прошлых лет: "
        if floatNew(rows[19])<0: res_god +=f"переплата {abs(floatNew(rows[19]))}руб."
        elif floatNew(rows[19])>0: res_god +=f"долг {rows[19]}руб."
        else: res_god +=f"долга нет"
        return res_god
    elif god == 2: # 2023 год
        res_god += f"За землю - {floatNew(rows[2])} соток * {floatNew(info['сотка'])}руб.={floatNew(rows[2]) * floatNew(info['сотка'])}\n"  # земля
        if (floatNew(rows[9])) > 0:
            res_god += f"Внесено: {floatNew(rows[9])}руб.\n {floatNew(rows[10])}\n"
        else:
            res_god += "оплаты не было \n"

        if rows[3] == "свет":
            res_god += f"За свет: {info['свет']}руб.\n"  # свет
        elif rows[3] == "живет":
            res_god += f"За проживание: {info['живет']}руб.\n"
        elif rows[3] == "вода (0.5)":
            res_god += f"За воду: {info['вода']}руб.\n"

        if (floatNew(rows[12]) + floatNew(rows[11])) > 0:
            res_god += f"Внесено: {floatNew(rows[12]) + floatNew(rows[11])}руб.\n  {rows[13]}\n\n"
        else:
            res_god += "платежи не вносились\n\n"

        res_god += f"Итого, с учетом прошлых лет: "
        if floatNew(rows[18]) < 0:
            res_god += f"переплата {abs(floatNew(rows[18]))}руб."
        elif floatNew(rows[18]) > 0:
            res_god += f"долг {floatNew(rows[18])}руб."
        else:
            res_god += f"долга нет"
        return res_god
    else: #2022 год
        res_god += f"С учетом прошлых лет: "
        if floatNew(rows[15])<0: res_god +=f"переплата {abs(floatNew(rows[19]))}руб."
        elif floatNew(rows[15])>0: res_god +=f"долг {floatNew(rows[19])}руб."
        else: res_god +=f"долга нет"
        return res_god



#--------------------------------------------------------------------------------------------------
keyboard = InlineKeyboardMarkup(inline_keyboard=[     #клавиатура обычного пользователя
        [InlineKeyboardButton(text="Информация об участке", callback_data="inf_ych")],
        [InlineKeyboardButton(text="Передать показания", callback_data="peredati_pocaz")],
        [InlineKeyboardButton(text="Реквизиты для оплаты", callback_data="recvisit")],
        [InlineKeyboardButton(text="сменить пароль", callback_data="parol")]

    ])

vbod_parol = InlineKeyboardMarkup(inline_keyboard=[     #клавиатура обычного пользователя
        [InlineKeyboardButton(text="Выбрать другой участок", callback_data="ne_tot")]

    ])

dobv_parol = InlineKeyboardMarkup(inline_keyboard=[     #клавиатура обычного пользователя
        [InlineKeyboardButton(text="Оставить старый пароль", callback_data="star")]

    ])

keyboardadm = InlineKeyboardMarkup(inline_keyboard=[        #клавиатура админа
        [InlineKeyboardButton(text="Посмотреть данные участка", callback_data="dan_ych")],
        [InlineKeyboardButton(text="Сколько внесено денег", callback_data="vnes")],
        [InlineKeyboardButton(text="Список должников", callback_data="dolchi")]
    ])




@dp.message()           #обработчик сообщений
async def handle_messages(message: Message):
    global nachaloi
    user_id = message.user_id()  # правильный ID отправителя

    # Увеличиваем счётчик для этого пользователя

    count = dei_json.json_to_col_vo(user_id)         #обращаюсь к програрамме dei_json

    if count == 1:
        await bot.send_message(user_id=user_id, text='Здравствуйте я бот СНТ"крутые горки"')
        await bot.send_message(user_id=user_id, text='Напишите пожалуйста номер участка (цифрами).')

    else:
        text = message.text
        if text != "админ":
            dana_ych = dei_json.admin_smotr(user_id)
            if dana_ych == None:

                new = dei_json.new_parol(user_id)
                # print(new)
                if new == None:

                    ob_text = extract_digits(text)
                    parol = dei_json.sostoinie_parol(user_id)
                    need = sh.get_worksheet(6)
                    need2 = need.col_values(1)


                    if parol == None:

                        if ob_text != "":
                            nomera = spisok_in_spisok(worksheet[0],1)
                            # print(nomera)
                            if str(ob_text) in nomera:
                                await bot.send_message(user_id=user_id, text='Напишите пароль.')
                                dei_json.sostoinie_parol_yes(user_id, ob_text)
                            else:
                                await bot.send_message(user_id=user_id, text='Этого участка несуществует.')
                        else:
                            await bot.send_message(user_id=user_id, text='Напишите номер участка цифрами.')
                    else:
                        r = need2.index(parol) + 1  # узнаем какой по счету в столбце участок
                        rows = need.row_values(r)
                        parol_text = rows[1]
                        if str(parol_text) == str(ob_text):
                            dei_json.json_to_clientc(user_id, parol)
                            dei_json.sostoinie_parol_no(user_id)
                            await bot.send_message(user_id=user_id, text='Что вас интересует?', reply_markup=keyboard)

                        else:
                            await bot.send_message(user_id=user_id, text='Пароль не верный, повторите попытку.', reply_markup=vbod_parol)
                else:
                    if is_valid_digit_string(text)==True:
                        dei_json.new_parol_no(user_id)
                        need = sh.get_worksheet(6)
                        need2 = need.col_values(1)
                        r = need2.index(dei_json.json_in_client(user_id)) + 1  # узнаем какой по счету в столбце участок
                         # rows = need.row_values(r)
                        # print(r)
                        need.update_cell(r, 2, text)
                        await bot.send_message(user_id=user_id, text='Что вас интересует?', reply_markup=keyboard)
                    else:
                        await bot.send_message(user_id=user_id, text='Пароль не подходит, он должен состоять только из цифр минимум из двух, повторите попытку.',reply_markup=dobv_parol)
            else:
                nomer = extract_digits(text)
                dei_json.admin_smotr_no(user_id)
                # nomer = dei_json.json_in_client(user_id)  # берем привязаный участок к айди

                await bot.send_message(user_id=user_id, text=f'номер участка: {nomer}')

                # ------------------------вывод отсутствия долгов-------------------------------------
                data = spisok_in_spisok(worksheet2,1) # берём первый столбец в 2026г
                if nomer in data:  # проверяем есть такой участок
                    r = data.index(nomer)  # узнаем какой по счету в столбце участок
                    rows = worksheet2[r]  # берём строку с этим участком в 2026

                    await bot.send_message(user_id=user_id, text=rows[4])  # отправляем ФИО

                    if int(rows[19]) < 0 or int(rows[19]) > 0:  # не равна ли общая задолженнось 2026г нулю
                        for riw in worksheet:  # перебираем страницы с 2025 по 2022гг
                            if dolg(riw, worksheet.index(riw),
                                    nomer) > 0:  # если долг в таблице номер worksheet.index(riw) есть
                                if worksheet.index(riw) == 3:
                                    nachaloi = 3
                            else:
                                if worksheet.index(riw) < 3:  # если нет долга в годах от 2023 до 2025
                                    await bot.send_message(user_id=user_id,
                                                           text=f"в2022-{2021 + (4 - worksheet.index(riw))}гг у вас нет долга")
                                    nachaloi = worksheet.index(
                                        riw) - 1  # следующий год, с которого начинаем выводить долги
                                    break
                                elif worksheet.index(riw) == 3:  # если нет долга в 2022 году
                                    await bot.send_message(user_id=user_id, text="в 2022г у вас нет долга")
                                    nachaloi = worksheet.index(riw) - 1
                                    break

                        # --------------------------вывод старых долгов --------------------------------------------------------
                        for i in range(nachaloi, -1, -1):
                            riw = worksheet[i]
                            await bot.send_message(user_id=user_id, text=info_dolg(riw, worksheet.index(riw), nomer))

                        # -------------------------вывод 2026 года -------------------------------------------------------------
                        await bot.send_message(user_id=user_id, text=info_dolg(worksheet2, 4, nomer))
                        r = data.index(nomer)
                        rows = worksheet2[r]

                        if int(rows[19]) > 0:
                            await bot.send_message(user_id=user_id, text=f'Ваш общий долг равен {rows[19]}')
                        else:
                            await bot.send_message(user_id=user_id,
                                                   text=f'Ваша общая переплата равна {abs(int(rows[19]))}')
                    else:
                        await bot.send_message(user_id=user_id, text="У вас нет долгов")
                else:
                    await bot.send_message(user_id=user_id, text=f'участок {nomer} в 2026году не найден')
                # await bot.send_message(user_id=user_id, text=f'данная информация обновлена:\n {clean}')

                await bot.send_message(user_id=user_id, text='Что вас интересует?', reply_markup=keyboardadm)

        else:
            await bot.send_message(user_id=user_id, text='Здраствуйте админ', reply_markup=keyboardadm)

@dp.callback()
async def on_callback(cb):
    global worksheet
    global worksheet2
    global nachalo

    # проверяем какая кнопка нажалась
    if cb.payload == "peredati_pocaz":#передать показания
        await bot.send_message(user_id=cb.user.id, text="Функция заблокирована!")
    elif cb.payload == "inf_ych":#информация об участке


        nomer = dei_json.json_in_client(cb.user.id) #берем привязаный участок к айди

        await bot.send_message(user_id=cb.user.id, text=f'номер участка: {nomer}')

#------------------------вывод отсутствия долгов-------------------------------------
        data = spisok_in_spisok(worksheet2,1) # берём первый столбец в 2026г
        if nomer in data: # проверяем есть такой участок
            r = data.index(nomer) # узнаем какой по счету в столбце участок
            rows = worksheet2[r] # берём строку с этим участком в 2026

            await bot.send_message(user_id=cb.user.id, text=rows[4]) # отправляем ФИО

            if int(rows[19]) < 0 or int(rows[19]) > 0:  # не равна ли общая задолженнось 2026г нулю
                for riw in worksheet: # перебираем страницы с 2025 по 2022гг
                    if dolg(riw,worksheet.index(riw),nomer) > 0: # если долг в таблице номер worksheet.index(riw) есть
                        if  worksheet.index(riw) == 3:
                            nachalo = 3
                    else:
                        if worksheet.index(riw) < 3:# если нет долга в годах от 2023 до 2025
                            await bot.send_message(user_id=cb.user.id, text=f"в2022-{2021 + (4 - worksheet.index(riw))}гг у вас нет долга")
                            nachalo = worksheet.index(riw)-1 # следующий год, с которого начинаем выводить долги
                            break
                        elif worksheet.index(riw) == 3:# если нет долга в 2022 году
                            await bot.send_message(user_id=cb.user.id, text="в 2022г у вас нет долга")
                            nachalo = worksheet.index(riw)-1
                            break

#--------------------------вывод старых долгов --------------------------------------------------------
                for i in range(nachalo, -1, -1):
                    riw = worksheet[i]
                    # data = riw.col_values(1)
                    # r = data.index(nomer) + 1
                    # rows = riw.row_values(r)
                    await bot.send_message(user_id=cb.user.id, text=info_dolg(riw, worksheet.index(riw), nomer))
                    # if i < 3:
                    #     if int(rows[-2]) == 0:
                    #         await bot.send_message(user_id=cb.user.id, text=f'долга за {2021 + (4 - i)} нет')
                    #     elif int(rows[-2]) < 0:
                    #         await bot.send_message(user_id=cb.user.id, text=f'переплата за {2021 + (4 - i)}: {abs(int(rows[-2]))}')
                    #     else:
                    #         await bot.send_message(user_id=cb.user.id, text=f'долг за {2021 + (4 - i)}: {int(rows[-2])}')
                    # else:
                    #     if int(rows[-1]) == 0:
                    #         await bot.send_message(user_id=cb.user.id, text=f'долга за {2021 + (4 - i)} нет')
                    #     elif int(rows[-1]) < 0:
                    #
                    #         await bot.send_message(user_id=cb.user.id, text=f'переплата за {2021 + (4 - i)}: {abs(int(rows[-1]))}')
                    #     else:
                    #         await bot.send_message(user_id=cb.user.id, text=f'долг за {2021 + (4 - i)}: {int(rows[-1])}')

#-------------------------вывод 2026 года -------------------------------------------------------------
                await bot.send_message(user_id=cb.user.id, text=info_dolg(worksheet2, 4, nomer))
                r = data.index(nomer)
                rows = worksheet2[r]

                if int(rows[19]) > 0:
                    await bot.send_message(user_id=cb.user.id, text=f'Ваш общий долг равен {rows[19]}')
                else:
                    await bot.send_message(user_id=cb.user.id, text=f'Ваша общая переплата равна {abs(int(rows[19]))}')
            else:
                await bot.send_message(user_id=cb.user.id, text="У вас нет долгов")
        else:
            await bot.send_message(user_id=cb.user.id, text=f'участок {nomer} в 2026году не найден')

        await bot.send_message(user_id=cb.user.id, text=f'данная информация обновлена:\n {clean}')


        await bot.send_message(user_id=cb.user.id, text='Что вас интересует?', reply_markup=keyboard)
    elif cb.payload == "recvisit": #реквизиты для оплаты
        await bot.send_file(user_id=cb.user.id, file_path="россельхозбанк qr од.png", media_type="image", text="Оплата за землю (СБЕР БАНК):")
        await bot.send_message(user_id=cb.user.id,
                               text='''
        Наименование: СНТ "КРУТЫЕ ГОРКИ"
        ИНН: 2424003947
        КПП: 242401001
        ОГРН: 1052404017489
        Расчетный счет: 40703810231000002895
        Банк: КРАСНОЯРСКОЕ ОТДЕЛЕНИЕ №8646 ПАО СБЕРБАНК
        БИК банка: 040407627
        Корр. счёт банка: 30101810800000000627
        ИНН банка: 7707083893
        КПП БАНКА: 246602001''')
        await bot.send_message(user_id=cb.user.id, text=f'(Пожалуйста, не забывайте указывать фамилию, сколько соток и номер участка)')
        await bot.send_file(user_id=cb.user.id, file_path="россельхозбанк qr од.png", media_type="image",  text=f'Оплата за свет (РОССЕЛЬХОЗ):')
        await bot.send_message(user_id=cb.user.id, text='''
        Наименование: СНТ "КРУТЫЕ ГОРКИ"
        Расчетный счет: 40703810349620000021
        Договор: №184962/1515
        Операционный офис Красноярского РФ АО "Россельхозбанк" №3349/49-2
        БИК: 040407923
        ИНН: 2424003947
        КПП: 246643001
        ОГРН: 1027700342890
        К/С: 30101810300000000923''')
        await bot.send_message(user_id=cb.user.id, text=f'(Пожалуйста, не забывайте указывать фамилию, сколько соток и номер участка)')

        await bot.send_message(user_id=cb.user.id, text='Что вас интересует?', reply_markup=keyboard)
    elif cb.payload == "parol": #смена пароля
        dei_json.new_parol_yes(cb.user.id)
        await bot.send_message(user_id=cb.user.id, text="Напишите новый пароль цифрами(минимум 2)")
    elif cb.payload == "ne_tot": #смена пароля
        dei_json.sostoinie_parol_no(cb.user.id)
        await bot.send_message(user_id=cb.user.id, text='Напишите номер участка цифрами.')
    elif cb.payload == "star":  # смена пароля
        dei_json.new_parol_no(cb.user.id)
        await bot.send_message(user_id=cb.user.id, text='Что вас интересует?', reply_markup=keyboard)
    elif cb.payload == "dan_ych":  # смена пароля
        dei_json.admin_smotr_yes(cb.user.id)
        await bot.send_message(user_id=cb.user.id, text="Напишите участок по которому вы хотите посмотреть информацию.")
    elif cb.payload == "vnes":  # смена пароля
        zem_nal = worksheet2[112][9]
        zem_bez = worksheet2[112][10]
        svet_nal = worksheet2[112][12]
        svet_bez = worksheet2[112][13]
        # print(worksheet2[113])
        await bot.send_message(user_id=cb.user.id, text=f"За землю наличными:\n{zem_nal}")
        await bot.send_message(user_id=cb.user.id, text=f"За землю безналичными:\n{zem_bez}")
        await bot.send_message(user_id=cb.user.id, text=f"За свет наличными:\n{svet_nal}")
        await bot.send_message(user_id=cb.user.id, text=f"За свет безналичными:\n{svet_bez}")
        await bot.send_message(user_id=cb.user.id, text=f"В сумме:\n{int(svet_bez) + int(zem_nal) + int(zem_bez) + int(svet_nal)}")
        await bot.send_message(user_id=cb.user.id, text='Что вас интересует?', reply_markup=keyboardadm)
    elif cb.payload == "dolchi":  # смена пароля
        spravka = "Должники\n участок ФИО Долг\n"
        iting = 0
        for i in range(112):
            itn = worksheet2[iting][19]
            iting += 1
            if str(itn) != "Осталось заплатить ВСЕГО":
                itn_clean = itn.replace(',', '.')
                if float(itn_clean) > 0:
                    kit = worksheet2[int(iting-1)]

                    spravka+=f"{kit[0]}  {kit[4]} {itn_clean}\n"

        await bot.send_message(user_id=cb.user.id, text=spravka)
        await bot.send_message(user_id=cb.user.id, text='Что вас интересует?', reply_markup=keyboardadm)




async def main():
    await dp.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
