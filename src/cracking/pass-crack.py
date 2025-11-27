#!/usr/bin/env python3

import os
import itertools

def clear():
    cmd = 'cls' if os.name == 'nt' else 'clear'
    os.system(cmd)

def generate_basic(data):
    passwords = []
    bfs = data["surname"][0].upper() if data["surname"] else ''
    
    passwords.append(data["name"] + data["surname"])
    passwords.append(data["surname"] + "123")
    passwords.append(data["nick"] + "2025")
    passwords.append(data["name"] + data["surname"])
    passwords.append(data["name"] + data["bday"])
    passwords.append(bfs + data["name"]) 
    passwords.append(bfs + data["name"] + "2025")

    for item in data["etc"]:
        passwords.append(data["name"] + item)
        passwords.append(item + data["name"])
        passwords.append(data["surname"] + item)
        passwords.append(item + data["surname"])
    
    return passwords

def generate_advanced(data):
    passwords = []
    
    # Собираем все данные в один список
    all_data = [
        data["name"],
        data["surname"], 
        data["nick"],
        data["bday"],
        data["pet"],
        data["love"]
    ] + data["etc"]
    
    # Убираем пустые значения
    all_data = [item for item in all_data if item.strip()]
    
    # Генерируем комбинации
    for r in range(1, 3):  # Комбинации из 1 и 2 элементов
        for combination in itertools.permutations(all_data, r):
            passwords.append(''.join(combination))
    
    # Добавляем числа к комбинациям
    numbers = ['123', '456', '789', '111', '000', '2024', '2025', data["bday"]]
    separators = ['', '_', '.', '-']
    
    for item in all_data:
        for number in numbers:
            for sep in separators:
                passwords.append(item + sep + number)
                passwords.append(number + sep + item)
    
    # Комбинации с заменой букв
    leet_dict = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
    
    for item in all_data[:3]:  # Берем только первые 3 элемента для экономии времени
        # Заменяем буквы
        leet_variations = []
        for char in item.lower():
            if char in leet_dict:
                leet_variations.append([char, leet_dict[char]])
            else:
                leet_variations.append([char])
        
        # Генерируем все возможные комбинации замен
        for leet_comb in itertools.product(*leet_variations):
            leet_word = ''.join(leet_comb)
            if leet_word != item:  # Не добавляем исходное слово
                passwords.append(leet_word)
    
    return list(set(passwords))  # Убираем дубликаты

def get_info():
    data = {}
    data["name"] = input("Enter victim's name\n> ").strip()
    data["surname"] = input("Enter victim's surname\n> ").strip()
    data["nick"] = input("Enter victim's nickname\n> ").strip()
    data["bday"] = input("Enter victim's birth day\n> ").strip()
    data["pet"] = input("Enter victim's pet name\n> ").strip()
    data["love"] = input("Enter the name of the victim's loved one\n> ").strip()

    quest = input("Add etc info? [Y/n]\n> ")

    if quest == '' or quest.lower() == 'y':
        etc = input("Enter more info (separated by commas): ").strip()
        if etc:
            data["etc"] = [item.strip() for item in etc.split(',') if item.strip()] 
        else:
            data["etc"] = []
    else:
        data["etc"] = []

    return data

def main():
    clear()
    all_info = get_info()
    
    # Выбор типа генерации
    print("\nChoose generation method:")
    print("1 - Basic (fast, less passwords)")
    print("2 - Advanced (slower, more passwords)")
    choice = input("> ").strip()
    
    if choice == "2":
        passwords = generate_advanced(all_info)
    else:
        passwords = generate_basic(all_info)

    clear()

    filename = input("Enter name for generated passwords (or press enter and name will be 'passwords.txt')\n> ").strip()

    if not filename:
        filename = "passwords.txt"

    with open(filename, "w", encoding='utf-8') as f:
        f.write("GENERATED PASSWORDS:\n")
        f.write("=" * 50 + "\n")
        for pwd in passwords:
            f.write(f"{pwd}\n")  # Убрана нумерация
        
    clear()
    print(f"Done! Generated {len(passwords)} passwords!\nGood Luck.")

if __name__ == '__main__':
    main()
