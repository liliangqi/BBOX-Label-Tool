
#-------------------------------------------------------------------------------
# Name:        Object bounding box label tool
# Purpose:     Label object bboxes for ImageNet Detection data
# Created:     06/06/2014
# Rectified:   09/29/2017
#
#-------------------------------------------------------------------------------
from __future__ import division
from tkinter import *
from PIL import Image as pilimg 
from PIL import ImageTk
import os
import glob
import random
from tkinter.filedialog import *

# colors for the bboxes
COLORS = ['red', 'blue', 'orange', 'yellow', 'pink', 'cyan', 'green', 'black']
# image sizes for the examples
SIZE = 256, 256
# 指定缩放后的图像大小
DEST_SIZE = 1200, 900

classLabels = ['1', '2', '3', '4', '5', '6', '7', '8']
hardLabels = ['easy', 'hard', 'very']

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = False, height = False)

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None
        self.currentClass = '1'
        self.currentHard = 'easy'

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.label = Label(self.frame, text = "Image Dir:")
        self.label.grid(row = 0, column = 0, sticky = E)
        self.entry = Listbox(self.frame, width=4, height=1)
        self.entry.grid(row=0, column=1, sticky=W+E)
        self.ldBtn = Button(self.frame, text = "Load", command = self.loadDir)
        self.ldBtn.grid(row = 0, column = 2, sticky = W+E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 1, column = 2,  sticky = W+N)
        self.listbox = Listbox(self.frame, width = 30, height = 12)
        self.listbox.grid(row = 2, column = 2, sticky = N)
        self.btnDel = Button(self.frame, text = 'Delete',
            command = self.delBBox)
        self.btnDel.grid(row = 3, column = 2, sticky = W+E+N)
        self.btnClear = Button(self.frame, text = 'ClearAll',
            command = self.clearBBox)
        self.btnClear.grid(row=4, column=2, sticky=W+E+N)
        
        #select class type
        self.classPanel = Frame(self.frame)
        self.classPanel.grid(row=5, column=0, columnspan=10, sticky=W+E)
        label = Label(self.classPanel, text='person:')
        label.grid(row=5, column=1, sticky = W+N)
       
        self.classbox = Listbox(self.classPanel, width=4, height=2)
        self.classbox.grid(row=5,column=2)
        self.classbox.insert(0, '1')
        self.classbox.itemconfig(0, fg=COLORS[0])
        for each in range(len(classLabels)):
            function = 'select' + classLabels[each]
            print(classLabels[each])
            btnMat = Button(self.classPanel, text=classLabels[each],
                command=getattr(self, function))
            btnMat.grid(row = 5, column = each + 3)
        
        #select hard type
        self.hardPanel = Frame(self.frame)
        self.hardPanel.grid(row=5, column=2, columnspan=4, sticky=W+E)
        hard = Label(self.hardPanel, text='hard:')
        hard.grid(row=5, column=3, sticky = W+N)
       
        self.hard = Listbox(self.hardPanel, width=4, height=2)
        self.hard.grid(row=5,column=4)
        self.hard.insert(0, 'easy')
        self.hard.itemconfig(0, fg=COLORS[1])
        for each in range(len(hardLabels)):
            function = 'choose_' + hardLabels[each]
            print(classLabels[each])
            btnMat = Button(self.hardPanel, text=hardLabels[each],
                command=getattr(self, function))
            btnMat.grid(row = 5, column = each + 5)
        
        
        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 6, column = 1, columnspan = 2, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, 
            command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, 
            command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go',
            command = self.gotoImage)
        self.goBtn.pack(side = LEFT)

        # example pannel for illustration
        self.egPanel = Frame(self.frame, border = 10)
        self.egPanel.grid(row = 1, column = 0, rowspan = 5, sticky = N)
        self.tmpLabel2 = Label(self.egPanel, text = "Examples:")
        self.tmpLabel2.pack(side = TOP, pady = 5)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side = TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(10, weight = 1)

        # for debugging
##        self.setImage()
##        self.loadDir()

    def loadDir(self):
        '''
        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'
        '''
        self.parent.focus()
        #self.category = askdirectory()
##        if not os.path.isdir(s):
##            tkMessageBox.showerror("Error!", message = "The specified dir doesn't exist!")
##            return
        # get image list
        # self.imageDir = os.path.join(r'./Images', '%d' %(self.category))
        self.imageDir = askdirectory()
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        self.entry.insert(0, self.imageDir)
        if len(self.imageList) == 0:
            print('No .jpg images found in the specified dir!')
            return   

        # set up output dir
        self.outDir = self.imageDir
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)
        
        labeledPicList = glob.glob(os.path.join(self.outDir, '*.txt'))
        
        for label in labeledPicList:
            data = open(label, 'r')
            if '0\n' == data.read():
                data.close()
                continue
            data.close()
            picture = label.replace('Labels', 'Images').replace('.txt', '.jpg')
            if picture in self.imageList:
                self.imageList.remove(picture)

        # load example bboxes
        self.egDir = os.path.join(self.outDir, '..')
        filelist = glob.glob(os.path.join(self.egDir, '*.jpg'))
        filelist.extend(glob.glob(os.path.join(self.egDir, '*.png')))
        self.tmp = []
        self.egList = []
        random.shuffle(filelist)
        for (i, f) in enumerate(filelist):
            if i == 3:
                break
            im = pilimg.open(f)
            r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
            new_size = int(r * im.size[0]), int(r * im.size[1])
            self.tmp.append(im.resize(new_size, pilimg.ANTIALIAS))
            self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
            self.egLabels[i].config(image=self.egList[-1], width=SIZE[0], height=SIZE[1])


        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)
        self.loadImage()
        print('%d images loaded from %s' %(self.total, self.imageDir))

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        pil_image = pilimg.open(imagepath)

        # 缩放到指定大小
        resize_image = pil_image.resize((DEST_SIZE[0], DEST_SIZE[1]),
            pilimg.ANTIALIAS)

        self.img = resize_image
        self.imgSize = self.img.size
        self.truesize = pil_image.size
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), 
            height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))

        # 载入图片以后的键盘响应
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("a", self.prevImage) # press 'a' to go backforward
        self.parent.bind("d", self.nextImage) # press 'd' to go forward
        self.parent.bind("1", self.select1)
        self.parent.bind("2", self.select2)
        self.parent.bind("3", self.select3)
        self.parent.bind("4", self.select4)
        self.parent.bind("5", self.select5)
        self.parent.bind("6", self.select6)
        self.parent.bind("7", self.select7)
        self.parent.bind("8", self.select8)
        self.parent.bind("e", self.choose_easy)
        self.parent.bind("h", self.choose_hard)
        self.parent.bind("v", self.choose_very)

        # 每次load进新的图片时初始化person和hard
        self.currentClass = '1'
        self.currentHard = 'easy'
        self.classbox.delete(0,END)
        self.classbox.insert(0, '1')
        self.classbox.itemconfig(0, fg=COLORS[0])
        self.hard.delete(0,END)
        self.hard.insert(0, 'easy')
        self.hard.itemconfig(0, fg=COLORS[1])

        # load labels
        self.clearBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0

        # 再次标记某张图片时从对应的txt文件里读入已有的bbox
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue
                    # 添加两种bbox，tbbox用于添加入txt文件，tmp用于画框
                    tbbox = [t.strip() for t in line.split()]
                    tmp = tbbox[:] # 取一个切片防止tbbox被更改

                    rate0 = DEST_SIZE[0]/self.truesize[0]
                    rate1 = DEST_SIZE[1]/self.truesize[1]
                    tmp[-4] = int(int(tmp[-4]) * rate0)
                    tmp[-3] = int(int(tmp[-3]) * rate1)
                    tmp[-2] = int(int(tmp[-2]) * rate0)
                    tmp[-1] = int(int(tmp[-1]) * rate1)

                    self.bboxList.append(tuple(tmp))
                    tmpId = self.mainPanel.create_rectangle(
                        tmp[-4], tmp[-3], tmp[-2], tmp[-1], width = 2,
                        outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])

                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, 'p%s %s (%s, %s) -> (%s, %s)' % \
                        (tbbox[0], tbbox[1], tbbox[-4], tbbox[-3], tbbox[-2],
                            tbbox[-1]))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1,
                        fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

    def saveImage(self):
        with open(self.labelfilename, 'w') as f:
            f.write('%d\n' %len(self.bboxList))
            for bbox in self.bboxList:
                tx0 = int(bbox[-4] * self.truesize[0]/DEST_SIZE[0])
                ty0 = int(bbox[-3] * self.truesize[1]/DEST_SIZE[1])
                tx1 = int(bbox[-2] * self.truesize[0]/DEST_SIZE[0])
                ty1 = int(bbox[-1] * self.truesize[1]/DEST_SIZE[1])
                tbbox = [bbox[0], bbox[1], tx0, ty0, tx1, ty1]
                f.write(' '.join(map(str, tbbox)) + '\n')
        print('Image No. %d saved' %(self.cur))


    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
            #self.STATE['x'], self.STATE['y'] = self.imgSize[0], self.imgSize[1]
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'],
                event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'],
                event.y)
            if x2 > self.imgSize[0]:
                x2 = self.imgSize[0]
            if y2 > self.imgSize[1]:
                y2 = self.imgSize[1]    

            tx0 = int(x1 * self.truesize[0]/DEST_SIZE[0])
            ty0 = int(y1 * self.truesize[1]/DEST_SIZE[1])
            tx1 = int(x2 * self.truesize[0]/DEST_SIZE[0])
            ty1 = int(y2 * self.truesize[1]/DEST_SIZE[1])

            self.bboxList.append((self.currentClass, self.currentHard, 
                x1, y1, x2, y2))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, 'p%s %s (%d, %d) -> (%d, %d)' %\
                (self.currentClass, self.currentHard, tx0, ty0, tx1, ty1))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, 
                fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

            # 每画一个框personID自动加1
            if self.currentClass == '8':
                self.currentClass = '2'
            else:
                self.currentClass = str(int(self.currentClass) + 1)
            self.classbox.delete(0,END)
            self.classbox.insert(0, self.currentClass)
            self.classbox.itemconfig(0, fg=COLORS[0])

        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y,
                self.tkimg.width(), event.y, width = 2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x,
                self.tkimg.height(), width = 2)
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'],
                self.STATE['y'], event.x, event.y, width = 2, 
                outline = COLORS[len(self.bboxList) % len(COLORS)])

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        
    def select1(self, event=None):
        self.currentClass = '1'
        self.classbox.delete(0,END)
        self.classbox.insert(0, '1')
        self.classbox.itemconfig(0,fg = COLORS[0])
    
    def select2(self, event=None):
        self.currentClass = '2'    
        self.classbox.delete(0,END)    
        self.classbox.insert(0, '2')
        self.classbox.itemconfig(0,fg = COLORS[0])
    
    def select3(self, event=None):
        self.currentClass = '3'    
        self.classbox.delete(0,END)    
        self.classbox.insert(0, '3')
        self.classbox.itemconfig(0,fg = COLORS[0])
        
    def select4(self, event=None):
        self.currentClass = '4'    
        self.classbox.delete(0,END)    
        self.classbox.insert(0, '4')
        self.classbox.itemconfig(0,fg = COLORS[0])
        
    def select5(self, event=None):
        self.currentClass = '5'
        self.classbox.delete(0,END)
        self.classbox.insert(0, '5')
        self.classbox.itemconfig(0,fg = COLORS[0])
        
    def select6(self, event=None):
        self.currentClass = '6'
        self.classbox.delete(0,END)    
        self.classbox.insert(0, '6')
        self.classbox.itemconfig(0,fg = COLORS[0])
        
    def select7(self, event=None):
        self.currentClass = '7'    
        self.classbox.delete(0,END)    
        self.classbox.insert(0, '7')
        self.classbox.itemconfig(0,fg = COLORS[0])
        
    def select8(self, event=None):
        self.currentClass = '8'    
        self.classbox.delete(0,END)    
        self.classbox.insert(0, '8')
        self.classbox.itemconfig(0,fg = COLORS[0])

    def choose_easy(self, event=None):
        self.currentHard = 'easy'
        self.hard.delete(0,END)
        self.hard.insert(0, 'easy')
        self.hard.itemconfig(0,fg = COLORS[1])

    def choose_hard(self, event=None):
        self.currentHard = 'hard'
        self.hard.delete(0,END)
        self.hard.insert(0, 'hard')
        self.hard.itemconfig(0,fg = COLORS[1])

    def choose_very(self, event=None):
        self.currentHard = 'very'
        self.hard.delete(0,END)
        self.hard.insert(0, 'very')
        self.hard.itemconfig(0,fg = COLORS[1])

    def prevImage(self, event=None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event=None):
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()

##    def setImage(self, imagepath = r'test2.png'):
##        self.img = Image.open(imagepath)
##        self.tkimg = ImageTk.PhotoImage(self.img)
##        self.mainPanel.config(width = self.tkimg.width())
##        self.mainPanel.config(height = self.tkimg.height())
##        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.mainloop()