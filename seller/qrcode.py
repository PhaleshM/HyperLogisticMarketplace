from qrcode import *
import os
from django.conf import settings

start = 00000000        # 8 zeroes ~ 1 crore
count = 100

def qr_gen(count):
    global start
    end = start + count
    while(start < end):    
        img = make(start)
        img_name = 'qr ' + start + '.png'
        #img.save(settings.MEDIA_ROOT + '/' + img_name)
        img.save(os.getcwd() + '/' + img_name)
        start += 1

qr_gen(5)