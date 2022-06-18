import hashlib
import base64
import sys
import os
import io
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random
from config import *

def getKey():
    keyHash = SHA256.new()
    keyHash.update(KEY.encode("utf8"))
    cryptoKey = keyHash.hexdigest()[:16]
    return cryptoKey.encode("utf8")

def pad(byte_array):
        pad_len = 16 - len(byte_array) % 16
        return byte_array + (bytes([pad_len]) * pad_len)
    
def unpad(byte_array):
    return byte_array[:-ord(byte_array[-1:])]

def encryptImage(data):
    cipher = AES.new(getKey(), AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(pad(data)))

def decryptImage(data):
    cipher = AES.new(getKey(), AES.MODE_ECB)
    return unpad(cipher.decrypt(data))

def hashImage(base64_img):
    hash = SHA256.new()
    hash.update(base64_img.encode('utf-8'))
    return hash.hexdigest()

def writeImage(content, filename, decode=True):
    with open(filename, "wb") as file:
        if decode:
            file.write(base64.b64decode(content))
        else:
            file.write(content)

def writeWatermarkedImage(input_image_path, output_image_path, watermark_image_path, text=""):
    
    base_image = Image.open(input_image_path).convert('RGBA')
    watermark = Image.open(watermark_image_path).convert('RGBA')
    width, height = base_image.size
    watermark_ratio = watermark.size[1] / watermark.size[0]
    watermark.thumbnail((int((0.2 * base_image.size[0])), int(base_image.size[1] * watermark_ratio)))

    shape = Image.new("RGBA", (width, int(2 * watermark.size[1])), (0, 0, 0, 100))

    transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    transparent.paste(base_image, (0, 0))


    color = (255, 255, 255)
    

    if text =="":
        position = (0, int(height / 2 - shape.size[1] / 2))
        position2 = (int(width/2 - watermark.size[0]/2), int(height/2 - watermark.size[1]/2))
        
        transparent.paste(shape, position, mask=shape)
        transparent.save(output_image_path)
        transparent.paste(watermark, position2, mask=watermark)
        transparent.save(output_image_path)
    else:
        # posicao da shape
        position = (0, int(height / 2 - shape.size[1] / 4))
        # posicao da logo
        position2 = (int(width / 2 - watermark.size[0] / 2), int(height / 2 - watermark.size[1] / 2))    
        fontsize = 1
        img_fraction = 0.75
        
        transparent.paste(shape, position, mask=shape)
        transparent.save(output_image_path)
        transparent.paste(watermark, position2, mask=watermark)
        transparent.save(output_image_path)

        font = ImageFont.truetype(os.path.normpath(os.path.join(STORAGE,"arial.ttf")), fontsize)
        while font.getsize(text)[0] < img_fraction*base_image.size[0] and font.getsize(text)[1] < watermark.height / 2:
            fontsize += 1
            font = ImageFont.truetype(os.path.normpath(os.path.join(STORAGE,"arial.ttf")), fontsize)
            
        fontsize -= 1

        draw = ImageDraw.Draw(transparent)
        position = (int(width/2-font.getsize(text)[0]/2), int(height/2-font.getsize(text)[1]/2 + watermark.size[1]/2 + watermark.size[1] / 2))

        draw.text(position, text, fill=color, font=font)
        transparent.save(output_image_path)