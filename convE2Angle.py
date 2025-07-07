#! /usr/bin/env python
import math
from tkinter import *

#print (12.3984/6.270832*1000/10210)

wndw = Tk()
wndw.title('CC <=> Energy')
wndw.geometry("700x150+10+10")

selected = StringVar(wndw,'toE')
r1 = Radiobutton(wndw, text='=>Energy', value='toE', variable=selected)
r2 = Radiobutton(wndw, text='=>Angle', value='toCC', variable=selected)
r3 = Radiobutton(wndw, text='=>d-spacing', value='toDs', variable=selected)
r1.pack(side=LEFT)
r2.pack(side=LEFT)
r3.pack(side=LEFT)


lb0 = Label(wndw, text='d [A]')
lb0.place(x=10,y=20)
t0=Entry(wndw, bd=2,width=15)
t0.configure({"background": 'white'})
t0.place(x=60,y=20)
t0.insert(END,'3.135560')

lbl1 = Label(wndw,text='Angle /deg.')
lbl1.place(x=220,y=20)
t1=Entry(wndw, bd=2,width=15)
t1.configure({"background": 'lightyellow'})
t1.place(x=300,y=20)
t1.insert(END,'12.7185')

lbl2 = Label(wndw,text='E[eV]')
lbl2.place(x=460,y=20)
t2=Entry(wndw, bd=2,width=15)
t2.configure({"background": 'lightblue'})
t2.place(x=510,y=20)
t2.insert(END, str(round(12398.52/(2*float(t0.get())*math.sin(float(t1.get())/180*math.pi)),1)))


def calc():
    print (selected.get())
    d = float(t0.get())
    if selected.get() == 'toE':
        t2.delete(0, END)
        try:
            cc = float(t1.get())
            Eng = 12398.52/(2*d*math.sin(cc/180*math.pi))
            t2.insert(END, str(round(Eng,1)))
        except Exception as e:
            print (e)

    elif selected.get() == 'toCC':
        t1.delete(0, END)
        try:
            E = float(t2.get())
            t1.insert(END, str(round(math.asin(12398.52/(2*d*E))*180/math.pi,4)))
        except Exception as e:
            print (e)

    elif selected.get() == 'toDs':
        t0.delete(0, END)
        try:
            E = float(t2.get())
            A = float(t1.get())
            t0.insert(END, str(round(12398.52/E/2/math.sin(A/180*math.pi),6)))
        except Exception as e:
            print (e)

B = Button(wndw, text ="Calc.", command = calc)
B.place(x=300,y=80)
r1.place(x=10,y=80)
r2.place(x=100,y=80)
r3.place(x=190,y=80)
wndw.mainloop()


# E = 12.3984/(6.270832*math.sin((int(cc.get())*4/10**6)*math.pi/180.0))*1000
# theta = (1/math.asin(E/12.3984/1000*6.270832))/math.pi*180/4*10**6
