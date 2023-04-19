
from pdf2image import convert_from_bytes
import numpy as np
import cv2
import time
import base64
from PIL import Image
import io
import pytesseract
from pytesseract import image_to_string
import re
from openaires import OpenAiRes
import json

class pdf2img():
    def __init__(self, image_64, filename):
        self.image_64 = image_64
        self.filename = filename
        try:
            # self.image = convert_from_bytes(image_64, 500, poppler_path=r'C:\poppler-0.68.0\bin')
            self.image = convert_from_bytes(image_64)
            self.filename = filename+'-'+time.strftime("%Y%m%d%H%M%S")+'.jpg'
            for img in self.image:
                img.save('./pdf/'+self.filename, 'JPEG')
        except TypeError:
            raise Exception("Could not decode base64 data")
    

    def convert_to_cv2(self):
        with open('./pdf/'+self.filename, 'rb') as f:
            text = f.read()
        file_bytes = np.fromstring(text, np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_ANYCOLOR)
        _, thresh = cv2.threshold(img,100,255,cv2.THRESH_BINARY) 
        _, im_arr = cv2.imencode('.jpg', thresh)
        im_bytes = im_arr.tobytes()
        im_b64 = base64.b64encode(im_bytes)
        image = Image.open(io.BytesIO(base64.b64decode(im_b64)))
        # pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
        return image_to_string(image, config='--psm 6')

    def filename(self):
        return self.filename
        
    def get_structure(self):
        text = self.convert_to_cv2()
        arr_text = text.split('\n')
        regex = '\d+'
        ret = []
        emp_str=[]
        list3=['total belanja', 'total']
        for txt in arr_text:
            if self.grocery_item(txt):
                ret.append(txt)

            elif self.bank_item(txt):
                ret.append(txt)
        
        if len(ret) > 1:
            for txt2 in list3:
                for pharse2 in ret:
                    if txt2.lower() in pharse2.lower():
                        if not len(re.findall(txt2, pharse2)):
                            emp_str =  re.findall(regex, pharse2)
                            if len(emp_str[-1]) > 2:
                                emp_str=''.join([str(elem) for elem in emp_str])
                            else:
                                emp_str='.'.join([''.join(emp_str[:-1])]+emp_str[-1:])

        else:
            for pharse in ret:
                emp_str =  re.findall(regex, pharse)
                if len(emp_str[-1]) > 2:
                    emp_str=''.join([str(elem) for elem in emp_str])
                else:
                    emp_str='.'.join([''.join(emp_str[:-1])]+emp_str[-1:])
        return emp_str

    def get_vendorname(self):
        text = self.convert_to_cv2()
        arr_text = text.split('\n')
        list = '[Vendor Name, Billing Address, Transaction Date, Payment Method, Invoice No, Item, Qty, Harga satuan, Total, Discount, Tax, Total]'
        res = OpenAiRes(arr_text, list)
        return json.loads(res.get_datares())

    def grocery_item(self, txt):
        sentinels = ['total', 'subtotal', 'sub total', 'grand total', 'sub-total','total belanja', 'balance due' ]
        txt = txt.lower()
        for sentinel in sentinels:
            if sentinel in txt:
                return True
        return False

    def bank_item(self, txt):
        sentinels = ['jumlah']
        txt = txt.lower()
        for sentinel in sentinels:
            if sentinel in txt:
                return True
        return False  