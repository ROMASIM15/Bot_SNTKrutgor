# работа с json


import json
import os


def json_to_clientc(id, nomer):     #добавление/изменение в json файл айди пользователя к которому привязан участок
    # Путь к вашему JSON-файлу
    file_path = os.getenv('clients')

    # Значение, которое вы хотите присвоить id (может быть строкой или числом)

    # 1. Читаем существующий файл, если он есть, иначе создаём пустой словарь
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}


    # 3. Добавляем или обновляем поле "id"
    data["client"][str(id)] = nomer  # если nomer – переменная

    # 4. Записываем обратно в файл (с красивым форматированием)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # print(f"Поле id успешно установлено в {nomer} в разделе client.")

def json_in_client(id):       #узнаём какой участок привязан к определённому айди
    file_path = os.getenv('clients')
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    nomer = data["client"][str(id)]
    # print(nomer)
    return nomer

def json_to_col_vo(idt):       #записываем первый ли раз нам написал пользователь
    file_path = os.getenv('clients')
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = os.getenv('clients')
    print data
    # print(data["col_vo"])
    # print(idt)
    value = data["col_vo"].get(str(idt))
    # print(value)
    if value == None:
        data["col_vo"][idt] = 1
    else:
        # # star = data["col_vo"][id]

        del data["col_vo"][str(idt)]
        data["col_vo"][idt] = 2
        # data.remove(dete2)
        # star = dete2[id]
        # dete2.remove(id)
        # dete2[id].append(star+1)
        # data.add(dete2)
        # # del data["col_vo"][str(id)]
        # # data["col_vo"][id] = 2
        # data['col_vo'].pop('273689952', None)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data["col_vo"][idt]

# i=input("ID ")
# nomer=input("номер ")
# json_to_col_vo(i)
