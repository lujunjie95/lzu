# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 10:34:42 2018

@author: lu junjie

Keysight N5227A Controlling the Measurment 

"""


import visa
import time
import datetime
from csv import reader
import numpy as np
import matplotlib.pyplot as pl

Freq_start = 13      # GHz
Freq_stop =  28      # GHz
Step    =    20     # kHz
Bandwidth =  10     # kHz


SW1_n = [1, 2, 3, 4, 5, 6, 5, 6]
SW2_n = [1, 2, 3, 4, 5, 6, 6, 5]

name_aim = ['line1', 'line2', 'thru', 'short', 'an12', 'an34', 'an14', 'an32']

file = list(range(len(SW1_n)))
for fi in range(len(SW1_n)):
    file[fi] = r'D:\superconducting\TRL\SW1_n'+str(SW1_n[0])+'_SW2_n'\
    +str(SW2_n[0])+'_'+str(name_aim[fi])+'.s2p'

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def Divid_Fre(Freq_stop, Freq_start, Step):
    T_points = (Freq_stop - Freq_start) / Step * 1e6
    Total_points = T_points
    pna_max_points = 100001
    for separate in range(1,50):
        if T_points > pna_max_points - 15:
            T_points = Total_points
            T_points = round(Total_points / (separate + 1))
        else:
            break
    Parts = separate
    Part_points = T_points
    Freq_part = list(range(Parts + 1))
    Freq_part[0] = int(Freq_start * 1e9)
    Freq_part[-1] = int(Freq_stop * 1e9)
    for tt in range(1,Parts):
        Freq_part[tt] = int(round((Freq_start + Part_points * Step / 1e6 * tt) * 1e9))
    return Parts, Freq_part

def Connect_VNA():
    rm = visa.ResourceManager()
    vna = rm.open_resource('TCPIP0::A-N5227A-70663.local::inst0::INSTR')  #192.168.1.6    
    vna.timeout = 120000
    vna.chunk_size = 9000000
    return vna

def Set_VNA():
    vna.write('FORM:BORD SWAP')
    vna.write('FORM REAL,64')
    vna.write('CALC:PAR:MNUM 1')    


def VNA_Measure_Set(Freq_part, ii):
    vna.write('SENS:FREQ:STAR %d' %  Freq_part[ii])
    vna.write('SENS:FREQ:STOP %d' %  Freq_part[ii+1])
    vna.write('SENS:SWE:STEP %d' %  int(Step * 1e3))
    vna.write('SENS:BWID %dKHZ' %  Bandwidth)
    
def VNA_Measure_and_Transform(S_ALL, ii, L):
    vna.write('SENS:SWE:MODE SING;*wai')
    S_ALL[ii] = vna.query_binary_values('CALC:DATA:SNP:PORT? "1,2"', datatype='d',container=np.array)
    vna.query('*OPC?')
    S_ALL[ii] = np.transpose(np.reshape(S_ALL[ii], (9,L)))
    if ii > 0:
        S_ALL[ii] = np.delete(S_ALL[ii], [0], axis=0)
    return S_ALL

def Save_data(S_ALL, file):
    S_save_part = "S_ALL" + ",S_ALL".join(str([i]) for i in list(range(Parts)))
    S_save_sum = np.vstack((eval(S_save_part)))
    Measure_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    filename = 'D:/low_temperature_record/20181130_19_00.csv'
    with open(filename) as raw_data:
        readers = reader(raw_data,delimiter=',')    
        last_t = list(readers)    
    temperature = last_t[-1]
    Comments = 'Date of measurement: ' + Measure_time + '\n'\
    + 'Frequency range: ' + str(Freq_start) + ' - ' + str(Freq_stop) + ' GHz' \
    + ' ( ' + str(Step) +' kHz resolution)' + '\n' + 'Frequency part: '+ str(Freq_part) + '\n' \
    + 'Bandwidth: ' + str(Bandwidth) + ' kHz'\
    + '\n' + 'Time Channel A Channel B Channel C Channel D Channel E Channel F Channel G Channel H'\
    + '\n' + str(temperature) + '\n' + 'f [Hz] Re(S11) Im(S11) Re(S21) Im(S21) Re(S12) Im(S12) Re(S22) Im(S22)'\
    + '\n' + ' Hz S  RI   R 50'
    np.savetxt(file, S_save_sum, header = Comments)
    return S_save_sum
    
def Plot_Figure(S_save_sum):
    F = S_save_sum[:,0]
    S11_Comp = S_save_sum[:,1] + S_save_sum[:,2]*1j
    S21_Comp = S_save_sum[:,3] + S_save_sum[:,4]*1j
    S12_Comp = S_save_sum[:,5] + S_save_sum[:,6]*1j
    S22_Comp = S_save_sum[:,7] + S_save_sum[:,8]*1j
    pl.plot(F,abs(S11_Comp))
    pl.plot(F,abs(S21_Comp))
    pl.plot(F,abs(S12_Comp))
    pl.plot(F,abs(S22_Comp))
    pl.show()
    
def Connect_Control_Switch(SW1,SW2):
    rm = visa.ResourceManager()
    switch = rm.open_resource('TCPIP0::192.168.1.101::5025::SOCKET')  #192.168.1.101
    if SW1 == 1:
        switch.write('ROUT:CLOS (@101:109)')
    if SW1 == 2:
        switch.write('ROUT:CLOS (@101:109)')
        switch.write('ROUT:OPE (@104)')
    if SW1 == 3:
        switch.write('ROUT:CLOS (@101:109)')
        switch.write('ROUT:OPE (@104,102)')
    if SW1 == 4:
        switch.write('ROUT:CLOS (@101:109)')
        switch.write('ROUT:OPE (@104,102,103)')
    if SW1 == 5:
        switch.write('ROUT:CLOS (@101:109)')
        switch.write('ROUT:OPE (@104,102,103,101)')
    if SW1 == 6:
        switch.write('ROUT:CLOS (@101:109)')
        switch.write('ROUT:OPE (@104,102,103,101,109)')
        
    if SW2 == 1:
        switch.write('ROUT:CLOS (@201:209)')
    if SW2 == 2:
        switch.write('ROUT:CLOS (@201:209)')
        switch.write('ROUT:OPE (@204)')
    if SW2 == 3:
        switch.write('ROUT:CLOS (@201:209)')
        switch.write('ROUT:OPE (@204,202)')
    if SW2 == 4:
        switch.write('ROUT:CLOS (@201:209)')
        switch.write('ROUT:OPE (@204,202,203)')
    if SW2 == 5:
        switch.write('ROUT:CLOS (@201:209)')
        switch.write('ROUT:OPE (@204,202,203,201)')
    if SW2 == 6:
        switch.write('ROUT:CLOS (@201:209)')
        switch.write('ROUT:OPE (@204,202,203,201,209)')
        
def Apply_Cal_Set(which_part):
    Cal_name = 'CalSet_TRL'+'_part_'+str(which_part+1)

#    vna.write('SENS:CORR:CSET:NAME "%s"' % Cal_name)        #only use in E-Cal rename, but should save first
    vna.write('SENS:CORR:CSET:ACT "%s",1' % Cal_name)
    
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

for mt in range(len(SW1_n)):
    Parts, Freq_part = Divid_Fre(Freq_stop, Freq_start, Step)
    Connect_Control_Switch(SW1_n[mt],SW2_n[mt])
    vna = Connect_VNA()
    start = time.perf_counter()
    S_ALL = list(range(Parts))
    for ii in range(Parts):
        vna.write('*rst')
        Set_VNA()
        VNA_Measure_Set(Freq_part, ii)
        L = int(vna.query('SENS:SWE:POIN?'))
        Apply_Cal_Set(ii)
        S_ALL = VNA_Measure_and_Transform(S_ALL, ii, L)
        if ii == Parts - 1: 
            S_save_sum = Save_data(S_ALL, file[mt])
            Plot_Figure(S_save_sum)
        print('Measurement Complete:',ii+1)
    end = time.perf_counter()
    print(end - start)

    
    

    
    
    # filename = 'C:/Users/meap/Desktop/I_V Sweep RESET [(1000) ; 2018-10-15 23_50_12].csv'
    # with open(filename) as raw_data:
    #     readers = reader(raw_data,delimiter=',')    
    #     last_t = list(readers) 
    # a=np.array(last_t[742::1534])
    # b=np.array(last_t[1523::1534])
    # c=a[:,2]
    # d=b[:,2]
    # e=np.zeros(1000)
    # f=np.zeros(1000)
    # for i in range(len(d)):
    #     e[i]=float(d[i])
    # for i in range(len(c)):
    #     f[i]=float(c[i])    
    # pl.plot(range(1000,0,-1),f[:],'*')
    # pl.plot(range(1000,0,-1),e[:],'*')
    # pl.ylim((1000, 1e8))