import math
from collections import deque

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
            decision = input(f"Объявляет ли {self.name} статус мапуто: ")
            if decision.strip().lower() == "да":
                self.status = "мапуто"
            else:
                self.status = "нейтральный"
        else:  # 2+ кубика
            self.status = "нейтральный"

    def dice_cast(self, manual: bool = False):  # функция осуществления бросков
        if manual:  # наш вводим вручную
            while True:
                values = input(
                    "Дружище, введи значения своих костей (от 1 до 6) через пробел: ").strip().split()  # вводим наши значения через пробел. На всякий случай делаем strip от всего лишнего
                try:  # конструкция try-except - чтобы исключить варианты, когда введено что-то не то
                    nums = list(map(int, values))  # закидываем в список
                    if len(nums) != self.dice:  # проверка, чтобы количество введенных нами значений совпадало с текущим колвом кубиков
                        print(f"Салага, ты ошибся: у тебя должно быть ровно {self.dice} кубиков!")
                        continue
                    if not all(1 <= val <= 6 for val in
                               nums):  # проверка, что все введенные значения в диапазоне 1-6 (кубик-шестигранник)
                        print("Салага, ты ошибся: кости должны быть числом от 1 до 6!")
                        continue
                    self.hand = nums  # закидываем наш проверенный и правильный список в характеристики класса
                    break
                except ValueError:  # вторая часть конструкции try-except. ValueError - проверка на неподдерживаемые значения
                    print("Салага, ты ошибся: вводи только целые числа!")
        else:  # броски остальных - неизвестны, поэтому оставляем пустыми
            self.hand = []


class Perudo:

    def __init__(self, player_names, username):
        self.players = deque([Player(name) for name in
                              player_names])  # deque - двусторонняя очередь, короче, улучшенный список как раз для наших целей. Для него я импортировала модуль в начале.
        self.username = username  # username и player_names мы возьмем в конце, в стартовике кода
        self.roundnumb = 0  # ну и объявляшка номера раунда по порядку, когда игра не запущена - нулевой раунд
        self.lastofus = 0  # индекс игрока, объявившего "конец" в предыдущем раунде

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
        print('--- Раунд ' + str(self.roundnumb) + " ---")
        print("Текущее состояние игроков:")
        for p in self.players:  # выводим
            print(p.name + ' : ' + str(p.dice) + " кубиков (" + p.status + ")")

        # производим бросок кубиков по вышенаписанной функции
        for p in self.get_active_players():
            if p.name == self.username:
                p.dice_cast(manual=True)  # если игрок мы, то вводим сами
            else:
                p.dice_cast(manual=False)  # если игрок - не мы, то автоматом (пустые)

    def statement(self, name: str):  # вводим стейтементы других игроков
        entry = input('Морской волк, введи утверждение игрока ' + name + '(например: 6 2 [шесть двоек]) или "Конец": ')
        if entry.strip().lower() == "конец":
            return "end", None, None  # я пока обозначу то, что возвращается вот так - end и claim (в функции запуска это будут флаги-маркеры), может, потом еще поменяю
        try:  # конструкция try-except, как до этого у нас была в броске
            k, val = map(int,
                         entry.strip().split())  # вводим наши 6 2 (шесть двоек), k - количество, val - значение-номинал
            if val < 1 or val > 6:
                print("Салага, ты ошибся. Номинал должен быть от 1 до 6.")
                return self.statement(name)
            return "claim", k, val
        except:
            print("Салага, ты ошибся. Введи нормально.")  # если вводят что-то левое
            return self.statement(
                name)  # рекурсируем, т.е. возвращаем в начало и просим все ввести заново, если ввели что-то левое до этого

    def round_end(self):
        # Обрабатывает конец раунда
        while True:  # такая же ситуация с вводом первого по очередности игрока
            loser = input("Введи имя проигравшего неудачника (или '-' если есть победивший везунчик): ")
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
                    winner = input("Введите имя победившего везунчика: ")
                    if winner in [p.name for p in self.players]:
                        for p in self.players:
                            if p.name == winner:
                                p.dice += 1  # даем победившему кубик
                                p.update_status()
                            elif p.dice == 1:  # проверяем всех на мапуто
                                p.update_status()
                        break
                    else:
                        print("Салага, ты ввел что-то не то. Попробуй еще раз.")
                break
            else:
                print("Салага, ты ввел что-то не то. Попробуй еще рвз.")

    def other_dice(self):
        # Возвращает общее количество скрытых кубиков (всех кроме нашего игрока)
        return sum(p.dice for p in self.players if p.name != self.username)

    def check_winner(self):  # проверка на победителя всей игры - если остался только 1 чел с кубиками
        active_players = self.get_active_players()
        if len(active_players) == 1:  # функция get_active_players у нас создает список, значит мы можем проверить через длину этого списка
            winner = active_players[
                0].name  # собственно, если длина 1, то этого чела (нулевой и единственный элемент) и берем
            print("Йо-хо-хо, игра окончена! Победитель: " + winner)
            return True  # если true, то конец игры
        return False  # если false, то начинается следующий ход и по кругу

               def play(self):  # функция-основной цикл игры
        print("Рад видеть ваши рожи! Полных парусов и сухого пороха!")  # устанавливаем первого игрока
        while True:
            self.username = input("Приятель, введи свое имя: ").strip()
            if self.username in [p.name for p in
                                 self.players]:  # проверка на то, что наше имя есть среди всех игроков, введенных ранее
                break  # если все норм, то скип
            else:
                print(
                    "Салага, ты ввел что-то не то. Этого имени нет среди игроков")  # если не норм, то заново запускается while. И так по бесконечности, пока не будет break (правильный ввод)
        while True:  # такая же ситуация с вводом первого по очередности игрока
            first = input("А кто начнет нашу битву? Введи имя: ").strip()
            if first in [p.name for p in self.players]:
                self.first_player(first)
                break
            else:
                print("Салага, ты ввел что-то не то. Этого имени нет среди игроков")

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
                flag, k, val = self.statement(real.name)
                if flag == "end":
                    self.lastofus = self.players.index(real)  # перезаписываем индекс (остаток) закончившего игрока
                    self.round_end()  # если игрок сделал утверждение "конец", заканчиваем текущий раунд и начинаем с начала цикла
                    self.first_player()  # обновляем очередность ходов в результате конца раунда
                    break

                # проверяем статус мапуто и считаем вероятность
                maputo_active = any(
                    p.status == "мапуто" for p in self.get_active_players())  # статусы из функции про статусы))
                prob = formula(k, val, user.hand, self.other_dice(),
                               maputo=maputo_active)  # посчитанная через функцию формулы вероятность
                print(
                    f"Пират {real.name} прав(-а) с вероятностью: {round(prob * 100, 2)}%")  # выводим переведенную в проценты (с округлением)
                idx += 1  # продолжаем крутить игроков по кругу

            if self.check_winner():  # если образовался победитель
                break  # заканчиваем игру
        print("Что ж, игра завершена. Славно намутили шторм в трюме, заглядывай еще.")


print("Добро пожаловать в игру Перудо, пираты!")
names = input(
    "Ну что, сыграем? Введи имена игроков через пробел: ").split()  # самые-самые первые строки, которые выводит код
game = Perudo(names, "")  # инициирование игры (в class Perudo - names это player_names, “” - это username
game.play()
