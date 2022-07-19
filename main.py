import tkinter as tk
import random
from threading import Lock

COLORS = ['dark slate blue', 'yellow2', 'green2', 'magenta3', 'gray1', 'Dark Orange2']       #List COLORS

class Latar():
    tinggi_latar = 20
    lebar_latar = 10        #Udah optimal 2 2 nya jangan diubah
    tetromino =  [
        [(0,0), (0,1), (1,0), (1,1)],       #Kubus
        [(0,0), (1,0), (1,1), (2,1)],       #Zig Zag Kanan
        [(0,1), (1,0), (1,1), (2,1)],       #T
        [(0,0), (0,1), (1,1), (2,1)],       #L
        [(0,1), (1,1), (2,1), (2,0)],       #L invers
        [(0,1), (1,1), (2,1), (3,1)],       #Lurus
        [(0,1), (1,0), (1,1), (2,0)],       #Zig Zag kiri
    ]       #Konsepnya itu (-y, x) dan akan berlaku bagi koordinat kedepannya
    skoring_tetris = (0, 40, 100, 300, 1200)   #Null, Satu baris, Dua baris, 3 baris, Tetris (4 baris)

    def __init__(self):
        self.bidang = [[0 for c in range(Latar.lebar_latar)] for r in range(Latar.tinggi_latar)]        #Ini bidangnya
        self.level = 0              #Init level
        self.skor_tetris = 0        #Init skor
        self.progress = 0           #Init kemajuan ke level selanjutnya
        self.eksponensi = 0         #Algoritma generator syarat
        self.kalah = 0              #Init kondisi kalah
        self.sinkron = Lock()       #Sinkron menggunakan fitur lock biar method gravitasi juga sinkron sama gerak turun pemain
        self.tetromino_ulang()      #Streaming tetromino

    def tetromino_ulang(self):
        self.spawntetromino = [-2, Latar.lebar_latar//2]     #Tempat
        self.tetrominopilih = random.choice(Latar.tetromino)[:]        #Pemilihan Tetromino
        self.tetrominowarna = random.randint(1, len(COLORS) - 1)        #Pemilihan warna
        self.kalah = any(not self.cek_nabrak_gak(r, c) for (r, c) in self.get_koord_tetro())        #Kalo kalah koordinat tetromino nya nyinggung cek_nabrak_gak

    def get_koord_tetro(self):
        return [(r + self.spawntetromino[0], c + self.spawntetromino[1]) for r, c in self.tetrominopilih]       #Get koordinat

    def buat_tetromino(self):
        for (r, c) in self.get_koord_tetro():
            self.bidang[r][c] = self.tetrominowarna     #Akan mewarnai kotak kotak sesuai koordinat tetromino yang udah dibikin di atas tadi
        bidang_baru = [baris for baris in self.bidang if any(kotak == 0 for kotak in baris)]
        baris_terisi = len(self.bidang) - len(bidang_baru)#Biar bisa tetris donkzz
        self.eksponensi = 1000**1.2**(self.level)       #Jadi syaratnya itu 1000 di pangkat 1,2 yang juga dipangkat lagi di level berapa (silahkan edit 100 dan 1.2 kalo mau)
        if self.skor_tetris // self.eksponensi >= 1:
            self.progress += 1                          #Biar eksponensi bekerja
        self.bidang = [[0] * Latar.lebar_latar for x in range(baris_terisi)] + bidang_baru
        self.skor_tetris += Latar.skoring_tetris[baris_terisi] * (self.level + 1)
        self.level = self.progress // 1
        self.tetromino_ulang()                          #Streaming tetromino 

    def get_warna(self, r, c):
        return self.tetrominowarna if (r, c) in self.get_koord_tetro() else self.bidang[r][c]       #Get warna buat warnain tetromino

    def cek_nabrak_gak(self, r, c):
        return r < Latar.tinggi_latar and 0 <= c < Latar.lebar_latar and (r < 0 or self.bidang[r][c] == 0)       #Biar ga keluar frame sama ngga nembus tetronimo lain

    def gerak(self, a, b):      #Method nggerakin tetromino
        with self.sinkron:
            if self.kalah:
                return

            if all(self.cek_nabrak_gak(r + a, c + b) for r, c in self.get_koord_tetro()):
                self.spawntetromino = [self.spawntetromino[0] + a, self.spawntetromino[1] + b]
            elif a == 1 and b == 0:        
                self.kalah = any(r < 0 for (r, c) in self.get_koord_tetro())        
                if not self.kalah:
                    self.buat_tetromino()

    def rotasi(self):       #Biar bisa dirotasi tetrominonya
        with self.sinkron:
            if self.kalah:
                self.__init__()         #Entah kenapa pake ini bisa nge reset game overnya ¯\_(ツ)_/¯
                return

            ydin = [r for (r, c) in self.tetrominopilih]
            xdin = [c for (r, c) in self.tetrominopilih]
            ukuran = max(max(ydin) - min(ydin), max(xdin) - min(xdin))
            hasil_rotasi = [(c, ukuran - r) for (r, c) in self.tetrominopilih]      #Algoritma rotasi clockwise
            anti_nembok = self.spawntetromino[:]        #Anti nembok ngefix bug tetromino yang dipinggir ga bisa dirotate
            koord_tempo = [(r + self.spawntetromino[0], c + self.spawntetromino[1]) for r, c in hasil_rotasi]
            minx = min(c for r, c in koord_tempo)
            maxx = max(c for r, c in koord_tempo)
            maxy = max(r for r, c in koord_tempo)
            anti_nembok[1] -= min(0, minx)
            anti_nembok[1] += min(0, Latar.lebar_latar - (1 + maxx))
            anti_nembok[0] += min(0, Latar.tinggi_latar - (1 + maxy))
            koord_tempo = [(r + anti_nembok[0], c + anti_nembok[1]) for r, c in hasil_rotasi]
            if all(self.cek_nabrak_gak(r, c) for r, c in koord_tempo):
                self.tetrominopilih, self.spawntetromino = hasil_rotasi, anti_nembok


#=========================================================================---> -------====Template dasar GUI====-------
class Tampilan(tk.Frame):                                                     
    def __init__(self,master=None):                                           # Template frame (do not edit)
        super().__init__(master)                                              # Template frame (do not edit)
        self.latar = Latar()                                                  
        self.pack()                                                           
        self.bikin_latar()
        self.gravitasi()        #Di apply donk gravitasinya

    def gravitasi(self):
        self.latar.gerak(1, 0)      #Gerak jatuh 1 koordinat ke bawah
        self.update()
        self.master.after(int(1000*(0.66**self.latar.level)), self.gravitasi)       #After itu fitur timer dan dengan satuan milisekon jadi 1000 yang didalem berarti 1000 milisekon (sisanya hanya operator)

    def bikin_latar(self):
        size_keping = 30                                                      #Ukuran kotak kotaknya
        self.canvas = tk.Canvas(self, height = size_keping*self.latar.tinggi_latar, width = size_keping*self.latar.lebar_latar, bg = 'green')# Sebagai frame (bg tertutup jadi tidak signifikan)
        self.canvas.focus_set()
        self.canvas.bind('w', lambda _: (self.latar.rotasi(), self.update()))           #Puterin pencet panah atas (searah jarum jam)
        self.canvas.bind('a', lambda _: (self.latar.gerak(0, -1), self.update()))       #Gerak ke kiri pencet panah kiri
        self.canvas.bind('s', lambda _: (self.latar.gerak(1, 0), self.update()))        #Gerak ke bawah pencet panah bawah
        self.canvas.bind('d', lambda _: (self.latar.gerak(0, 1), self.update()))        #Gerak ke kanan pencet panah kanan
        self.canvas.bind('<Up>', lambda _: (self.latar.rotasi(), self.update()))           #Puterin pencet  (searah jarum jam)
        self.canvas.bind('<Left>', lambda _: (self.latar.gerak(0, -1), self.update()))       #Gerak ke kiri pencet a
        self.canvas.bind('<Down>', lambda _: (self.latar.gerak(1, 0), self.update()))        #Gerak ke bawah pencet s
        self.canvas.bind('<Right>', lambda _: (self.latar.gerak(0, 1), self.update()))        #Gerak ke kanan pencet d
        self.latar2 = [
            self.canvas.create_rectangle(c*size_keping, r*size_keping, (c+1)*size_keping, (r+1)*size_keping)        #r+1 sama c+1 supaya bidang lebih besar 1 dari kotak - kotaknya
                for r in range(self.latar.tinggi_latar) for c in range(self.latar.lebar_latar)
        ]
        self.canvas.pack(side="right")                                       # Biar ketata dikanan
        self.judul = tk.Label(self, anchor = 'center', width = 8, height = 1, font=("System", 42), fg = 'magenta2', bg = 'black')
        self.judul.pack(side="top")
        self.deskripsi = tk.Label(self, anchor = 'center', width = 26, height = 5, font = ("System", 16), fg = 'orange2', bg='black')
        self.deskripsi.pack(side="top")
        self.panel_tetris = tk.Label(self, anchor ='n', width = 26, height = 10, font = ("System", 14), fg = 'medium blue', bg = 'black')
        self.panel_tetris.pack(side="top")
        self.kalo_kalah = tk.Label(self, anchor = 'n', width = 16, height = 7, font = ("System", 18), fg = 'red', bg = 'black')
        self.kalo_kalah.pack(side="top")        #Berupaya mendesain deskripsi agar terlihat bagus ╥﹏╥
        self.update()
#==========================================================================---> -----===End of Template dasar GUI===-----
    def update(self):
        for i, _id in enumerate(self.latar2):
            angka_warna = self.latar.get_warna(i // self.latar.lebar_latar, i % self.latar.lebar_latar)
            self.canvas.itemconfig(_id, fill = COLORS[angka_warna])     #Memperbarui frame tetromino yang jatuh

        self.judul['text'] = "TETRIS"
        self.deskripsi['text'] = "Tekan Panah Keyboard\natau\nW,A,S,D\nUntuk main"
        self.panel_tetris['text'] = "Level : {}\nSkor : {}\nSyarat : {}".format(self.latar.level, self.latar.skor_tetris, self.latar.eksponensi)
        self.kalo_kalah['text'] = "YAH ANDA KALAH!\nTekan W atau Up Key\n untuk Reset!" if self.latar.kalah else ""     #Penggemar \n broo

root=tk.Tk()
GUI=Tampilan(master=root)
GUI.mainloop() 