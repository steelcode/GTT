import time
import rfidiot
import os
import copy
import datetime

class GTTMifareUL:
    mem_raw = []
    mem_struct = {'SN1':0x3,'BCC0':0x1,'SN2':0x4,'BCC1':0x1,'INT':0x1,'LOCK':0x2,'OTP':0x4,'DATA':0x30}
    mem_data={'SN1':'','BCC0':'','SN2':'','BCC1':'','INT':'','LOCK':'','OTP':'','DATA':''}
    myindex = ['SN1','BCC0','SN2','BCC1','INT','LOCK','OTP','DATA']
    buffer = []
    card = None
    def __init__(self):
        self.card = rfidiot.card
        self.card.select()
        self.mem_raw = []
        self.readCard()
        self.createRaw()
        self.createData()
    def readCard(self):
        for x in range(98):
            if self.card.readblock(x):
                self.buffer.append(self.card.data[:8])
            else:
                pass
    def createData(self):
        writed = 0
        for x in self.myindex:
            self.mem_data[x] =  self.mem_raw[0][writed:writed+self.mem_struct[x]*2]
            writed += self.mem_struct[x]*2
    def createRaw(self):
        newdata = ''
        for data in self.buffer:
            newdata += data
        self.mem_raw.append(newdata)
    def reverseLOCK(self):
        y = 0
        l0 = ''
        l1 = ''
        otpbits = self.printBlock('LOCK',16)
        for x in range(7,-1,-1):
            l0 = otpbits[y:y+1] + l0
            l1 = otpbits[y+8:y+9] + l1
            y += 1
        print l0,l1
        return (l0,l1)
    def writeToFile(self,name):
        fp = open(name,'w')
        for index in self.myindex:
            fp.write(self.card.ToBinary(self.mem_data[index]))
        fp.close()
    def readFromFile(self,name):
        try:
            fp = open(name,'r')
        except:
            pass
        lines = fp.readlines()
        print 'contenuto: ' + self.card.ToHex(lines[0])
        fp.close()
    def printMemData(self):
        for index in self.myindex:
            print index+' '+self.mem_data[index]
    def getBinaryBlock(self,blockname,mod):
        if blockname not in self.mem_struct.keys():
            print 'error'
            return None
        writed = 0
        out = ''
        bitlist = []
        for x in range(0,len(self.mem_data[blockname]),2):
            for y in range(7,-1,-1):
                if ((writed % mod) == 0 and writed>0):
                    bitlist.append(out)
                    out = ''
                    writed = 0
                out += '%s' % (int(self.mem_data[blockname][x:x+2],16) >> y & 1)
                writed += 1
        bitlist.append(out)
        #print out
        return bitlist
    def analyzeData(self,blockname):
        out = ''
        w = 0
        for x in range(0,len(self.mem_data[blockname]),2):
            if ((w % 6) == 0 and w>0):
                out += ' '
                w = 0
            out += '%02x' % (int(self.mem_data[blockname][x:x+2],16))
            w += 2
        #print out
        return out
    def writeBlock(self,operation,data):
        #self.card.writeblock(block,data)
        #print self.card.ToBinaryString(self.card.ToBinary('c0'))
        #bin='11111111'
        #print '%02x' % int(bin,2)
        pass
    '''
    def printBinaryBlock(self,blockname):
        if blockname not in self.myindex:
            return None
        return self.card.ToBinaryString(self.card.ToBinary(self.mem_data[blockname]))
    '''
    def countRide(self):
        cont = 0
        ridebyte = self.mem_data['OTP'][-2:]
        bitstring = self.card.ToBinaryString(self.card.ToBinary(ridebyte))
        for x in range(len(bitstring)):
            print bitstring[x]
            if bitstring[x]=='0':
                cont += 1
        return str(cont)
    def checkLOCK(self):
        locklist = self.getBinaryBlock('LOCK',8)
        l0 = locklist[0]
        l1 = locklist[1]
        ltmp = l1 + l0
        out = ''
        "from MSB to LSB"
        for y in range(len(ltmp)):
            out = ltmp[y] + out
        print out
        if int(out[3]) == 1: print 'OTP is locked'
        if out[0] == '1': print 'OTP is freezed'
    def bruteDate(self):
        "la data viene salvata in 3 byte il cui valore rappresenta i minuti trascorsi dalla gtt epoch 1104534000"
        gttepoch='2005/01/01 00:00'
        "secondi dal linux epoch al gtt epoch"
        gttfromlinux = time.mktime((2005,01,01,00,00,00,00,00,00))
        print int(gttfromlinux)
        '''
        prendo 3 byte dal campo data e li converto in int
        calcolo l'equivalente in secondi e lo aggiungo al gttfromlinux
        stampo la data corrispondente

        date = int(3byte,16)
        gttfromlinux+date
        '''
        


mygtt = GTTMifareUL()
mygtt.printMemData()
print   mygtt.getBinaryBlock('LOCK',8)
print 'ride rimanenti: ' + mygtt.countRide()
mygtt.checkLOCK()
mygtt.bruteDate()
#mygtt.analyzeData('DATA')
#print mygtt.mem_raw
#mygtt.reverseLOCK()
#mygtt.writeToFile('prova.raw')
#mygtt.readFromFile('prova.raw')
