from flask import Flask, request, jsonify
import io
import os
import base64
import sys
from ocr import ReceiptOCR
from onvertpdf import pdf2img
from pdf2image import convert_from_bytes
import numpy as np
import cv2
from pathlib import Path
from werkzeug.utils import secure_filename

sys.path.append("Lib/site-packages")

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg','pdf'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/api/upload_image", methods=["POST"])
def process_image():
    # Read the image via file.stream
    if 'file' not in request.files:
        resp = jsonify({'error': True, 'message' : 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'error': True, 'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        if file.filename.endswith('.pdf'):
            ocr = pdf2img(file.read(), Path(file.filename).stem)
            resp = jsonify({'error': False, 'msg': 'Data Read Image Success', 'total': ocr.get_structure(), 'result': ocr.get_vendorname()})
            resp.status_code = 201
            if os.path.exists('./pdf/'+ocr.filename):
                os.remove('./pdf/'+ocr.filename)
            return resp
        else:
            file_bytes = np.fromstring(file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_ANYCOLOR)
            _, thresh = cv2.threshold(img,100,255,cv2.THRESH_BINARY) 
            _, im_arr = cv2.imencode('.jpg', thresh)

            im_bytes = im_arr.tobytes()
            im_b64 = base64.b64encode(im_bytes)
            ocr = ReceiptOCR(im_b64)
            resp = jsonify({'error': False, 'msg': 'Data Read Image Success', 'total': ocr.get_structure(), 'result': ocr.get_vendorname(), 'raw': ocr.convert_to_text()})
            resp.status_code = 201
            return resp
            
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)