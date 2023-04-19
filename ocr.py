import sys
sys.path.append("Lib/site-packages")

import pytesseract
from pytesseract import image_to_string
from PIL import Image
import io
import base64
import re
from openaires import OpenAiRes
import json
class ReceiptOCR():
    
    def __init__(self, image_64):
        self.image_64 = image_64
        
        try:
            self.image = Image.open(io.BytesIO(base64.b64decode(image_64)))
        except TypeError:
            raise Exception("Could not decode base64 data")

    def convert_to_text(self):
        # pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
        return image_to_string(self.image, config='--psm 6')

    def get_structure(self):
        text = self.convert_to_text()
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
        text = self.convert_to_text()
        arr_text = text.split('\n')
        list = '[Vendor Name, Billing Address, Transaction Date, Payment Method, Invoice No, Item, Qty, Harga satuan, Total, Discount, Tax, Total]'
        res = OpenAiRes(arr_text, list)
        return json.loads(res.get_datares())

    def grocery_item(self, txt):
        sentinels = ['total', 'subtotal', 'sub total', 'grand total', 'sub-total','total belanja' ]
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



def test():
    f = open('bill.jpg', 'rb')
    j = base64.encode(f.read())
    f.close()
    f = open('bill_base64.txt', 'w')
    f.write(j)
    f.close()
    ocr = ReceiptOCR(j)
    print(ocr.convert_to_text())
    
if __name__=="__main__":
    test()
