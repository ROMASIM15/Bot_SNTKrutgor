
#-------------Запуск Бота----------------


#import token_bot

import dei_json
import gspread #таблица гугл
# from google.oauth2.service_account import Credentials

import os
import asyncio
from maxbot.bot import Bot
#from maxbot import Bot
from maxbot.dispatcher import Dispatcher
from maxbot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton #, Callback




nachalo = 0

BOT_TOKEN = os.getenv('TOKEN')#token_bot.TOKEN #записываем токен

bot = Bot(token=BOT_TOKEN)   #создаём тело бота
dp = Dispatcher(bot)  #обработчик команд

gc = gspread.service_account(filename=os.getenv('sntkrutyegorkikod'))
sh = gc.open_by_key(os.getenv('key'))

worksheet = [ sh.get_worksheet(4), sh.get_worksheet(3), sh.get_worksheet(2), sh.get_worksheet(1)]
worksheet2 = sh.get_worksheet(5)

#------------------------------функции -----------------------------------------------------------

def extract_digits(text: str) -> str:
    """Возвращает строку, содержащую только цифры из исходного текста."""
    return ''.join(ch for ch in text if ch.isdigit())

def floatNew(stroka):
    if stroka == None or stroka == "": return 0
    else:
        return float(str(stroka).replace(',','.'))

def dolg (table, god: int, number: float): # возвращает общий долг за данный год
    data = table.col_values(1) # берём первый столбец в этом году(riw)
    r = data.index(number) + 1 # узнаем какой по счету в столбце участок
    rows = table.row_values(r) # берём строку с этим участком в этом году
    if god <2 or god==4: # c 2024 по 2026 годы
        return int(rows[19])
    elif god == 2: # 2023 год
        return int(rows[18])
    else: return int(rows[15])

def info_dolg (table, god: int, number: float): #вывод подробной информации о долге на конкретный год
    data = table.col_values(1)  # берём первый столбец в этом году(riw)
    r = data.index(number) + 1  # узнаем какой по счету в столбце участок
    rows = table.row_values(r)  # берём строку с этим участком в этом году

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
        [InlineKeyboardButton(text="Реквизиты для оплаты", callback_data="recvisit")]
    ])

keyboardadm = InlineKeyboardMarkup(inline_keyboard=[        #клавиатура админа
        [InlineKeyboardButton(text="Информация об участке", callback_data="inf_ych")],
        [InlineKeyboardButton(text="Передать показания", callback_data="peredati_pocaz")],
        [InlineKeyboardButton(text="Реквизиты для оплаты", callback_data="recvisit")]
    ])




@dp.message()           #обработчик сообщений
async def handle_messages(message: Message):
    user_id = message.user_id()  # правильный ID отправителя

    # Увеличиваем счётчик для этого пользователя

    count = dei_json.json_to_col_vo(user_id)         #обращаюсь к програрамме dei_json

    if count == 1:
        await bot.send_message(user_id=user_id, text='Здравствуйте я бот СНТ"крутые горки"')
        await bot.send_message(user_id=user_id, text='Напишите пожалуйста номер участка (цифрами).')

    else:
        text = message.text
        if text != "админ":
            ob_text = extract_digits(text)
            if ob_text != "":
                nomera = worksheet[0].col_values(1)
                if str(ob_text) in nomera:
                    dei_json.json_to_clientc(user_id, ob_text)
                    await bot.send_message(user_id=user_id, text='Что вас интересует?', reply_markup=keyboard)
                else:
                    await bot.send_message(user_id=user_id, text='Этого участка несуществует.')
            else:
                await bot.send_message(user_id=user_id, text='Напишите номер участка цифрами.')
        else:
            await bot.send_message(user_id=user_id, text='Здраствуйте админ')

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
        data = worksheet2.col_values(1) # берём первый столбец в 2026г
        if nomer in data: # проверяем есть такой участок
            r = data.index(nomer) + 1 # узнаем какой по счету в столбце участок
            rows = worksheet2.row_values(r) # берём строку с этим участком в 2026

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
                r = data.index(nomer) + 1
                rows = worksheet2.row_values(r)

                if int(rows[19]) > 0:
                    await bot.send_message(user_id=cb.user.id, text=f'Ваш общий долг равен {rows[19]}')
                else:
                    await bot.send_message(user_id=cb.user.id, text=f'Ваша общиая переплата равна {rows[19]}')
            else:
                await bot.send_message(user_id=cb.user.id, text="У вас нет долгов")
        else:
            await bot.send_message(user_id=cb.user.id, text=f'участок {nomer} в 2026году не найден')
        await bot.send_message(user_id=cb.user.id, text='Что вас интересует?', reply_markup=keyboard)
    elif cb.payload == "recvisit": #реквизиты для оплаты
        await bot.send_message(user_id=cb.user.id, text="Функция заблокирована!")






async def main():
    await dp.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
