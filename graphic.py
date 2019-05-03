#!/usr/bin/env python
# -*- coding: utf-8 -*-

#black cant place = 2
#White cant place = 3
#white piece on tab = -1
#black piece on tab = 1

from Tkinter import *
from PIL import ImageTk, Image
from utils import *
import time
import os
import socket
from ctypes import *
import atexit

lib = cdll.LoadLibrary("./algo.so")
statetab = []
blackorwhite = [-1]
capturewin = [0, 0, 0, 0, 0]
victorydone = False
countturn = [0, 1, 0]
lan = [0, 0]
cas = None
cac = None


class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        master.geometry("{0}x{1}+0+0".format(
        master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        self.master.geometry(self._geom)
        self._geom=geom


def close():
    global lan
    global cas
    global cac
    if (lan[0] == 1):
        print "close connexion"
        cas.send("-1")
        cas.close()
    if (lan[0] == 2):
        print "close connexion"
        cac.send("-1")
        cac.close()

atexit.register(close)

def victory(canvas, player, sentence):
    global victorydone
    victorydone = True
    if (player == -1):
        r = "Victory White player" + sentence
    else:
        r = "Victory Black player" + sentence
    canvas.unbind("<Button-1>")
    canvas.unbind("<Motion>")
    canvas.create_text(250, 510, text=r, font=("Arial", 30), fill="pink")

def pos(pos, pos2):
    if pos < 0 or pos > 18 :
        return False
    if pos2 < 0 or pos2 > 18 :
        return False
    return True

def increment_compt(s, compt):

    if (s == 'L' or s == 'R'):
        if (compt['L'] == 0):
            compt['T'] += 1
        compt['L'] += 1

    if (s == 'U' or s == 'D'):
        if (compt['U'] == 0):
            compt['T'] += 1
        compt['U'] += 1

    if (s == 'UR' or s == 'DL'):
        if (compt['UR'] == 0):
            compt['T'] += 1
        compt['UR'] += 1

    if (s == 'UL' or s == 'DR'):
        if (compt['DR'] == 0):
            compt['T'] += 1
        compt['DR'] += 1

    return compt

def check_double_tree(player):
    sides = {
        'L': {'y': 0, 'x': -1},
        'U': {'y': -1, 'x': 0},
        'D': {'y': 1, 'x': 0},
        'R': {'y': 0, 'x': 1},
        'UR': {'y': -1, 'x': 1},
        'DR': {'y': 1, 'x': 1},
        'UL': {'y': -1, 'x': -1},
        'DL': {'y':1, 'x': -1}
    }
    compt = {'L' : 0, 'U' : 0, 'UR' : 0, 'DR' : 0, 'T' : 0}
    compt2 = {'L' : 0, 'U' : 0, 'UR' : 0, 'DR' : 0, 'T' : 0}
    for y in xrange(19):
        for x in xrange(19):
            for s in sides.keys():
                y2 = sides[s]['y']
                x2 = sides[s]['x']
                if (pos(y + y2, x + x2) == True and pos(y + (y2 * 2), x + (x2 * 2)) == True and (statetab[y][x] == 0 or statetab[y][x] == 2 or statetab[y][x] == 3)):
                    if (statetab[y + y2][x + x2] == player and statetab[y + (y2 * 2)][x + (x2 * 2)] == player):
                        compt2 = increment_compt(s, compt2)
                    elif (pos(y + (y2 * 3), x + (x2 * 3)) == True):
                        if ((statetab[y + y2][x + x2] == 0 or statetab[y + y2][x + x2] == 2 or statetab[y + y2][x + x2] == 3) and statetab[y + (y2 * 2)][x + (x2 * 2)] == player and statetab[y + (y2 * 3)][x + (x2 * 3)] == player):
                            compt2 = increment_compt(s, compt2)

                if (pos(y + y2, x + x2) == True and pos(y + (y2 * -1), x + (x2 * -1)) == True and (statetab[y][x] == 0 or statetab[y][x] == 2 or statetab[y][x] == 3) and (s == 'L' or s == 'U' or s == 'UR' or s == 'DR')):
                    if (statetab[y + y2][x + x2] == player and statetab[y + (y2 * -1)][x + (x2 * -1)] == player):
                        compt = increment_compt(s, compt)
                    elif (pos(y + (y2 * 3), x + (x2 * 3)) == True):
                        if ((statetab[y + y2][x + x2] == 0 or statetab[y + y2][x + x2] == 2 or statetab[y + y2][x + x2] == 3) and statetab[y + (y2 * 2)][x + (x2 * 2)] == player and statetab[y + (y2 * 3)][x + (x2 * 3)] == player):
                            compt = increment_compt(s, compt)
            if (compt['T'] >= 2 or compt2['T'] >= 2):
                if (player == 1):
                    statetab[y][x] = 2
                if (player == -1):
                    statetab[y][x] = 3
            compt = {'L' : 0, 'U' : 0, 'UR' : 0, 'DR' : 0, 'T' : 0}
            compt2 = {'L' : 0, 'U' : 0, 'UR' : 0, 'DR' : 0, 'T' : 0}
            for t in sides.keys():
                y2 = sides[t]['y']
                x2 = sides[t]['x']
                if (pos(y + y2, x + x2) == True and pos(y + (y2 * 2), x + (x2 * 2)) == True and (statetab[y][x] == 0 or statetab[y][x] == 2 or statetab[y][x] == 3)):
                    if (statetab[y + y2][x + x2] == player and statetab[y + (y2 * 2)][x + (x2 * 2)] == player):
                        if (pos(y + (y2 * -1), x + (x2 * -1)) == True):
                            if (statetab[y + (y2 * -1)][x + (x2 * -1)] == player * -1):
                                statetab[y][x] = 0
                        if (pos(y + (y2 * 3), x + (x2 * 3)) == True):
                            if (statetab[y + (y2 * 3)][x + (x2 * 3)] == player * -1):
                                statetab[y][x] = 0
                    elif (pos(y + (y2 * 3), x + (x2 * 3)) == True and pos(y + (y2 * 4), x + (x2 * 4)) == True):
                        if (statetab[y + (y2 * 2)][x + (x2 * 2)] == player and statetab[y + (y2 * 3)][x + (x2 * 3)] == player):
                            if (statetab[y + y2][x + x2] == player * -1 or statetab[y + (y2 * 4)][x + (x2 * 4)] == player * -1):
                                statetab[y][x] = 0

                if (pos(y + y2, x + x2) == True and pos(y + (y2 * -1), x + (x2 * -1)) == True and pos(y + (y2 * -2), x + (x2 * -2)) == True and pos(y + (y2 * 2), x + (x2 * 2)) == True  and (statetab[y][x] == 0 or statetab[y][x] == 2 or statetab[y][x] == 3) and (s == 'L' or s == 'U' or s == 'UR' or s == 'DR')):
                    if (statetab[y + y2][x + x2] == player and statetab[y + (y2 * -1)][x + (x2 * -1)] == player):
                        if (statetab[y + (y2 * -2)][x + (x2 * -2)] == player * -1 or statetab[y + (y2 * 2)][x + (x2 * 2)] == player * -1):
                            statetab[y][x] = 0
                    elif (pos(y + (y2 * 3), x + (x2 * 3)) == True and pos(y + (y2 * 4), x + (x2 * 4)) == True):
                        if (statetab[y + (y2 * 2)][x + (x2 * 2)] == player and statetab[y + (y2 * 3)][x + (x2 * 3)] == player):
                            if (statetab[y + y2][x + x2] == player * -1 or statetab[y + (y2 * 4)][x + (x2 * 4)] == player * -1):
                                statetab[y][x] = 0

def check_capture_tree(x2, y2, player, capture):
    if (capture != []):
        statetab[y2][x2] = 0
        return 0
    if (player == -1):
        return 3
    if (player == 1):
        return 4

def check_equality(canvas):
    is_empty = True
    for line in statetab:
        for p in line:
            if p == 0:
                is_empty = False
                break
        if not is_empty:
            break
    if is_empty == True:
        canvas.unbind("<Button-1>")
        canvas.unbind("<Motion>")
        canvas.create_text(250, 510, text="equality", font=("Arial", 30), fill="pink")

def checkcapture(x2, y2, player, img3, canvas):
    check_equality(canvas)
    check_double_tree(player)
    check_double_tree(player * -1)
    if (check_victory(statetab, y2, x2, player) == True):
        victory(canvas, player, " by alignement")
    t = place_piece(statetab, y2, x2, player, True)
    if (t != []):
        for f in t:
            img3[f[0]][f[1]] = ""
            statetab[f[0]][f[1]] = 0

        if (player == 1):
            capturewin[0] += 1

        else:
            capturewin[1] += 1
    if (capturewin[0] >= 5):
        victory(canvas, 1, " by capture")
    elif (capturewin[1] >= 5):
        victory(canvas, -1, " by capture")

def sharetab(statetab):
    fichier = open("tab.txt", "w")
    for t in statetab:
        for f in t:
            if (f == -1):
                fichier.write('4')
            else:
                fichier.write(str(f))

def gainline(canvas, x, y, x2, y2, color, state, img3, tmppion, advice, gamemode, depth, param, order):
    sharetab(statetab)
    starttime = time.time()
    lib.Algorithm(param)
    endtime = str(time.time() - starttime) + "000"
    i = 0
    endtime2 = ""
    endtime2 = endtime2 + endtime[0]
    while (endtime[i] != '.'):
        i += 1
        endtime2 = endtime2 + endtime[i]
    try :
        r = open("tab_out.txt", "r")
    except (OSError, IOError) as e:
        errexit("error open")
    t = r.read()
    pos = []
    for p in t.split(','):
        pos.append(int(p))
    if (pos[0] == -1 or pos[1] == -1):
        errexit("error in AI return")
    showadvice(pos, canvas, x, y, img3, tmppion, blackorwhite, advice, gamemode, depth, order)
    r =  "AI time suggestion : " + endtime2 + endtime[i + 1] + endtime[i + 2] + endtime[i + 3] + 's'
    canvas.delete(advice[1])
    advice[1] = canvas.create_text(250, 110, text=r, font=("Arial", 24), fill="#FFFFFF")

def showpion(canvas, x, y, x2, y2, color, state, img3, tmppion, advice, gamemode, depth, order):
    if (color == -1):
        if (state == 0):
            path = "img/circle-grey50.png"
            tmppion[0] = ImageTk.PhotoImage(Image.open(path).resize((60,60)))
            canvas.create_image(x[x2] - 2, y[y2] - 2, image=tmppion[0], anchor='nw')
            return
        if (state == 1):
            path = "img/circle-grey.png"
            statetab[y2][x2] = -1
            countturn[0] += 1
            checkcapture(x2, y2, -1, img3, canvas)
        if (state == 2):
            path = "img/circle-grey50.png"
            advice[0] = ImageTk.PhotoImage(Image.open(path).resize((60,60)))
            canvas.create_image(x[x2] -2, y[y2] -2, image=advice[0], anchor='nw')
            return
        if (state == 3):
            path = "img/circle-grey50r.png"
            tmppion[0] = ImageTk.PhotoImage(Image.open(path).resize((55,55)))
            canvas.create_image(x[x2], y[y2], image=tmppion[0], anchor='nw')
            return
        img3[y2][x2] = ImageTk.PhotoImage(Image.open(path).resize((60,60)))
        canvas.create_image(x[x2] -2, y[y2] -2, image=img3[y2][x2], anchor='nw')
        if gamemode == 4:
            advice[0] = ""
        if (gamemode == 0 or gamemode == 3 or (gamemode == 1 and order == 0)):
            gainline(canvas, x, y, x2, y2, color, state, img3, tmppion, advice, gamemode, depth, 1, order)
    if (color == 1):
        if (state == 0):
            path = "img/black-circle50.png"
            tmppion[0] = ImageTk.PhotoImage(Image.open(path).resize((55,55)))
            canvas.create_image(x[x2], y[y2], image=tmppion[0], anchor='nw')
            return
        if (state == 1):
            path = "img/black-circle.jpg"
            statetab[y2][x2] = 1
            countturn[0] += 1
            checkcapture(x2, y2, 1, img3, canvas)
        if (state == 2):
            path = "img/black-circle50.png"
            advice[0] = ImageTk.PhotoImage(Image.open(path).resize((55,55)))
            canvas.create_image(x[x2], y[y2], image=advice[0], anchor='nw')
            return
        if (state == 4):
            path = "img/black-circle50r.png"
            tmppion[0] = ImageTk.PhotoImage(Image.open(path).resize((55,55)))
            canvas.create_image(x[x2], y[y2], image=tmppion[0], anchor='nw')
            return
        img3[y2][x2] = ImageTk.PhotoImage(Image.open(path).resize((55,55)))
        canvas.create_image(x[x2], y[y2], image=img3[y2][x2], anchor='nw')
        if gamemode == 3:
            advice[0] = ""
        if (gamemode == 0 or gamemode == 4 or (gamemode == 1 and order == 1)):
            gainline(canvas, x, y, x2, y2, color, state, img3, tmppion, advice, gamemode, depth, -1, order)
    if (countturn[0] >= 2):
        countturn[1] += 1
        countturn[0] = 0
    return

def errexit(string):
    print "error : ", string
    sys.exit()

def ignore():
    return "break"

def eventclick(canvas, x, y, dic, frame, x2, y2, img3, tmppion, blackorwhite, advice, gamemode, depth, order, fenetre):
    tab = canvas.find_overlapping(x, y, x + 100, y + 100) 
    if (blackorwhite[0] == 1):
        tmp = 1
    if (blackorwhite[0] == -1):
        tmp = -1
    if (cas != None):
        tmp = 1
    if (cac != None):
        tmp = -1
    for p in tab:
        for f in frame:
            if (f == p and (statetab[dic[p][1]][dic[p][0]] == 1 or statetab[dic[p][1]][dic[p][0]] == -1)):
                return
            if (f == p and statetab[dic[p][1]][dic[p][0]] == 2 and blackorwhite[0] == 1):

                return
            if (f == p and statetab[dic[p][1]][dic[p][0]] == 3 and blackorwhite[0] == -1):
                return
            if (f == p):
                showpion(canvas, x2, y2, dic[p][0], dic[p][1], tmp, 1, img3, tmppion, advice, gamemode, depth, order)
                if (blackorwhite[0] == 1):
                    blackorwhite[0] = -1
                else :
                    blackorwhite[0] = 1
                if ((gamemode == 1 or gamemode == 2) and victorydone == False):
                    sharetab(statetab)
                    starttime = time.time()
                    lib.Algorithm(1, capturewin[1], capturewin[0])
                    endtime = str(time.time() - starttime) + "000"
                    i = 0
                    endtime2 = ""
                    endtime2 = endtime2 + endtime[0]
                    while (endtime[i] != '.'):
                        i += 1
                        endtime2 = endtime2 + endtime[i]
                    try :
                        r = open("tab_out.txt", "r")
                    except (OSError, IOError) as e:
                        errexit("error open")
                    t = r.read()
                    pos = []
                    for p in t.split(','):
                        pos.append(int(p))
                    if (pos[0] == -1 or pos[1] == -1):
                        errexit("error in AI return")
                    showpion(canvas, x2, y2, pos[1], pos[0], blackorwhite[0], 1, img3, tmppion, advice, gamemode, depth, order) 
                    r =  "AI time : " + endtime2 + endtime[i + 1] + endtime[i + 2] + endtime[i + 3] + 's'
                    canvas.delete(advice[2])
                    advice[2] = canvas.create_text(250, 170, text=r, font=("Arial", 24), fill="#FFFFFF")
                    if (blackorwhite[0] == 1):
                        blackorwhite[0] = -1
                    else :
                        blackorwhite[0] = 1
                if (cas != None):
                    tmp = -1
                    cas.send(str(p))
                    if (victorydone != True):
                        try:
                            p = int(cas.recv(1024))
                        except socket.error, exc:
                            print "Caught exception socket.error : %s" % exc
                        if (p == -1):
                            sys.exit()
                        if (p != -1):
                            showpion(canvas, x2, y2, dic[p][0], dic[p][1], tmp, 1, img3, tmppion, advice, gamemode, depth, order)
                        countturn[0] += 1
                if (cac != None):
                    tmp = 1
                    cac.send(str(p))
                    if (victorydone != True):
                        try:
                            p = int(cac.recv(1024))
                        except socket.error, exc:
                            print "Caught exception socket.error : %s" % exc
                        if (p == -1):
                            sys.exit()
                        if (p != -1):
                            showpion(canvas, x2, y2, dic[p][0], dic[p][1], tmp, 1, img3, tmppion, advice, gamemode, depth, order)
                        countturn[0] += 1
                r = "Round : " + str(countturn[1])
                if countturn[2] != 0:
                    canvas.delete(countturn[2])
                countturn[2] = canvas.create_text(250, 910, text=r, font=("Arial", 30), fill="White")

                r = "Black's captures : " + str(capturewin[0])
                canvas.delete(capturewin[3])
                capturewin[3] = canvas.create_text(250, 710, text=r, font=("Arial", 30), fill="White")

                r = "White's captures : " + str(capturewin[1])
                canvas.delete(capturewin[4])
                capturewin[4] = canvas.create_text(250, 610, text=r, font=("Arial", 30), fill="White")

                return

def eventclick50(canvas, x, y, dic, frame, x2, y2, img3, check, tmppion, blackorwhite, advice, gamemode, depth, order):
    if (blackorwhite[0] == 1) :
        tmp = 1
    if (blackorwhite[0] == -1):
        tmp = -1
    if (cas != None):
        tmp = 1
    if (cac != None):
        tmp = -1

    state = 0
    tab = canvas.find_overlapping(x, y, x + 100, y + 100)
    for p in tab:
        for f in frame:
            if (f == p and check[0] == p):
                return
            if ((f == p and statetab[dic[p][1]][dic[p][0]] == 0) or (f == p and statetab[dic[p][1]][dic[p][0]] == 2 and blackorwhite[0] == -1) or (f == p and statetab[dic[p][1]][dic[p][0]] == 3 and blackorwhite[0] == 1)):
                check[0] = p
                showpion(canvas, x2, y2, dic[p][0], dic[p][1], tmp, 0, img3, tmppion, advice, gamemode, depth, order)
                return
            elif (f == p and statetab[dic[p][1]][dic[p][0]] == 2 and  blackorwhite[0] == 1):
                check[0] = p
                state = check_capture_tree(dic[p][0], dic[p][1], blackorwhite[0], place_piece(statetab, dic[p][1], dic[p][0], blackorwhite[0], True))
                showpion(canvas, x2, y2, dic[p][0], dic[p][1], tmp, state, img3, tmppion, advice, gamemode, depth, order)
                return
            elif (f == p and statetab[dic[p][1]][dic[p][0]] == 3 and blackorwhite[0] == -1):
                check[0] = p
                state = check_capture_tree(dic[p][0], dic[p][1], blackorwhite[0], place_piece(statetab, dic[p][1], dic[p][0], blackorwhite[0], True))
                showpion(canvas, x2, y2, dic[p][0], dic[p][1], tmp, state, img3, tmppion, advice, gamemode, depth, order)
                return

def showadvice(pos, canvas, x, y, img3, tmppion, blackorwhite, advice, gamemode,depth, order):
    if (blackorwhite[0] == 1) :
        tmp = -1
    if (blackorwhite[0] == -1):
        tmp = 1
    if (cas != None):
        tmp = 1
    if (cac != None):
        tmp = -1

    showpion(canvas, x, y, pos[1], pos[0], tmp, 2, img3, tmppion, advice, gamemode, depth, order)
    return

def reset(fenetre):
    global victorydone
    victorydone = False
    if (lan[0] == 1):
        cas.send("-1")
        cas.close()
    if (lan[0] == 2):
        cac.send("-1")
        cac.close()
    lan[0] = 0
    fenetre.destroy()
    start()

def init(fenetre, b, b2, b3, b4, b5, b6, depth, gamemode, order, canvas):
    ligne1 = []
    ligne2 = []
    ligne3 = []
    ligne4 = []

    global statetab
    global blackorwhite
    global capturewin
    global countturn

    canvas.delete("all")
    advice = [0, 0, 0]
    b.place_forget()
    b2.place_forget()
    b3.place_forget()
    b4.place_forget()
    b5.place_forget()
    b6.place_forget()
    blackorwhite = [-1]
    countturn = [0, 1, 0]
    tmppion = [0]
    check = [0]
    img3 = []
    statetab = []
    capturewin = [0, 0, 0, 0, 0]

    for i in xrange(19):
        statetab.append([])
        for i2 in  xrange(19):
            statetab[i].append(0)

    for i in xrange(19):
        img3.append([])
        for i2 in  xrange(19):
            img3[i].append(0)

    fenetre.title("Gomoku")
    app = FullScreenApp(fenetre)
    fenetre.resizable(0,0)

    path = "img/wood2.jpg"
    img = ImageTk.PhotoImage(Image.open(path).resize((2560, 1440)))
    canvas.create_image(0, 0, image=img, anchor='nw')

    img2 = ImageTk.PhotoImage(Image.open("img/wood3.jpg").resize((73, 38)))
    b = Button(canvas, text="reset", command= lambda: reset(fenetre), highlightthickness = 0, bd = 0, image = img2)
    b.place(x=200, y=1000) 
    x = 50
    y = 500
    for i in xrange(21):
        ligne3.append(canvas.create_line(y, 49, y, 1291, width = 7, fill = "white"))
        ligne4.append(canvas.create_line(499, x, 2041, x, width = 7, fill = "white"))
        x += 62
        y += 77

    x = 50
    y = 500
    for i in xrange(21):
        ligne1.append(canvas.create_line(y, 49, y, 1291, width = 5))
        ligne2.append(canvas.create_line(499, x, 2041, x, width = 5))
        x += 62
        y += 77

    x = []
    y = []
    x2 = 550
    y2 = 85

    for i2 in xrange(19):
        y.append(y2)
        y2 += 62
    for i in xrange(19):
        x.append(x2)
        x2 += 77

    frame = []
    x2 = 540
    x3 = 612
    y2 = 82
    y3 = 140
    for i in xrange(19):
        for i2 in xrange(19):
            frame.append(canvas.create_rectangle(x2, y2, x3, y3, outline = ""))
            x2 += 77
            x3 += 77
        i2 = 0
        x2 = 540
        x3 = 612
        y2 += 62
        y3 += 62

    dic = {}
    i = 0
    i2 = 0
    for p in frame:
        if i == 19:
            i = 0
            i2 += 1
        dic[p] = [i, i2]
        i += 1

    if (order == 0) :
        sharetab(statetab)
        starttime = time.time()
        lib.Algorithm(1, capturewin[1], capturewin[0])
        endtime = str(time.time() - starttime) + "000"
        i = 0
        endtime2 = ""
        endtime2 = endtime2 + endtime[0]
        while (endtime[i] != '.'):
            i += 1
            endtime2 = endtime2 + endtime[i]
        try :
            r = open("tab_out.txt", "r")
        except (OSError, IOError) as e:
            errexit("error open")
        t = r.read()
        pos = []
        for p in t.split(','):
            pos.append(int(p))
        if (pos[0] == -1 or pos[1] == -1):
            errexit("error in AI return")
        showpion(canvas, x, y, pos[1], pos[0], blackorwhite[0], 1, img3, tmppion, advice, gamemode, depth, order) 
        r =  "AI time : " + endtime2 + endtime[i + 1] + endtime[i + 2] + endtime[i + 3] + 's'
        canvas.delete(advice[2])
        advice[2] = canvas.create_text(250, 170, text=r, font=("Arial", 24), fill="#FFFFFF")
        if (blackorwhite[0] == 1):
            blackorwhite[0] = -1
        else :
            blackorwhite[0] = 1
    canvas.bind("<Button-1>", lambda event: eventclick(canvas, event.x, event.y, dic, frame, x, y, img3, tmppion, blackorwhite, advice, gamemode, depth, order, fenetre))
    canvas.bind("<Motion>", lambda event: eventclick50(canvas, event.x, event.y, dic, frame, x, y, img3, check, tmppion, blackorwhite, advice, gamemode,depth, order))
    canvas.pack(expand=TRUE, fill=BOTH, side = TOP)
    if (cas != None):
        if (countturn[1] == 1):
            p = int(cas.recv(1024))
            if (p == -1):
                sys.exit()
            showpion(canvas, x, y, dic[p][0], dic[p][1], -1, 1, img3, tmppion, advice, gamemode, depth, order)
            countturn[0] += 1
    fenetre.mainloop()

def initclient(fenetre, b, b2, b3, b4, b5, b6, depth, gamemode, order, canvas):
    global cas
    try :
        cas = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cas.connect(('localhost', 12800))
    except socket.error, exc:
            print "Caught exception socket.error : %s" % exc
            sys.exit()
    var = "connexion established"
    cas.send(var)
    lan[0] = 1
    init(fenetre, b, b2, b3, b4, b5, b6, 3, gamemode, 1, canvas)

def initserver(fenetre, b, b2, b3, b4, b5, b6, depth, gamemode, order, canvas):
    global cac
    try:
        connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion_principale.bind(('', 12800))
        connexion_principale.listen(5)
        cac, infos_connexion = connexion_principale.accept()
        var = cac.recv(2048)
        lan[0] = 2
        print var
    except socket.error, exc:
            print "Caught exception socket.error : %s" % exc
            sys.exit()
    init(fenetre, b, b2, b3, b4, b5, b6, 3, gamemode, 1, canvas)

def start1v1lan(fenetre, b, b2, b3, b4, b5, b6, depth, gamemode, canvas):

    canvas.delete("all")
    b.place_forget()
    b2.place_forget()
    b3.place_forget()
    b4.place_forget()
    b5.place_forget()
    b6.place_forget()

    fenetre.title("Choose type of connection")

    b = Button(canvas, text="Client", command= lambda: initclient(fenetre, b, b2, b3, b4, b5, b6, 3, gamemode, 1, canvas), bg="blue", width="40", height="3")
    b.place(relx=1, x=-250, y=475, anchor=NE)
    b2 = Button(canvas, text="Server", command= lambda: initserver(fenetre, b, b2, b3, b4, b5, b6, 3, gamemode, 1, canvas), width="40", height="3")
    b2.place(relx=1, x=-250, y=825, anchor=NE)
    b3 = Button(canvas, text="return", command= lambda: start1v1(fenetre, b, b2, b3, b4, b5, b6, 3, 1, canvas), width="40", height="3")
    b3.place(relx=1, x=-250, y=1200, anchor=NE)
    path = "img/wood2.jpg"
    img = ImageTk.PhotoImage(Image.open(path).resize((2560, 1440)))
    canvas.create_image(0, 0, image=img, anchor='nw')
    path = "img/gomoku.png"
    img2 = ImageTk.PhotoImage(Image.open(path))
    canvas.create_image(200, 475, image=img2, anchor='nw')

    canvas.pack(expand=TRUE, fill=BOTH, side = TOP)
    fenetre.mainloop()


def start1v1(fenetre, b, b2, b3, b4, b5, b6, depth, gamemode, canvas):

    canvas.delete("all")
    b.place_forget()
    b2.place_forget()
    b3.place_forget()
    b4.place_forget()
    b5.place_forget()
    b6.place_forget()

    fenetre.title("Choose mode")

    b = Button(canvas, text="On same PC", command= lambda: init(fenetre, b, b2, b3, b4, b5, b6, 3, gamemode, 1, canvas), bg="blue", width="40", height="3")
    b.place(relx=1, x=-250, y=475, anchor=NE)
    b2 = Button(canvas, text="LAN", command= lambda: start1v1lan(fenetre, b, b2, b3, b4, b5, b6, 3, gamemode, canvas), width="40", height="3")
    b2.place(relx=1, x=-250, y=825, anchor=NE)
    b3 = Button(canvas, text="return", command= lambda: reset(fenetre), width="40", height="3")
    b3.place(relx=1, x=-250, y=1200, anchor=NE)
    path = "img/wood2.jpg"
    img = ImageTk.PhotoImage(Image.open(path).resize((2560, 1440)))
    canvas.create_image(0, 0, image=img, anchor='nw')
    path = "img/gomoku.png"
    img2 = ImageTk.PhotoImage(Image.open(path))
    canvas.create_image(200, 475, image=img2, anchor='nw')

    canvas.pack(expand=TRUE, fill=BOTH, side = TOP)
    fenetre.mainloop()


def start2(fenetre, b, b2, b3, b4, b5, b6, depth, gamemode, canvas):


    canvas.delete("all")
    b.place_forget()
    b2.place_forget()
    b3.place_forget()
    b4.place_forget()
    b5.place_forget()
    b6.place_forget()

    fenetre.title("Choose your player")

    b = Button(canvas, text="Player play first", command= lambda: init(fenetre, b, b2, b3, b4, b5, b6, 3, gamemode, 1, canvas), bg="blue", width="40", height="3")
    b.place(relx=1, x=-250, y=475, anchor=NE)
    b2 = Button(canvas, text="IA play first", command= lambda: init(fenetre, b, b2, b3, b4, b5, b6, 3, gamemode, 0, canvas), width="40", height="3")
    b2.place(relx=1, x=-250, y=825, anchor=NE)
    b3 = Button(canvas, text="return", command= lambda: reset(fenetre), width="40", height="3")
    b3.place(relx=1, x=-250, y=1200, anchor=NE)
    path = "img/wood2.jpg"
    img = ImageTk.PhotoImage(Image.open(path).resize((2560, 1440)))
    canvas.create_image(0, 0, image=img, anchor='nw')
    path = "img/gomoku.png"
    img2 = ImageTk.PhotoImage(Image.open(path))
    canvas.create_image(200, 475, image=img2, anchor='nw')

    canvas.pack(expand=TRUE, fill=BOTH, side = TOP)
    fenetre.mainloop()

def start():
    fenetre = Tk()
    global lib
    global lan
    if (lan[1] == 0):
        lan = [0, 0]
    if (lan[1] == 1):
        lan = [0, 1]
    fenetre.title("Choose Mode")
    app = FullScreenApp(fenetre)
    fenetre.resizable(0,0)

    canvas = Canvas(fenetre, width=1501, height=1201)

    b = Button(canvas, text="1v1 mode", command= lambda: init(fenetre, b, b2, b3, b4, b5, b6, 3, 0, 1, canvas), width="40", height="3")
    b.place(relx=1, x=-250, y=175, anchor=NE)
    b2 = Button(canvas, text="1vIA mode", command= lambda: start2(fenetre, b, b2, b3, b4, b5, b6, 3, 1, canvas), width="40", height="3")
    b2.place(relx=1, x=-250, y=350, anchor=NE)
    b3 = Button(canvas, text="1vIA mode sans suggestion", command= lambda: start2(fenetre, b, b2, b3, b4, b5, b6, 3, 2, canvas), width="40", height="3")
    b3.place(relx=1, x=-250, y=525, anchor=NE)
    b4 = Button(canvas, text="1v1 mode sans suggestion P1", command= lambda: init(fenetre, b, b2, b3, b4, b5, b6, 3, 3, 1, canvas), width="40", height="3")
    b4.place(relx=1, x=-250, y=700, anchor=NE)
    b5 = Button(canvas, text="1v1 mode sans suggestion P2", command= lambda: init(fenetre, b, b2, b3, b4, b5, b6, 3, 4, 1, canvas), width="40", height="3")
    b5.place(relx=1, x=-250, y=875, anchor=NE)
    b6 = Button(canvas, text="1v1 mode sans suggestion", command= lambda: start1v1(fenetre, b, b2, b3, b4, b5, b6, 3, 5, canvas), width="40", height="3")
    b6.place(relx=1, x=-250, y=1050, anchor=NE)

    path = "img/wood2.jpg"
    img = ImageTk.PhotoImage(Image.open(path).resize((2560, 1440)))
    canvas.create_image(0, 0, image=img, anchor='nw')
    path = "img/gomoku.png"
    img2 = ImageTk.PhotoImage(Image.open(path))
    canvas.create_image(200, 475, image=img2, anchor='nw')

    canvas.pack(expand=TRUE, fill=BOTH, side = TOP)
    fenetre.mainloop()

if __name__ == "__main__":
    start()
