# -*- coding: UTF-8 -*-
#from functools import total_ordering
#from pickle import TRUE
#from xml.sax.handler import feature_namespace_prefixes
#gui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#系统
import sys
import os
#初始化图片
import base64
#3个图片，可以去更改
from ysbys_png import img as png1
from reysbys_png import img as png2
from maskysbys_png import img as png3
#seam
import cv2
from numpy import imag
import json
import numpy as np
#seam的函数
from seam_carving import *
#服务器函数
from putall import *
from getall import *
#创建文件夹
def mkdir(path):
    path=path.strip()
    path=path.rstrip("\\")
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path) 
mkdir(os.getcwd()+"\\photo\\")
mkdir(os.getcwd()+"\\temp\\")
mkdir(os.getcwd()+"\\putmask\\")
mkdir(os.getcwd()+"\\getmask\\")
#删掉程序垃圾
def delinit(path):
    file=os.listdir(path)
    for i in file:
        os.remove(path+"/"+i)
delinit(os.getcwd()+"/temp")
#初始图片
def savep(png,name):
    bs4 = base64.b64decode(png)
    tmp = open(name, 'wb+')
    tmp.write(bs4)
    tmp.close()
savep(png1,"ysbys.png")
savep(png2,"reysbys.png")
savep(png3,"maskysbys.png") 
#json转mask
def jstoph(jspath,imgpath,maskpath):
    list = []
    with open(jspath, 'r') as f:
        data = json.load(f)
        for i in data.keys():
            if i == 'shapes':
                list = data[i]
                break
    tmp = {}
    with open(jspath, "r") as f:
        tmp = f.read()
    tmp = json.loads(tmp)
    img = cv2.imread(imgpath)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)#BGR->RGB
    mask = np.zeros_like(img)
    #好好研究json文件
    for i in range(len(list)):
        points = tmp["shapes"][i]["points"]
        #print(points)
        points = np.array(points, np.int32)
        for j in list[i].keys():
            if j == 'label':
                if list[i][j] == 'remove':
                    cv2.fillPoly(mask, [points], (255, 255, 255))
                    break
                if list[i][j] == 'left':
                    cv2.fillPoly(mask, [points], (128, 128, 128))
                    break
    cv2.imwrite(maskpath, mask)

#主窗口位置尺寸
wx=150;wy=150;ww=1000;wh=700
showimgsize=QSize(290,290)
class myui(QWidget):
    def __init__(self):
        super().__init__()
        self.imgpath=os.getcwd()+"/ysbys.png"
        self.maskpath=os.getcwd()+"/maskysbys.png"
        self.repath=os.getcwd()+"/reysbys.png"
        self.dicsousepath=[self.imgpath,self.maskpath,self.repath]
        self.dicshowpath=self.dicsousepath[0:3]
        self.dicloadimg=[self.imgpath,self.maskpath]
        self.imgid=[0,0]
        self.dic={"resize":0,"remove":0,"im":"","out":"","mask":"","rmask":"","dy":0,"dx":0,"vis":0,"hremove":0,"backward_energy":0}
        #{"resize":0,"remove":1,"im":"Path to image","out":"Output file name","mask":"Path to (protective) mask","rmask":"Path to removal mask","dy":0,"dx":0,"vis":"Visualize the seam removal process","hremove":"Remove horizontal seams for object removal","backward_energy":"Use backward energy map (default is forward)"}
        self.InitUI()

    def InitUI(self):
        
        #self.menu=QMenuBar(self)
        #self.tool=QToolBar(self)
        #self.statu=QStatusBar(self)


        #模式选择
        self.modbtn1=QPushButton(self,text="本地处理")
        self.modbtn2=QPushButton(self,text="服务器协助生成掩码")
        self.modbtn1.setStyleSheet("QPushButton{background-color:rgb(0,255,255)}")

        self.modbtn1.clicked.connect(self.changeshowbox)
        self.modbtn2.clicked.connect(self.changeshowbox)
        
        modbox=QHBoxLayout()
        modbox.addWidget(self.modbtn1)
        modbox.addWidget(self.modbtn2)
        modbox.addStretch(1)
        #模块封装完成

        #MOD1常规模式
        self.showwin1=QWidget()
        #显示原图
        self.btnshow1=QPushButton(self)
        self.btnshow1.setText("显示原图")
        #self.btnshow1.set
        self.btnshow1.resize(140,10)
        self.btnshow2=QPushButton(self)
        self.btnshow2.setText("显示掩码")
        self.btnshow3=QPushButton(self)
        self.btnshow3.setText("结果")

        self.btnshow1.clicked.connect(self.btnshowimg)
        self.btnshow2.clicked.connect(self.btnshowimg)
        self.btnshow3.clicked.connect(self.btnshowimg)
        
       #self.btnshowg.
        #更改图片路径
        self.btncgshow1=QPushButton(self)
        self.btncgshow1.setText("导入图片")
        self.btncgshow2=QPushButton(self)
        self.btncgshow2.setText("切换掩码")
        self.btncgshow3=QPushButton(self)
        self.btncgshow3.setText("切换结果")
        self.btncgshow1.clicked.connect(self.btncgimg)
        self.btncgshow2.clicked.connect(self.btncgimg)
        self.btncgshow3.clicked.connect(self.btncgimg)
        
        #第一排容器。
        showbox1=QVBoxLayout()
        #控件
        boxbtn1=QHBoxLayout()
        boxbtn1.addWidget(self.btncgshow1)
        boxbtn1.addWidget(self.btnshow1)
        
        boxbtn1.addSpacing(10)
        boxbtn1.addWidget(self.btncgshow2)
        boxbtn1.addWidget(self.btnshow2)
    
        boxbtn1.addSpacing(10)
        boxbtn1.addWidget(self.btnshow3)
        boxbtn1.addWidget(self.btncgshow3)
        boximg1=QHBoxLayout()
        self.boximg1=QLabel(self)
        self.boximg1.setPixmap(QPixmap(self.imgpath).scaled(showimgsize))
        self.boximg2=QLabel(self)
        self.boximg2.setPixmap(QPixmap(self.maskpath).scaled(showimgsize))
        self.boximg3=QLabel(self)
        self.boximg3.setPixmap(QPixmap(self.repath).scaled(showimgsize))
        self.dicimglab=[self.boximg1,self.boximg2,self.boximg3]
        boximg1.addWidget(self.boximg1)
        boximg1.addSpacing(10)
        boximg1.addWidget(self.boximg2)
        boximg1.addSpacing(10)
        boximg1.addWidget(self.boximg3)
        #封装
        #掩码制作
        boxbtn4=QHBoxLayout()
        self.btnpaint=QPushButton("人工标定目标",self)
        self.btnmask=QPushButton("生成三值掩码图",self)
        self.btnpaint.clicked.connect(self.getjson)
        self.btnmask.clicked.connect(self.makemask)
        boxbtn4.addSpacing(320)
        boxbtn4.addWidget(self.btnpaint)
        boxbtn4.addWidget(self.btnmask)
        boxbtn4.addSpacing(320)
        
        showbox1.addLayout(boximg1)
        showbox1.addSpacing(10)
        showbox1.addLayout(boxbtn1)
        showbox1.addLayout(boxbtn4)
        showbox1.addStretch(1)
        #第二排容器
        showbox2=QHBoxLayout()
        #控件
        #功能键容器
        mod1btnbox=QVBoxLayout()
        
        #功能选择
        boxbtn5=QVBoxLayout()
        self.labcs=QLabel("细缝雕刻参数选择:")
        self.picsize=QLabel("图片目标尺寸(宽x高)")
        self.picx=QLineEdit(self)
        self.picy=QLineEdit(self)
        x,y=cv2.imread(self.dicsousepath[0]).shape[0:2]
        self.picx.setText(str(x))
        self.picy.setText(str(y))
        self.btnvis=QCheckBox("可视化显示裁切过程",self)
        self.btnvis.setChecked(True)
        self.btnsmmod=QCheckBox("是否移除目标",self)
        self.btnsmmod.setChecked(True)
        self.btnbackeg=QCheckBox("启用后向能量(默认使用前向能量)",self)
        boxbtn51=QHBoxLayout()
        boxbtn52=QHBoxLayout()
        boxbtn51.addWidget(self.picsize)
        boxbtn51.addWidget(self.picx)
        boxbtn51.addWidget(self.picy)
        boxbtn52.addWidget(self.btnvis)
        boxbtn52.addWidget(self.btnsmmod)
        boxbtn52.addWidget(self.btnbackeg)
        boxbtn5.addWidget(self.labcs)
        boxbtn5.addLayout(boxbtn51)
        boxbtn5.addLayout(boxbtn52)
        #seam模式选择,默认移除
        boxbtn6=QHBoxLayout()
        boxlabbtn=QVBoxLayout()
        self.labmod=QLabel("细缝雕刻方向:")
        self.seammodx=QRadioButton("竖直裁切(建议目标比较窄的时候使用)",self)
        self.seammody=QRadioButton("水平裁切(建议目标比较矮的时候使用)",self)
        self.seammodx.setChecked(True)
        self.btnwork=QPushButton("开始转换",self)
        self.btnwork.clicked.connect(self.ysbys)
        
        self.seammodg=QButtonGroup(self)
        self.seammodg.addButton(self.seammody,1)
        self.seammodg.addButton(self.seammodx,2)
    
        boxlabbtn.addWidget(self.labmod)
        boxlabbtn.addWidget(self.seammodx)
        boxlabbtn.addWidget(self.seammody)
        boxbtn6.addSpacing(50)
        boxbtn6.addLayout(boxlabbtn)
        boxbtn6.addWidget(self.btnwork)
        boxbtn6.addSpacing(50)
        #封装功能键
        #mod1btnbox.addLayout(boxbtn4)
        mod1btnbox.addLayout(boxbtn5)
        mod1btnbox.addLayout(boxbtn6)
        
        
        #mod1btnbox.addStretch(1)
        #封装功能页面
        
        
        modbtnbox=QFrame(self)
        modbtnbox.setFrameShape(QFrame.Panel)
        
        modbtnbox.setLayout(mod1btnbox)
        #modbtnbox.show()
        #modbtnbox.setStyleSheet("border-style: dotted")
        showbox2.addWidget(modbtnbox)
        #showbox2.addSpacing(100)
        #showbox2.addStretch(1)

        #MOD1页面封装
        
        self.showbox=QVBoxLayout()
        self.showbox.addLayout(showbox1)   
        self.showbox.addSpacing(30) 
        self.showbox.addLayout(showbox2)  
        self.showbox.addStretch(1)
        self.showwin1.setLayout(self.showbox)
        self.showwin1.show()

        #MOD2联网模式
        self.showwin2=QWidget()
        showbox3=QHBoxLayout()
        #上传box
        btnimgbox1=QVBoxLayout()

        box1btnbox=QHBoxLayout()
        imguppathbtn= QPushButton("选择图片")
        imguppathbtn.clicked.connect(self.openfile)
        uploadbtn = QPushButton("上传")
        uploadbtn.clicked.connect(self.uploadimg)
        box1btnbox.addWidget(imguppathbtn)
        box1btnbox.addWidget(uploadbtn)
        #封装
        btnimgbox1.addLayout(box1btnbox)
        ######图片展示
        self.lab1vbox=QVBoxLayout()
        self.plab1=QLabel()
        self.plab1.setPixmap(QPixmap(self.dicshowpath[0]).scaled(1.5*showimgsize))
        self.lab1vbox.addWidget(self.plab1)
        btnimgbox1.addSpacing(30)
        btnimgbox1.addLayout(self.lab1vbox)
        
        ###############
        
        #下载box
        btnimgbox2=QVBoxLayout()

        box2btnbox=QHBoxLayout()
        fwqbtn= QPushButton("服务器操作")
        fwqbtn.clicked.connect(self.putty)
        downloadbtn = QPushButton("下载")
        downloadbtn.clicked.connect(self.downloadimg)
        box2btnbox.addWidget(fwqbtn)
        box2btnbox.addWidget(downloadbtn)
        #封装
        btnimgbox2.addLayout(box2btnbox)
        ######图片展示
        self.lab2vbox=QVBoxLayout()
        self.plab2=QLabel()
        self.plab2.setPixmap(QPixmap(self.dicshowpath[1]).scaled(1.5*showimgsize))
        self.lab2vbox.addWidget(self.plab2)
        btnimgbox2.addSpacing(20)
        btnimgbox2.addLayout(self.lab2vbox)
        ###############
        
        #封装窗口2
        #showbox3.addSpacing(50) 
        showbox3.addLayout(btnimgbox1)
        showbox3.addSpacing(50)
        showbox3.addLayout(btnimgbox2)
        showbox3.addStretch(1)
        #窗
        self.showwin2.setLayout(showbox3)
        self.showwin2.hide()
       
        
        #准备在这里实现窗口转换
        #顶层布局
        mainbox=QVBoxLayout()
        mainbox.addLayout(modbox)
        mainbox.addSpacing(10)
        mainbox.addWidget(self.showwin1)
        mainbox.addWidget(self.showwin2)
        mainbox.addStretch(1)
        self.setLayout(mainbox)
        self.setGeometry(wx,wy,ww,wh)
        self.setWindowTitle("细缝雕刻大师")
        self.show()

    def changeshowbox(self,pressed):
        id=self.sender().text()
        if id=="本地处理":
            self.modbtn1.setStyleSheet("QPushButton{background-color:rgb(0,255,255)}")
            self.modbtn2.setStyleSheet("QPushButton{background-color:rgb(255,255,255)}")
            self.showwin2.hide()
            self.showwin1.show()
        if id=="服务器协助生成掩码":
            self.modbtn1.setStyleSheet("QPushButton{background-color:rgb(255,255,255)}")
            self.modbtn2.setStyleSheet("QPushButton{background-color:rgb(0,255,255)}")
            self.showwin1.hide()
            self.showwin2.show()
    
    def btnshowimg(self):
        id=0 if self.sender().text()=="显示原图" else 1 if self.sender().text()=="显示掩码" else 2
        os.startfile(self.dicsousepath[id])

    def btncgimg(self):
        id=0 if self.sender().text()=="导入图片" else 1 if self.sender().text()=="切换掩码" else 2
        fname=QFileDialog.getOpenFileName(self,"图片选择","./")
        if fname[0]:
            self.dicsousepath[id]=fname[0]
            self.dicimglab[id].setPixmap(QPixmap(self.dicsousepath[id]).scaled(showimgsize))
        if id==0:
            x,y=cv2.imread(self.dicsousepath[id]).shape[0:2]
            self.picx.setText(str(x))
            self.picy.setText(str(y))
    
    def getjson(self):
        os.system('labelme')

    def makemask(self):
        fname=QFileDialog.getOpenFileName(self,"图片选择","./")
        if fname[0]:
            jspath=fname[0]
            if jspath[-6:-5]==self.dicsousepath[0][-5:-4]:
                maskpath=jspath[0:-5]+"mask.png"
                jstoph(jspath,self.dicsousepath[0],maskpath)
                os.remove(jspath)
                self.dicsousepath[1]=maskpath
                self.dicimglab[1].setPixmap(QPixmap(self.dicsousepath[1]).scaled(showimgsize))
                QMessageBox.information(self,"成功","生成成功")
            else:
                QMessageBox.information(self,"错误","所选文件于原图不匹配")
                #QMessageBox.warning(self,"Warning","恢复出厂设置将导致用户数据丢失，是否继续操作？",QMessageBox.Reset|QMessageBox.Help|QMessageBox.Cancel,QMessageBox.Reset)


    def openfile(self):
        QMessageBox.information(self,"提示","请将图片复制到软件文件夹下putmask文件夹中")
        fname=QFileDialog.getOpenFileNames(self,"文件选择","./")
        file=os.listdir(os.getcwd()+"/putmask")
        id=0
        for i in file:
            if i[-4:-1]=="png" or i[-4:-1]=="jpg":
                id=i
        self.dicloadimg[0]=os.getcwd()+"/putmask/"+file[id]
        self.plab1.setPixmap(QPixmap(self.dicloadimg[0]).scaled(1.5*showimgsize))
        
        #上传文件，下载文件有一个
        
    
    def putty(self):
        os.system('putty')
        

    def uploadimg(self):
        
        if putmask():
            QMessageBox.information(self,"成功","图片已经上传成功")
        else:
            QMessageBox.information(self,"失败","图片上传失败")
    
    def downloadimg(self):
        getmask()
        QMessageBox.information(self,"成功","掩码已下载于软件文件夹下getmask文件夹中")
        file=os.listdir(os.getcwd()+"/getmask")
        id=0
        for i in file:
            if i[-4:-1]=="png" or i[-4:-1]=="jpg":
                id=i
        if file[0]:
            self.dicloadimg[1]=os.getcwd()+"/getmask/"+file[0]
            self.plab2.setPixmap(QPixmap(self.dicloadimg[1]).scaled(1.5*showimgsize))

    def ysbys(self):
        id=self.seammodg.checkedId()
        if id==1:
            self.dic["hremove"]=1  
        else :
            self.dic["hremove"]=0
        if self.btnsmmod.isChecked()==0:
            self.dic["resize"]=1
            self.dic["remove"]=0
            self.dic["out"]=self.dicsousepath[0][0:-4]+"resize.jpg"
        if self.btnsmmod.isChecked()==1:
            self.dic["resize"]=0
            self.dic["remove"]=1
            self.dic["out"]=self.dicsousepath[0][0:-4]+"remove.jpg"
        x,y=cv2.imread(self.dicsousepath[0]).shape[0:2]
        self.dic["dx"]=int(eval(self.picx.text()))-x
        self.dic["dy"]=int(eval(self.picy.text()))-y
        self.dic["vis"]=self.btnvis.isChecked()
        self.dic["backward_energy"]=self.btnbackeg.isChecked()
        self.dic["im"]=self.dicsousepath[0]
        self.dic["mask"]=self.dicsousepath[1]
        self.dic["rmask"]=self.dicsousepath[1]
        self.dicsousepath[2]=self.dic["out"]
        
        ysbys(self.dic)
        self.dicsousepath[2]=self.dic["out"]
        self.dicimglab[2].setPixmap(QPixmap(self.dicsousepath[2]).scaled(showimgsize))
        QMessageBox.information(self,"成功","操作成功")
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = myui()
    sys.exit(app.exec_())