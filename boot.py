#by Lutz Herrmann, www.bitpilot.de, 19.2.2021
from machine import LCD
from machine import Pin, Map, ADC
import random
from time import sleep


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

colors = [
    (0, 0, 0),
    (20, 255, 62),
    (255, 0, 0),
    (10, 48, 255),
    (10, 246, 255),
    (246, 240, 0),
    (180, 34, 122),
]

Button_A = Pin(Map.WIO_KEY_A, Pin.IN)
Button_B = Pin(Map.WIO_KEY_B, Pin.IN)
Button_C = Pin(Map.WIO_KEY_C, Pin.IN)
Switch_UP = Pin(Map.WIO_5S_UP, Pin.IN)
Switch_DOWN = Pin(Map.WIO_5S_DOWN, Pin.IN)
Switch_LEFT = Pin(Map.WIO_5S_LEFT, Pin.IN)
Switch_RIGHT = Pin(Map.WIO_5S_RIGHT, Pin.IN)
Switch_PRESS = Pin(Map.WIO_5S_PRESS, Pin.IN)

adc = ADC(Pin(Map.WIO_MIC))

lcd = LCD()                           
lcd.fillScreen(lcd.color.BLACK) 
lcd.setTextSize(2)
lcd.setTextColor(lcd.color.GREEN)
strg="Wio-Tetris 1.4"
lcd.drawString(strg, 140, 20)
strg="Score = " + str(0)
lcd.drawString(strg, 140, 50)
strg="Level = " + str(3-2)
lcd.drawString(strg, 140, 80)

class Figure:
    x = 0
    y = 0

    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        for n in range(adc.read()%9):
            random.randint(0, 10)
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])
pass


class Tetris:
    ZEILEN = 20
    SPALTEN = 10
    XSTART = 3
    YSTART = 4
    BREITE = 11
    figure = None
    score = 0
    state = "start"
    field = []

    def __init__(self, zeilen, spalten):
        self.ZEILEN = zeilen
        self.SPALTEN = spalten
        self.field = []
        self.score = 0
        self.state = "start"
        for i in range(zeilen):
            new_line = []
            for j in range(spalten):
                new_line.append(0)
            pass
            self.field.append(new_line)
        pass
        self.DrawGitter()
        self.ClearFelder()
    pass

    def DrawGitter(self):
        for x in range(self.XSTART, (self.SPALTEN-1)*self.BREITE, self.BREITE-1):
            for y in range(self.YSTART, (self.ZEILEN-2)*self.BREITE, self.BREITE-1):
                lcd.drawRect(x, y, self.BREITE, self.BREITE, lcd.color565(125,125,125))
            pass
        pass
    pass

    def ClearFelder(self):
        for x in range(self.XSTART, (self.SPALTEN-1)*self.BREITE, self.BREITE-1):
            for y in range(self.YSTART, (self.ZEILEN-2)*self.BREITE, self.BREITE-1):
                lcd.fillRect(x+1, y+1, self.BREITE-2, self.BREITE-2, lcd.color565(0,0,0))
            pass
        pass
    pass

    def Index2Px(self,x,y):
        px = self.XSTART + x*(self.BREITE-1)
        py = self.YSTART + y*(self.BREITE-1)
        if(x < self.SPALTEN and y < self.ZEILEN): 
            return (px, py)
        pass
    pass

    def SetRect(self,ix,iy,color):
        #x, y = self.Index2Px(ix,iy)
        x = self.XSTART + ix*(self.BREITE-1)
        y = self.YSTART + iy*(self.BREITE-1)
        lcd.fillRect(x+1, y+1, self.BREITE-2, self.BREITE-2, lcd.color565(color[0],color[1],color[2]))
    pass

    def DrawFigure(self):
        if game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in game.figure.image():
                        self.SetRect((j + self.figure.x), (i + self.figure.y), colors[self.figure.color])
    
    def DelFigure(self):
        if game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in game.figure.image():
                        self.SetRect((j + self.figure.x), (i + self.figure.y), BLACK)
                    pass
                pass
            pass
        pass
    pass

    def UpdateFelder(self):
        for i in range(self.SPALTEN):
            for j in range(self.ZEILEN):
                if self.field[j][i] > 0:
                    self.SetRect(i,j,colors[self.field[j][i]])
                pass
            pass
        pass
    pass       

    def new_figure(self):
        self.figure = Figure(3, 0)
    pass

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.ZEILEN - 1 or \
                            j + self.figure.x > self.SPALTEN - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > 0:
                        intersection = True
        return intersection
    pass

    def break_lines(self):
        lines = 0
        for i in range(1, self.ZEILEN):
            zeros = 0
            for j in range(self.SPALTEN):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.SPALTEN):
                        self.field[i1][j] = self.field[i1 - 1][j]
                    pass
                pass
            pass
        pass
        if lines > 0:
            self.score += lines ** 2
            strg="score = " + str(self.score)
            lcd.drawString(strg, 140, 50)
        pass
    pass

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
                pass
            pass
        pass
        self.break_lines()
        self.ClearFelder()
        self.UpdateFelder()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"
        pass
    pass

pass #Class Tetris


game = Tetris(20, 10)
game.new_figure()
running = True
beginner = True
ticker = 0
level = 2

while running:
    if (game.state == "start" and not beginner):
        if(ticker >= level):
            game.figure.y += 1
            if(not game.intersects()):
                game.figure.y -= 1
                game.DelFigure()
                game.figure.y += 1
            else:
                game.figure.y -= 1
                game.freeze()
            pass
            ticker = 0
        ticker += 1
    pass
    if(game.state == "gameover"):
        lcd.setTextColor(lcd.color.RED)
        lcd.drawString("GAMEOVER!", 140, 110)
        running = False
    pass
    game.DrawFigure()
    sleep(0.15) #Verzögerung bzgl. Tastenabfrage
    if(Switch_DOWN.value() == 0): #unten
        game.figure.y += 1
        if(not game.intersects()):
            game.figure.y -= 1
            game.DelFigure()
            game.figure.y += 1
        else:
            game.figure.y -= 1
            game.freeze()
        pass
    elif(Switch_UP.value() == 0): #rotate
        old = game.figure.rotation
        game.figure.rotate()
        if(not game.intersects()):
            game.figure.rotation = old
            game.DelFigure()
            game.figure.rotate()
        else:
            game.figure.rotation = old
        pass
    elif(Switch_RIGHT.value() == 0): #rechts
        game.figure.x += 1
        if(not game.intersects()):
            game.figure.x -= 1
            game.DelFigure()
            game.figure.x += 1
        else:
            game.figure.x -= 1
        pass
    elif(Switch_LEFT.value() == 0): #links
        game.figure.x -= 1
        if(not game.intersects()):
            game.figure.x += 1
            game.DelFigure()
            game.figure.x -= 1
        else:
            game.figure.x += 1
        pass
    elif(Button_B.value() == 0): #Wechsel beginner ja/nein
        beginner = not beginner
    elif (Button_A.value() == 0): #Ende
        running = False
        game.ClearFelder()
    elif (Button_C.value() == 0):
        if(level >= 3):
            level = 1
        else:
            level += 1
        strg="Level = " + str(3-level)
        lcd.drawString(strg, 140, 80)
    pass
pass


