import os
from PIL import *
from urllib import *
from pytesser import *
import ImageFilter
import requests
from StringIO import StringIO

import Image,ImageEnhance,ImageFilter,ImageDraw


def numpoint(im):
    w,h = im.size
    data = list( im.getdata() )
    mumpoint=0
    for x in range(w):
        for y in range(h):
            if data[ y*w + x ] !=255:
                mumpoint+=1
    return mumpoint
def pointmidu(im):
    w,h = im.size
    p=[]
    for y in range(0,h,5):
        for x in range(0,w,5):
            box = (x,y, x+5,y+5)
            im1=im.crop(box)
            a=numpoint(im1)
            if a<11:
                for i in range(x,x+5):
                    for j in range(y,y+5):
                        im.putpixel((i,j), 255)
    return im


class Captcha:
    def __init__(self, session):
        self.url = 'https://isdna1.yzu.edu.tw/CnStdSel/SelRandomImage.aspx'
        self.path = "web.tif"
        self.session = session
    def download(self):
        #urlretrieve(self.url, self.path)
        #if( os.path.exists(self.path) ):

        c = self.session.get(self.url, verify=False)
        i = Image.open(StringIO(c.content))
        i.save(self.path)
        
        self.img = Image.open(self.path).convert("RGBA")
        self.img = self.img.rotate(1)     
        self.img = self.img.crop( (1,4,self.img.size[0]-1,self.img.size[1]-1) )
        self.img.save('tmp.png')
            
    def save(self):
        self.img = self.img.convert('L')  
        self.img.save(self.path)
        
    def strong(self):
        dx=[-1,-1,-1,0,0,0,1,1,1]
        dy=[-1,0,1,-1,0,1,-1,0,1]
        #dx=[-1,0,0,1]
        #dy=[0,1,-1,0]            
        pix = self.img.load()
        width = self.img.size[0]
        height = self.img.size[1]        
        for y in xrange(1,height,1):
            for x in xrange(1,width,1):  
                num=0
                for i in range(len(dx)):
                    if x>0 and x<width-1 and y>0 and y<height-1:
                        if(pix[(x+dx[i]),(y+dy[i])][0] == 0):
                            num+=1
                if pix[x,y]==(255,255,255) and num >=3:
                    pix[x, y] = (0, 0, 0, 0)
                    
    def clean_noise(self):
        
        pix = self.img.load()
        width = self.img.size[0]
        height = self.img.size[1]   
        for y in xrange(height):
            for x in xrange(width):  
                if pix[x, y][1] != 0 and ( pix[(x+1)%width, y][1] != 0 and pix[x, (y+1)%height][1] != 0) :
                #if pix[x, y][1] != 0:
                    pix[x, y] = (255, 255, 255, 255)
                else:
                    pix[x, y] = (0, 0, 0, 0)
        #self.img = self.img.filter( ImageFilter.EDGE_ENHANCE )
        #self.img = self.img.filter( ImageFilter.CONTOUR )        
            
    def resize(self, width, height):
        self.img = self.img.resize((width, height), Image.NEAREST)

    def isvilid(self):
        if len(self.text)!=4: return False
        if self.text.isupper()==False: return False
        for i in self.text:
            if i.isalnum()==False : return False
        return True
    def ocr(self):
        self.download()
        self.clean_noise()
        self.strong()
        self.resize(180,100)
        self.img = pointmidu(self.img)
        self.save()
        self.text = image_to_string(self.img).strip()
    def ocr_png(self,filename):
        self.img = Image.open(filename).convert("RGBA")
        self.img = self.img.rotate(1)     
        self.img = self.img.crop( (1,4,self.img.size[0]-1,self.img.size[1]-1) )
        self.clean_noise()
        self.strong()
        #self.resize(180,100)
        self.img = pointmidu(self.img)
        self.save()
        self.text = image_to_string(self.img).strip()
        return self.text
    def _next(self):
        self.ocr()
        while ( self.isvilid() == False):
            #print self.text
            self.ocr()
        return self.text
    

