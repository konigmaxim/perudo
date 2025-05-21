import math
from collections import deque
import tkinter as tk  # ткинкеровские библиотеки
from tkinter import simpledialog, messagebox
import threading

"""
Формула рассчитывает вероятность утверждений
claimk - утвержденное игроком количество кубиков
claimval - утвержденное игроком значение кубиков
knowndice - наши кубики (известны)
totaldice - общее количество чужих-неизвестных кубиков
maputo - статус мапуто. Изначально мы его объявляем False, потому что так в большинстве случаев
"""


def formula(claimk, claimval, knowndice, totaldice,
            maputo=False):  # считаем сколько у нас уже есть нужных значений среди наших кубиков (включая джокеры - единицы)
    same = knowndice.count(claimval)  # считает количество названных игроком значений среди наших кубиков
    if not maputo and claimval != 1:
        same += knowndice.count(1)  # добавляем к посчитанному единицы-джокеры (если не мапуто)
    remainder = claimk - same  # остаток - сколько нужно кубиков с таким значением среди не наших (см. для обоснования файл с формулами, стр. 3 под графиком)
    if remainder <= 0:
        return 1.0  # если среди наших уже набралось достаточно, то вероятность 100%
    resres = 0.0  # базовая вероятность, к которой мы уже плюсуем - иначе получается кривой return. лучше объявить это до цикла
    n = totaldice
    # считаем вероятность по формуле (см. файл с формулами)
    for i in range(remainder, n + 1):  # нам же подходит не только заявленное количество, но и большее - см. файл
        combs = math.comb(n, i)  # встроенная функция из библиотеки math про сочетания, работает на версиях 3.8 и выше!
        if maputo:
            # формула для статуса мапуто (без джокеров-единиц)
            res = combs * (5 ** (n - i)) / (6 ** n)
        else:
            # базовая формула (с джокерами-единицами)
            res = combs * (4 ** (n - i)) * (2 ** i) / (6 ** n)
        resres += res
    return resres


class Player:

    def __init__(self, name: str):
        self.name = name  # имя - строкой
        self.dice = 5  # у каждого игрока в начале 5 кубиков, int
        self.hand = []  # значения кубиков игрока которые потом  введутся (пустой список, потом будем обновлять через split)
        self.status = "нейтральный"  # статус - по дефолту нейтральный, или мапуто (1 кубик)/проигравший
        self.mpt = 0  # счетчик объявлений мапуто игрока (макс. 1 раз за игру)

    def update_status(
            self):  # dice и status берем из предыдущей моей штуки, а потом будем обновлять уже в коде самой игры
        if self.dice == 0:  # потом в коде пропишем, что кто с 0,тот ход скипается
            self.status = "на мели, пройдоха"
        elif self.dice == 1 and self.mpt == 0:  # проверка условий подходящих мапуто
            decision = simpledialog.askstring("Мапуто", f"Объявляет ли {self.name} статус мапуто? (да/нет)")
            if decision and decision.strip().lower() == "да":  # два. раза, чтобы проверить, что вообще что-то ввели
                self.status = "мапуто"
                self.mpt = 1
            else:
                self.status = "нейтральный"
        else:  # 2+ кубика
            self.status = "нейтральный"

    def dice_cast(self, manual: bool = False, app=None):  # функция осуществления бросков
        if manual:  # наш вводим вручную
            while True:
                entry = simpledialog.askstring("Бросок кубиков",
                                               f"{self.name}, введи значения своих костей (от 1 до 6) через пробел:")
                if entry is None:
                    continue
                values = entry.strip().split()  # вводим наши значения через пробел. На всякий случай делаем strip от всего лишнего
                try:  # конструкция try-except - чтобы исключить варианты, когда введено что-то не то
                    nums = list(map(int, values))  # закидываем в список
                    if len(nums) != self.dice:  # проверка, чтобы количество введенных нами значений совпадало с текущим колвом кубиков
                        messagebox.showerror("Ошибка", f"У тебя должно быть ровно {self.dice} костей!")
                        continue
                    if not all(1 <= val <= 6 for val in
                               nums):  # проверка, что все введенные значения в диапазоне 1-6 (кубик-шестигранник)
                        messagebox.showerror("Ошибка", "Кости должны быть числом от 1 до 6!")
                        continue
                    self.hand = nums  # закидываем наш проверенный и правильный список в характеристики класса
                    app.log(f"{self.name}, твой бросок: {" ".join(str(i) for i in self.hand)}")
                    break
                except ValueError:  # вторая часть конструкции try-except. ValueError - проверка на неподдерживаемые значения
                    messagebox.showerror("Ошибка", "Дружище, вводи только целые значения!")
        else:  # броски остальных - неизвестны, поэтому оставляем пустыми
            self.hand = []


class Perudo:

    def __init__(self, player_names, username, gui):
        self.players = deque([Player(name) for name in
                              player_names])  # deque - двусторонняя очередь, короче, улучшенный список как раз для наших целей. Для него я импортировала модуль в начале.
        self.username = username  # username и player_names мы возьмем в конце, в стартовике кода
        self.roundnumb = 0  # ну и объявляшка номера раунда по порядку, когда игра не запущена - нулевой раунд
        self.lastofus = 0  # индекс игрока, объявившего "конец" в предыдущем раунде
        self.gui = gui  # ткинкер

    def log(self, message):  # ткинкер
        self.gui.log(message)

    def get_active_players(self):
        # возвращаем список игроков, у которых еще есть кубики
        return [p for p in self.players if p.dice > 0]

    def first_player(self, name: str = None):
        # устанавливаем первого игрока в раунде - если 1 раунд, то мы потом введем вручную, иначе - махинации ниже
        if name is None:  # не 1 раунд
            real_players = list(self.players)
            length = len(real_players)  # находим длину нашего списка игроков (в тч неактивных)
            starter = (self.lastofus + 1) % length  # та же циклическая очередь что и в play
            name = real_players[starter].name
        while self.players[0].name != name:  # крутим deque пока не докрутим до него
            self.players.rotate(-1)

    def get_user(self):
        # возвращаем объект нашего игрока
        for p in self.players:
            if p.name == self.username:
                return p
        return None

    def next_round(self):  # начинаем раунды
        self.roundnumb += 1  # номер раунда увеличивается + выводим красивенько
        self.log(f'--- Раунд {self.roundnumb} ---')
        self.log("Текущее состояние игроков:")
        for p in self.players:  # выводим
            self.log(f"{p.name} : {p.dice} кубиков ({p.status})")

        # производим бросок кубиков по вышенаписанной функции
        for p in self.get_active_players():
            if p.name == self.username:
                p.dice_cast(manual=True, app=self)  # если игрок мы, то вводим сами
            else:
                p.dice_cast(manual=False, app=self)  # если игрок - не мы, то автоматом (пустые)

    def statement(self, name: str):  # вводим стейтементы других игроков
        entry = simpledialog.askstring("Утверждение", f'Введи утверждение игрока {name} (например: 6 2) или "Конец":')
        if entry is None:
            return self.statement(name)  # ткинкеровская условность
        if entry.strip().lower() == "конец":
            return "end", None, None  # я пока обозначу то, что возвращается вот так - end и claim (в функции запуска это будут флаги-маркеры), может, потом еще поменяю
        try:  # конструкция try-except, как до этого у нас была в броске
            quant, val = map(int,
                             entry.strip().split())  # вводим наши 6 2 (шесть двоек), k - количество, val - значение-номинал
            if val < 1 or val > 6:
                messagebox.showerror("Ошибка", "Салага, ты ошибся. Номинал должен быть от 1 до 6.")
                return self.statement(name)
            return "claim", quant, val
        except:
            messagebox.showerror("Ошибка", "Введи два числа через пробел или 'Конец'!")  # если вводят что-то левое
            return self.statement(
                name)  # рекурсируем, т.е. возвращаем в начало и просим все ввести заново, если ввели что-то левое до этого

    def round_end(self):
        # Обрабатывает конец раунда
        while True:  # такая же ситуация с вводом первого по очередности игрока
            loser = simpledialog.askstring("Конец раунда",
                                           "Введи имя проигравшего неудачника (или '-' если есть победивший):")
            if loser is None:  # ткинкерская условность
                continue
            if loser in [p.name for p in self.players]:
                for p in self.players:
                    if p.name == loser:
                        p.dice = max(0, p.dice - 1)  # уменьшаем у проигравшего кол-во кубиков на 1
                        p.update_status()
                    elif p.dice == 1:  # проверяем всех на мапуто
                        p.update_status()
                break
            elif loser == "-":
                while True:
                    winner = simpledialog.askstring("А кто победил?", "Введи имя победившего везунчика:")
                    if winner in [p.name for p in self.players]:
                        for p in self.players:
                            if p.name == winner:
                                p.dice += 1  # даем победившему кубик
                                p.update_status()
                            elif p.dice == 1:  # проверяем всех на мапуто
                                p.update_status()
                        break
                    else:
                        messagebox.showerror("Ошибка", "Дружище, такого имени нет среди игроков.")
                break
            else:
                messagebox.showerror("Ошибка", "Дружище, такого имени нет среди игроков.")

    def other_dice(self):
        # Возвращает общее количество скрытых кубиков (всех кроме нашего игрока)
        return sum(p.dice for p in self.players if p.name != self.username)

    def check_winner(self):  # проверка на победителя всей игры - если остался только 1 чел с кубиками
        active_players = self.get_active_players()
        if len(active_players) == 1:  # функция get_active_players у нас создает список, значит мы можем проверить через длину этого списка
            winner = active_players[
                0].name  # собственно, если длина 1, то этого чела (нулевой и единственный элемент) и берем
            self.log("Йо-хо-хо, игра окончена! Победитель: " + winner)
            return True  # если true, то конец игры
        return False  # если false, то начинается следующий ход и по кругу

    def play(self):  # функция-основной цикл игры
        self.log("Рад видеть ваши рожи! Полных парусов и сухого пороха!")  # устанавливаем первого игрока
        while True:
            self.username = simpledialog.askstring("А как тебя зовут?", "Приятель, введи свое имя:")
            if self.username in [p.name for p in
                                 self.players]:  # проверка на то, что наше имя есть среди всех игроков, введенных ранее
                break  # если все норм, то скип
            else:
                messagebox.showerror("Ошибка",
                                     "Дружище, этого имени нет среди игроков.")  # если не норм, то заново запускается while. И так по бесконечности, пока не будет break (правильный ввод)
        while True:  # такая же ситуация с вводом первого по очередности игрока
            first = simpledialog.askstring("Первый игрок", "А кто начнет нашу битву? Введи имя:")
            if first in [p.name for p in self.players]:
                self.first_player(first)
                break
            else:
                messagebox.showerror("Ошибка", "Дружище, такого имени нет среди игроков.")

        # наш главный игровой цикл
        while len(self.get_active_players()) > 1:  # пока у нас больше чем 1 активный игрок
            self.next_round()  # наша функция начала раунда
            idx = 0
            real_players = list(self.players)  # берем всех игроков
            user = self.get_user()  # берем нашего игрока

            # цикл ходов внутри раунда
            while True:
                idxidx = idx % len(
                    real_players)  # крутим игроков по кругу. Например, если игроков 4, то очередность у программы будет 0, 1, 2, 3, 0, 1, и тд
                real = real_players[idxidx]  # игрок, чей сейчас ход
                if real.dice == 0:  # если у того, чей сейчас ход не осталось кубиков
                    idx += 1  # мы его скипаем и ход переходит дальше
                    continue

                # получаем утверждение игрока (если его не скипнули)
                flag, quant, val = self.statement(real.name)
                if flag == "end":
                    self.lastofus = self.players.index(real)  # перезаписываем индекс (остаток) закончившего игрока
                    self.round_end()  # если игрок сделал утверждение "конец", заканчиваем текущий раунд и начинаем с начала цикла
                    self.first_player()  # обновляем очередность ходов в результате конца раунда
                    break

                # проверяем статус мапуто и считаем вероятность
                maputo_active = any(
                    p.status == "мапуто" for p in self.get_active_players())  # статусы из функции про статусы))
                prob = formula(quant, val, user.hand, self.other_dice(),
                               maputo=maputo_active)  # посчитанная через функцию формулы вероятность
                self.log(
                    f"Пират {real.name} прав с вероятностью: {round(prob * 100, 2)}% ({quant} {val})")  # выводим переведенную в проценты (с округлением)
                idx += 1  # продолжаем крутить игроков по кругу

            if self.check_winner():  # если образовался победитель
                break  # заканчиваем игру
        self.log("Что ж, похоже, мы закончили. Славно намутили шторм в трюме, заглядывай еще.")


class GameGUI:  # интерфейс ткинкером

    def __init__(self):
        self.root = tk.Tk()  # главное окно
        self.root.title("Игра перудо")  # название
        self.root.geometry("1250x800")  # размер
        self.bg_image = tk.PhotoImage(file="background_1.gif")  # изображение фона (загружаем)
        self.background_label = tk.Label(self.root, image=self.bg_image)  # настраиваем фон через label
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)  # и его координаты
        self.frame = tk.Frame(self.root, bg='#fdf6e3')  # штука с текстом поверх фона
        self.frame.place(x=20, y=20, width=800, height=700)  # координаты ее
        self.text = tk.Text(self.frame, wrap=tk.WORD, font=("Helvetica", 20), bg="#fdf6e3",
                            relief=tk.FLAT)  # настройки текста
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.root.after(100, self.run_game)
        self.root.mainloop()

    def log(self, message):  # вывод сообщений в мини-окошки
        self.text.insert(tk.END, message + "\n")
        self.text.see(tk.END)

    def run_game(self):
        self.log("Ну что, тряхнем костями? Давай начинать игру.")
        names_str = simpledialog.askstring("Игроки", "Введи имена игроков через пробел:")
        if names_str:
            names = names_str.strip().split()
            game = Perudo(names, "", self)
            game.play()


if __name__ == "__main__":  # запуск
    GameGUI()
