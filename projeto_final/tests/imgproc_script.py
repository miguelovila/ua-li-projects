import hashlib
import base64
import sys
import os
import io
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random
# from config import *

pad   = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

def hashImage(base64_img):
    hash = SHA256.new()
    hash.update(base64_img.encode('utf-8'))
    return hash.hexdigest()

def encryptImage(data):
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(hashlib.sha256(KEY.encode("utf-8")).digest(), AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(pad(data)))

def decryptImage(data):
    enc = base64.b64decode(data)
    iv = enc[:16]
    cipher = AES.new(hashlib.sha256(KEY.encode("utf-8")).digest(), AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))

def writeImage(content, filename):
    with open(filename, "wb") as file:
        file.write(base64.b64decode(content))

def writeWatermarkedImage(input_image_path, output_image_path, watermark_image_path, text=""):
    if not os.path.isfile(input_image_path):
        return "No input image specified"
    elif not os.path.isfile(output_image_path) == "":
        return "No way specified to save the image"
    elif not os.path.isfile(watermark_image_path) == "":
        return "No watermark image specified"
    
    
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

        font = ImageFont.truetype("../storage/arial.ttf", fontsize)
        while font.getsize(text)[0] < img_fraction*base_image.size[0] and font.getsize(text)[1] < watermark.height / 2:
            fontsize += 1
            font = ImageFont.truetype("../storage/arial.ttf", fontsize)
            
        fontsize -= 1

        draw = ImageDraw.Draw(transparent)
        position = (int(width/2-font.getsize(text)[0]/2), int(height/2-font.getsize(text)[1]/2 + watermark.size[1]/2 + watermark.size[1] / 2))

        draw.text(position, text, fill=color, font=font)
        transparent.save(output_image_path)
    
    return "Image saved"