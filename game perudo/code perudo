import math
from collections import deque
import tkinter as tk
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




def formula(claimk, claimval, knowndice, totaldice, maputo=False):  # функция расчета вероятности верности утверждений
   same = knowndice.count(claimval)
   if not maputo and claimval != 1:
       same += knowndice.count(1)
   remainder = claimk - same
   if remainder <= 0:
       return 1.0
   resres = 0.0
   n = totaldice
   for i in range(remainder, n + 1):
       combs = math.comb(n, i)
       if maputo:
           res = combs * (5 ** (n - i)) / (6 ** n)
       else:
           res = combs * (4 ** (n - i)) * (2 ** i) / (6 ** n)
       resres += res
   return resres




class Player:  # параметры игрока
   def __init__(self, name: str):
       self.name = name
       self.dice = 5
       self.status = "нейтральный"
       self.mpt = 0


   def update_status(self):  # функция изменения статуса игрока (зависит от кубиков)
       if self.dice == 0:
           self.status = "на мели, пройдоха"
       elif self.dice == 1 and self.mpt == 0:
           decision = simpledialog.askstring("Мапуто", f"Объявляет ли {self.name} статус мапуто? (да/нет)")
           if decision and decision.strip().lower() == "да":
               self.status = "мапуто"
               self.mpt = 1
           else:
               self.status = "нейтральный"
       else:
           self.status = "нейтральный"


   def dice_cast(self, manual: bool = False, app=None):  # функция броска кубиков игроками
       if manual:
           while True:
               entry = simpledialog.askstring("Бросок кубиков",
                                              f"{self.name}, введи значения своих костей (от 1 до 6) через пробел:")
               if entry is None:
                   continue
               values = entry.strip().split()
               try:
                   nums = list(map(int, values))
                   if len(nums) != self.dice:
                       messagebox.showerror("Ошибка", f"У тебя должно быть ровно {self.dice} костей!")
                       continue
                   if not all(1 <= val <= 6 for val in nums):
                       messagebox.showerror("Ошибка", "Кости должны быть числом от 1 до 6!")
                       continue
                   self.hand = nums
                   app.log(f"{self.name}, твой бросок: {" ".join(str(i) for i in self.hand)}")
                   break
               except ValueError:
                   messagebox.showerror("Ошибка", "Дружище, вводи только целые значения!")
       else:
           self.hand = []




class Perudo:  # параметры игры


   def __init__(self, player_names, username, gui):
       self.players = deque([Player(name) for name in player_names])
       self.username = username
       self.roundnumb = 0
       self.lastofus = 0
       self.gui = gui


   def log(self, message):  # переадресация из логики игры в интерфейс (связующая функция)
       self.gui.log(message)


   def get_active_players(self):  # функция проверки, какие игроки активны


       return [p for p in self.players if p.dice > 0]


   def first_player(self, name: str = None):  # функция определения 1 игрока в раунде


       if name is None:
           real_players = list(self.players)
           length = len(real_players)
           starter = (self.lastofus + 1) % length
           name = real_players[starter].name
       while self.players[0].name != name:
           self.players.rotate(-1)


   def get_user(self):  # функция вызова к пользователю
       for p in self.players:
           if p.name == self.username:
               return p
       return None


   def next_round(self):  # функция инициации раунда
       self.roundnumb += 1
       self.log(f'--- Раунд {self.roundnumb} ---')
       self.log("Текущее состояние игроков:")
       for p in self.players:  # выводим
           self.log(f"{p.name} : {p.dice} кубиков ({p.status})")
       for p in self.get_active_players():
           if p.name == self.username:
               p.dice_cast(manual=True, app=self)
           else:
               p.dice_cast(manual=False, app=self)


   def statement(self, name: str):  # функция реализации утверждений игрока
       entry = simpledialog.askstring("Утверждение", f'Введи утверждение игрока {name} (например: 6 2) или "Конец":')
       if entry is None:
           return self.statement(name)
       if entry.strip().lower() == "конец":
           return "end", None, None
       try:
           quant, val = map(int, entry.strip().split())
           if val < 1 or val > 6:
               messagebox.showerror("Ошибка", "Салага, ты ошибся. Номинал должен быть от 1 до 6.")
               return self.statement(name)
           return "claim", quant, val
       except:
           messagebox.showerror("Ошибка", "Введи два числа через пробел или 'Конец'!")
           return self.statement(name)


   def round_end(self):  # функция окончания раунда
       while True:
           loser = simpledialog.askstring("Конец раунда",
                                          "Введи имя проигравшего неудачника (или '-' если есть победивший):")
           if loser is None:
               continue
           if loser in [p.name for p in self.players]:
               for p in self.players:
                   if p.name == loser:
                       p.dice = max(0, p.dice - 1)
                       p.update_status()
                   elif p.dice == 1:
                       p.update_status()
               break
           elif loser == "-":
               while True:
                   winner = simpledialog.askstring("А кто победил?", "Введи имя победившего везунчика:")
                   if winner in [p.name for p in self.players]:
                       for p in self.players:
                           if p.name == winner:
                               p.dice += 1
                               p.update_status()
                           elif p.dice == 1:
                               p.update_status()
                       break
                   else:
                       messagebox.showerror("Ошибка", "Дружище, такого имени нет среди игроков.")
               break
           else:
               messagebox.showerror("Ошибка", "Дружище, такого имени нет среди игроков.")


   def other_dice(self):  # функция возвращает кол-во кубиков на руках других игроков (неизвестных)
       return sum(p.dice for p in self.players if p.name != self.username)


   def check_winner(self):  # функция проверки, есть ли в игре победитель
       active_players = self.get_active_players()
       if len(active_players) == 1:
           winner = active_players[0].name
           self.log("Йо-хо-хо, игра окончена! Победитель: " + winner)
           return True
       return False


   def play(self):  # главная функция - сама игра, вобравшая в себя остальные
       self.log("Рад видеть ваши рожи! Полных парусов и сухого пороха!")
       while True:
           self.username = simpledialog.askstring("А как тебя зовут?", "Приятель, введи свое имя:")
           if self.username in [p.name for p in self.players]:
               break
           else:
               messagebox.showerror("Ошибка", "Дружище, этого имени нет среди игроков.")
       while True:
           first = simpledialog.askstring("Первый игрок", "А кто начнет нашу битву? Введи имя:")
           if first in [p.name for p in self.players]:
               self.first_player(first)
               break
           else:
               messagebox.showerror("Ошибка", "Дружище, такого имени нет среди игроков.")


       while len(self.get_active_players()) > 1:
           self.next_round()
           idx = 0
           real_players = list(self.players)
           user = self.get_user()


           while True:
               idxidx = idx % len(real_players)
               real = real_players[idxidx]
               if real.dice == 0:
                   idx += 1
                   continue


               flag, quant, val = self.statement(real.name)
               if flag == "end":
                   self.lastofus = self.players.index(real)
                   self.round_end()
                   self.first_player()
                   break


               maputo_active = any(p.status == "мапуто" for p in self.get_active_players())
               prob = formula(quant, val, user.hand, self.other_dice(), maputo=maputo_active)
               self.log(f"Пират {real.name} прав с вероятностью: {round(prob * 100, 2)}% ({quant} {val})")
               idx += 1
           if self.check_winner():
               break
       self.log("Что ж, похоже, мы закончили. Славно намутили шторм в трюме, заглядывай еще.")




class GameGUI:


   def __init__(self):  # параметры интерфейса
       self.root = tk.Tk()
       self.root.title("Игра перудо")
       self.root.geometry("1250x800")
       self.bg_image = tk.PhotoImage(file="background.gif")
       self.background_label = tk.Label(self.root, image=self.bg_image)
       self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
       self.frame = tk.Frame(self.root, bg='#fdf6e3')
       self.frame.place(x=20, y=20, width=800, height=700)
       self.text = tk.Text(self.frame, wrap=tk.WORD, font=("Helvetica", 20), bg="#fdf6e3", relief=tk.FLAT)
       self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


       self.root.after(100, self.run_game)
       self.root.mainloop()


   def log(self, message):  # вывод окошек на экран
       self.text.insert(tk.END, message + "\n")
       self.text.see(tk.END)


   def run_game(self):  # запуск игры
       self.log("Ну что, тряхнем костями? Давай начинать игру.")
       names_str = simpledialog.askstring("Игроки", "Введи имена игроков через пробел:")
       if names_str:
           names = names_str.strip().split()
           game = Perudo(names, "", self)
           game.play()




if __name__ == "__main__":  # инициация всего кода
   GameGUI()

