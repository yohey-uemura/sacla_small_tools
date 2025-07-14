#! /usr/bin/env python
import math, re
from tkinter import *

mw = Tk('')

buttonframe = Frame(mw)
buttonframe.pack( side = TOP)

selected = StringVar(mw,'Eng')
r1 = Radiobutton(buttonframe, text='Energy', value='Eng', font = ('Arial',14), variable=selected)
r2 = Radiobutton(buttonframe, text='Delay', value='Dly', font = ('Arial',14), variable=selected)
r1.pack(side=LEFT)
r2.pack(side=LEFT)

text = Text(mw,font=("Arial",16),width=60,height=16)
text.insert(END,"########################################################\n")
text.insert(END,"#     how to write: 'start', 'end', 'step'             #\n")
text.insert(END,"#        Example (for Energy in eV): 7110, 7120, 1     #\n")
text.insert(END,"#        Example (for Delay in ps):  0.0, 1.0, 0.1    #\n")
text.insert(END,"########################################################\n")
text.insert(END,"7100, 7105, 1\n")
text.insert(END,"7105, 7112, 0.3\n")
text.insert(END,"7112, 7180, 1\n")
text.insert(END,"out=fe_xanes\n")
text.pack()

lb0 = Label(mw, text='>>>>>> Output <<<<<<', font=("Arial",16))
lb0.pack()
out = Text(mw,font=("Arial",16),width=60,height=20)
out.pack()

def calcCC(E):
    return round(math.asin(12.3984/6.270832*1000/E)/math.pi*180/4*10**6)

def make_params():
    out.delete('1.0',END)
    params = []
    tinput = (text.get("1.0",END)).split('\n')
    fn = 'params.csv'
    if selected.get() == 'Eng':
        for l in tinput:
            if re.match(r'^#.+',l.rstrip()):
                pass
            elif re.match(r'^\d+.+',l.rstrip()):
                start, end, step = [float(v) for v in l.split(',')]
                i = 0
                while end > start + step*i:
                    params.append(start+step*i)
                    i += 1
            elif re.match(r'^(out=)\s*.+',l.rstrip()):
                fn = (l.split('=')[1])
            else:
                pass
        # print (params)
        CC = [calcCC(e) for e in params]
        # print (CC)
        txt = ''
        if '.csv' in fn:
            f = open(fn,'w')
        else:
            f = open(fn+'.csv','w')
        for v in CC:
            txt+= f'{v:d}, {-v:d}\n'
            f.write(f'{v:d}, {-v:d}\n')
        f.close()
        out.insert(END,txt)
    elif selected.get() == 'Dly':
        for l in tinput:
            if re.match(r'^#.+',l.rstrip()):
                pass
            elif re.match(r'^-?\d+.+',l.rstrip()):
                start, end, step = [float(v) for v in l.split(',')]
                i = 0
                while end > start + step*i:
                    params.append(start+step*i)
                    i += 1
            elif re.match(r'^(out=)\s*.+',l.rstrip()):
                fn = (l.split('=')[1])
            else:
                pass
        DELEYS = [int(e*150) for e in params]
        txt = ''
        if '.csv' in fn:
            f = open(fn,'w')
        else:
            f = open(fn+'.csv','w')
        for v in DELEYS:
            f.write(f'{v:d}\n')
            txt+= f'{v:d}\n'
        f.close()
        out.insert(END,txt)

B = Button(mw, text ="exec", command = make_params)
B.pack()
mw.mainloop()
