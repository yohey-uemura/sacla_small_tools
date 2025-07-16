#! /usr/bin/env python
import math, re
from tkinter import *

mw = Tk('')
mw.title('Custom Param. Editor')

buttonframe = Frame(mw)
buttonframe.pack( side = TOP)

selected = StringVar(mw,'Eng')
text = Text(mw,font=("Arial",16),width=60,height=16)
def InsertText():
    text.delete('1.0',END)
    if selected.get() =='Eng':
        text.insert(END,"########################################################\n")
        text.insert(END,"#     how to write: 'start', 'end', 'step'             #\n")
        text.insert(END,"#            <Example (for Energy in eV)>             #\n")
        text.insert(END,"#                7110, 7160, 1  <= 'start', 'end', 'step' #\n")
        text.insert(END,"#                out=fe_xanes   <= output file name       #\n")
        text.insert(END,"########################################################\n")
        text.insert(END,"6530, 6537, 1\n")
        text.insert(END,"6537, 6545, 0.5\n")
        text.insert(END,"6545, 6575, 1\n")
        text.insert(END,"out=mn_xanes\n")
    elif selected.get() == 'Dly':
        text.insert(END,"########################################################\n")
        text.insert(END,"#     how to write: 'start', 'end', 'step'             #\n")
        text.insert(END,"#             <Example (for delay in ps)>              #\n")
        text.insert(END,"#"+f"{'t0 = 100 (in \"pls\") ':^54}"+"\n#")
        text.insert(END,"#"+f"{'-5,-1,1 <= start, end, step':^54}"+"\n#")
        text.insert(END,"#"+f"{'-1,1,0.1':^54}"+"\n#")
        text.insert(END,"#"+f"{'1,5,1':^54}"+"\n#")
        text.insert(END,"#"+f"{'out=fe_delay <=  output file name':^54}"+"\n#")
        text.insert(END,"########################################################\n")
        text.insert(END,"t0 = -300\n")
        text.insert(END,"-5,-1,1\n")
        text.insert(END,"-1,1,0.1\n")
        text.insert(END,"1,5.1,1\n")
        text.insert(END,"out=test_delay\n")
    elif selected.get() == 'Eng_with_D':
        text.insert(END, "########################################################\n")
        text.insert(END, "#     how to write: 'start', 'end', 'step'             #\n")
        text.insert(END, "#          <Example (for Energy in eV)>             #\n")
        text.insert(END, "#          E0 = 7120 ( in \"eV\")                    #\n")
        text.insert(END, "#          t0 = 100 (in \"pls\")                     #\n")
        text.insert(END, "#       7110, 7160, 1  <= 'start', 'end', 'step'     #\n")
        text.insert(END, "#        out=fe_xanes_wth_delay   <= output file name   #\n")
        text.insert(END, "########################################################\n")
        text.insert(END, "E0 = 6558\n")
        text.insert(END, "t0 = 100\n")
        text.insert(END, "6530, 6537, 1\n")
        text.insert(END, "6537, 6545, 0.5\n")
        text.insert(END, "6545, 6575, 1\n")
        text.insert(END, "out=mn_xanes_wth_delay\n")


InsertText()
r1 = Radiobutton(buttonframe, text='Energy', value='Eng', font = ('Arial',14), variable=selected,command=InsertText)
r2 = Radiobutton(buttonframe, text='Delay', value='Dly', font = ('Arial',14), variable=selected,command=InsertText)
r3 = Radiobutton(buttonframe, text='Energy with delay', value='Eng_with_D', font = ('Arial',14), variable=selected,command=InsertText)

r1.pack(side=LEFT)
r3.pack(side=LEFT)
r2.pack(side=LEFT)

text.pack()

lb0 = Label(mw, text='>>>>>> Output <<<<<<', font=("Arial",16))
lb0.pack()
out = Text(mw,font=("Arial",16),width=60,height=20)
out.pack()

def calcCC(E):
    return round(math.asin(12.3984/6.270832*1000/E)/math.pi*180/4*10**6)
def calcAng(E):
    return round(math.asin(12.3984/6.270832*1000/E)/math.pi*180,6)

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
        txt = '#Eng(eV), CCpos, CCneg\n'
        if '.csv' in fn:
            f = open(fn,'w')
        else:
            f = open(fn+'.csv','w')
        f.write('bl3_st1_pm003,	bl3_st1_pm005\n')
        for i, v in enumerate(CC):
            _e = params[i]
            txt+= f'{_e:.1f}, {v:d}, {-v:d}\n'
            f.write(f'{v:d}, {-v:d}\n')
        f.close()
        out.insert(END,txt)

    elif selected.get() == 'Dly':
        for l in tinput:
            if re.match(r'^#.+',l.rstrip()):
                pass
            elif re.match(r'^t0\s*=\s*-?\d+.\d+',l.rstrip()):
                t0 = int(l.rstrip().split('=')[-1])
            elif re.match(r'^-?\d+.+',l.rstrip()):
                start, end, step = [float(v) for v in l.split(',')]
                i = 0
                if step > 0:
                    while end > start + step*i:
                        params.append((start+step*i))
                        i += 1
                else:
                    while end < start + step*i:
                        params.append((start+step*i))
                        i += 1
            elif re.match(r'^(out=)\s*.+',l.rstrip()):
                fn = (l.split('=')[1])
            else:
                pass

        DELAYS = [ e for e in params]
        MOTORS = [ int(e*150) +t0 for e in params]
        txt = ''
        if '.csv' in fn:
            f = open(fn,'w')
        else:
            f = open(fn+'.csv','w')
        f.write('bl3_st2_pm001')
        for k, v in enumerate(MOTORS):
            f.write(f'{v:d}\n')
            txt+= f'{DELAYS[k]:.2f}, {v:d}\n'
        f.close()
        out.insert(END,'DELAY(ps) MOTOR(pls)\n')
        out.insert(END,txt)

    elif selected.get() == 'Eng_with_D':
        E0 = 0
        t0 = 0
        d = 8/1000
        c = 299792458
        for l in tinput:
            if re.match(r'^#.+', l.rstrip()):
                pass
            elif re.match(r'^E0\s*=\s*\d+.\d+', l.rstrip()):
                E0 = float(l.rstrip().split('=')[-1])
            elif re.match(r'^t0\s*=\s*\d+.\d+', l.rstrip()):
                t0 = int(l.rstrip().split('=')[-1])
            elif re.match(r'^\d+.+', l.rstrip()):
                start, end, step = [float(v) for v in l.split(',')]
                i = 0
                while end > start + step * i:
                    params.append(start + step * i)
                    i += 1
            elif re.match(r'^(out=)\s*.+', l.rstrip()):
                fn = (l.split('=')[1])
            else:
                pass
        # print (params)
        CC = [calcCC(e) for e in params]
        Angles = [calcAng(e) for e in params]
        dist = [2*2*d*math.sin(a/180*math.pi) for a in Angles]
        Ang_e0 = calcAng(E0)
        dist_at_e0 = 2*2*d*math.sin(Ang_e0/180*math.pi)
        diffs = [x - dist_at_e0 for x in dist]
        delays_in_fs = [round(x/c*1e15,1) for x in diffs]
        c_delay_positions = [int(x/1000*150)+t0 for x in delays_in_fs]

        # print (CC)
        txt = '#Eng(eV), CCpos, CCneg, delay(pls)\n'
        if '.csv' in fn:
            f = open(fn, 'w')
        else:
            f = open(fn + '.csv', 'w')
        f.write('bl3_st1_pm003,	bl3_st1_pm005,	bl3_st2_pm001\n')
        for i,v in enumerate(CC):
            _delay = c_delay_positions[i]
            eng = params[i]
            txt += f'{eng:.1f}, {v:d}, {-v:d}, {_delay:d}\n'
            f.write(f'{v:d}, {-v:d}, {_delay:d}\n')
        f.close()
        out.insert(END, txt)


B = Button(mw, text ="exec", command = make_params)
B.pack()
mw.mainloop()
