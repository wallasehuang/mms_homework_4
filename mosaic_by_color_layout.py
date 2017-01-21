from PIL import Image
from matplotlib.pyplot import imshow
from glob import glob
from os.path import splitext
import numpy as np
import math
import os
import csv
from scipy import fftpack

# color layout
def colorlayout(im_1):
    #Image partitioning
    #We divided the picture into M*N 64 block and the float is ignored
    width,height=im_1.size
    im = im_1.crop((0,0,(width/8)*8,(height/8)*8))
    pixel=im.load()
    width,height = im.size
    #some parameter
    bw=width/8
    bh=height/8
    DCT_x=[]
    Y=[]
    Cr=[]
    Cb=[]
    #Representative color
    for w in xrange(0,width,bw):
        for h in xrange(0,height,bh):
            #the block number(w,h) width has width/8 and the height has height/8
            avgycrcb=[0,0,0] #the avg color of the block
            for i in range(bw):
                for j in range(bh):
                    #read the Y,Cr,Cb from pixel(w+i,h+j)
                    y,k,r=pixel[w+i,h+j]
                    avgycrcb=[aa+bb for aa, bb in zip(avgycrcb,[y,k,r])]
            avgycrcb=[aa/bb for aa, bb in zip(avgycrcb,[bw*bh,bw*bh,bw*bh])]
            DCT_x.extend([avgycrcb])
            Y.extend([avgycrcb[0]])
            Cr.extend([avgycrcb[2]])
            Cb.extend([avgycrcb[1]])

            #set the color
            for i in range(bw):
                for j in range(bh):
                    #set the avgrgb to pixel(w+i,h+j)
                    pixel[w+i,h+j]=(avgycrcb[0],avgycrcb[1],avgycrcb[2])

    #find the parameter of DCT
    BpqY=[]
    BpqCr=[]
    BpqCb=[]
    M=8
    N=8
    for p in xrange(M):
        for q in xrange(N):
            aphp=math.sqrt(2/8.0)
            aphq=math.sqrt(2/8.0)
            if(p==0):
                aphp=1/(math.sqrt(M))
            if(q==0):
                aphq=1/(math.sqrt(N))
            result_Y=0.0
            result_Cr=0.0
            result_Cb=0.0
            for m in xrange(8):
                for n in xrange(8):
                    AmnY=Y[m*8+n]
                    AmnCr=Cr[m*8+n]
                    AmnCb=Cb[m*8+n]
                    result_Y+=AmnY*math.cos((math.pi*(2*m+1)*p)/(2*M))*math.cos((math.pi*(2*n+1)*q)/(2*N))
                    result_Cr+=AmnCr*math.cos((math.pi*(2*m+1)*p)/(2*M))*math.cos((math.pi*(2*n+1)*q)/(2*N))
                    result_Cb+=AmnCb*math.cos((math.pi*(2*m+1)*p)/(2*M))*math.cos((math.pi*(2*n+1)*q)/(2*N))
            result_Y=aphp*aphq*result_Y
            result_Cr=aphp*aphq*result_Cr
            result_Cb=aphp*aphq*result_Cb
            BpqY.insert(p*8+q,result_Y)
            BpqCr.insert(p*8+q,result_Cr)
            BpqCb.insert(p*8+q,result_Cb)
    #Bpq is the parameter of the DCT
    #the parameter of the zigzag scan
    right=True
    sly_right=False
    sly_left=True
    down=False
    zzY=[]
    zzCr=[]
    zzCb=[]
    now=0
    times=1
    loc=0
    #zigzag scanned
    zzY.insert(loc,BpqY[now])#1
    zzCr.insert(loc,BpqCr[now])
    zzCb.insert(loc,BpqCb[now])
    revese=True
    while(now !=63):
        if(revese):
            now+=1
            loc+=1
        else:
            now+=8
            loc+=1
        zzY.insert(loc,BpqY[now])#2,4,6,8,24,40,56
        zzCr.insert(loc,BpqCr[now])
        zzCb.insert(loc,BpqCb[now])
        for i in xrange(times):
            now+=7
            loc+=1
            zzY.insert(loc,BpqY[now])#9,11,18,25,13,20,27,34,41,15,22,29,36,43,50,57,31,38,45,52,59,47,54,61,63
            zzCr.insert(loc,BpqCr[now])
            zzCb.insert(loc,BpqCb[now])
        if(times<7 and revese):
            times+=1#times=2,4,6
            now+=8
            loc+=1
        else:
            revese=False
            now+=1
            loc+=1
            times-=1 #times=6,4,2,0
        zzY.insert(loc,BpqY[now])#17,33,49,58,60,62
        zzCr.insert(loc,BpqCr[now])
        zzCb.insert(loc,BpqCb[now])
        if(times !=0):
            for i in xrange(times):
                now-=7
                loc+=1
                zzY.insert(loc,BpqY[now])#10,3,26,19,12,5,42,35,28,21,14,7,51,44,37,30,23,16,53,46,39,32,55,48
                zzCr.insert(loc,BpqCr[now])
                zzCb.insert(loc,BpqCb[now])
        if(times<7 and revese):
            times+=1#times=3,5,7
        else:
            times-=1#times=5,3,1
    return (zzY,zzCb,zzCr)

#color layout csv
def color_layout_csv(DATASET):
	color_layout_data = list()
	for filename in os.listdir(DATASET):

	    img = Image.open(DATASET+'/'+filename).convert('YCbCr')

	    [Y_n,Cb_n,Cr_n] = colorlayout(img)

	    img_row =[filename,','.join(repr(i) for i in Y_n),','.join(repr(i) for i in 	Cb_n),','.join(repr(i) for i in Cr_n)]
	    color_layout_data.append(img_row)
	f = open("color_layout.csv","w")
	w = csv.writer(f)
	w.writerows(color_layout_data)
	f.close()
	print 'color layout csv finish'

# match
def match(img):
    img = img.convert('YCbCr')
    [Y_1,Cb_1,Cr_1] = colorlayout(img)

    wyi=1.0
    wcri=0.5
    wcbi=0.5

    f = open('color_layout.csv','r')
    match = list()

    for row in csv.reader(f):

        Y_n = [float(y) for y in row[1].split(',')]
        Cb_n = [float(cb) for cb in row[2].split(',')]
        Cr_n = [float(cr) for cr in row[3].split(',')]

        dis,dis_y,dis_cb,dis_cr = 0.0,0.0,0.0,0.0

        for j in xrange(64):
            dis_y+=((Y_1[j]-Y_n[j])**2)*wyi
            dis_cb+=((Cb_1[j]-Cb_n[j])**2)*wcri
            dis_cr+=((Cr_1[j]-Cr_n[j])**2)*wcbi
        dis=math.sqrt(dis_y)+math.sqrt(dis_cb)+math.sqrt(dis_cr)

        match_row = (row[0],dis)
        match.append(match_row)
    f.close()


    match = sorted(match,key=lambda match:match[1])
    return match[0][0]

# mosaic
def mosaic(img_name,n):
    img = Image.open(img_name)
    width,height=img.size
    bw = width/n
    bh = height/n

    for w in xrange(0,width,bw):
        for h in xrange(0,height,bh):
            box =(w,h,w+bw,h+bh)
            b_img = img.crop(box)
            m_img = match(b_img)
            m_img = Image.open('dataset/'+m_img)
            m_img = m_img.resize((bw,bh))
            img.paste(m_img,box)
    img.save('mosaic.jpg')
    return True
