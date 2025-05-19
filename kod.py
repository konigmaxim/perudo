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
   sovpav = knowndice.count(claimval)  # считает количество названных игроком значений среди наших кубиков
   if not maputo and claimval != 1:
       sovpav += knowndice.count(1)  # добавляем к посчитанному единицы-джокеры (если не мапуто)
   ostatok = claimk - sovpav  # остаток - сколько нужно кубиков с таким значением среди не наших (см. для обоснования файл с формулами, стр. 3 под графиком)
   if ostatok <= 0:
       return 1.0  # если среди наших уже набралось достаточно, то вероятность 100%
   res = 0.0  # базовая вероятность, к которой мы уже плюсуем - иначе получается кривой return. лучше объявить это до цикла
   n = totaldice
   # считаем вероятность по формуле (см. файл с формулами)
   for i in range(ostatok, n + 1):  # нам же подходит не только заявленное количество, но и большее - см. файл
       combs = math.comb(n, i)  # встроенная функция из библиотеки math про сочетания, работает на версиях 3.8 и выше!
       if maputo:
           # формула для статуса мапуто (без джокеров-единиц)
           itog = combs * (5 ** (n - i)) / (6 ** n)
       else:
           # базовая формула (с джокерами-единицами)
           itog = combs * (4 ** (n - i)) * (2 ** i) / (6 ** n)
       res += itog
   return res




class Player:


   def __init__(self, name: str):
       self.name = name  # имя - строкой
       self.dice = 5  # у каждого игрока в начале 5 кубиков, int
       self.hand = []  # значения кубиков игрока которые потом  введутся (пустой список, потом будем обновлять через split)
       self.status = "нейтральный"  # статус - по дефолту нейтральный, или мапуто (1 кубик)/проигравший


   def update_status(
           self):  # dice и status берем из предыдущей моей штуки, а потом будем обновлять уже в коде самой игры
       if self.dice == 0:  # потом в коде пропишем, что кто с 0,тот ход скипается
           self.status = "на мели, пройдоха"
       elif self.dice == 1:
           self.status = "мапуто"
       else:  # 2+ кубика
           self.status = "нейтральный"


   def brosok(self, manual: bool = False):  # функция осуществления бросков
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


   def get_active_players(self):
       # возвращаем список игроков, у которых еще есть кубики
       return [p for p in self.players if p.dice > 0]


   def first_player(self, name: str):
       # устанавливаем первого игрока в раунде
       while self.players[0].name != name:
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
               p.brosok(manual=True)  # если игрок мы, то вводим сами
           else:
               p.brosok(manual=False)  # если игрок - не мы, то автоматом (пустые)


   def statement(self, name: str):  # вводим стейтементы других игроков
       entry = input('Морской волк, введи утверждение игрока ' + name + '(например: 6 2) или "Конец": ')
       if entry.strip().lower() == "конец":
           return "end", None, None  # я пока обозначу то, что возвращается вот так - end и claim (в функции запуска это будут флаги-маркеры), может, потом еще поменяю
       try:  # конструкция try-except, как до этого у нас была в броске
           k, val = map(int,
                        entry.strip().split())  # вводим наши 6 2 (шесть двоек), k - количество, val - значение-номинал
           return "claim", k, val
       except:
           print("Салага, ты ошибся. Введи нормально.")  # если вводят что-то левое
           return self.statement(
               name)  # рекурсируем, т.е. возвращаем в начало и просим все ввести заново, если ввели что-то левое до этого


   def round_end(self):
       # Обрабатывает конец раунда
       loh = input("Введи имя проигравшего неудачника (или '-' если есть победивший везунчик): ")
       if loh != "-":
           for p in self.players:
               if p.name == loh:
                   p.dice = max(0, p.dice - 1)
                   p.update_status()
       else:
           winner = input("Введите имя победившего везунчика: ")
           for p in self.players:
               if p.name == winner:
                   p.dice += 1
                   p.update_status()


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
                   self.round_end()  # если игрок сделал утверждение "конец", заканчиваем текущий раунд и начинаем с начала цикла
                   break


               # проверяем статус мапуто и считаем вероятность
               maputo_active = any(
                   p.status == "мапуто" for p in self.get_active_players())  # статусы из функции про статусы))
               prob = formula(k, val, user.hand, self.other_dice(),
                              maputo=maputo_active)  # посчитанная через функцию формулы вероятность
               print(
                   f"Пират {real.name} прав с вероятностью: {round(prob * 100, 2)}%")  # выводим переведенную в проценты (с округлением)
               idx += 1  # продолжаем крутить игроков по кругу


           if self.check_winner():  # если образовался победитель
               break  # заканчиваем игру
       print("Что ж, игра завершена. Славно намутили шторм в трюме, заглядывай еще.")




print("Игра Перудо")
names = input(
   "Ну что, сыграем? Введи имена игроков через пробел: ").split()  # самые-самые первые строки, которые выводит код
game = Perudo(names, "")  # инициирование игры (в class Perudo - names это player_names, “” - это username
game.play()

