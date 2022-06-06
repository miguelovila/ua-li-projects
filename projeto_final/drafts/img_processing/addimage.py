from PIL import Image, ImageFilter, ImageDraw, ImageFont
import sys
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import os
import io
from Crypto.Util.Padding import pad, unpad

# Transform image to bytes
def TransformToBytes(data):
    image = open(data, 'rb')
    return image.read()



# Transform bytes to image
def TransformToImage(data):
    image = Image.open(io.BytesIO(data))
    image.show()
    image.save("decrypted.png")




# encrypt image
def encryptImage(data):
    block_size = 16
    key = b'NarcisosNarcisos'
    cipher = AES.new(key, AES.MODE_ECB)
    dataencrypted = cipher.encrypt(pad(data, block_size))
    return dataencrypted


# decrypt image
def decryptImage(datatodecrypt):
    block_size = 16
    key = b'NarcisosNarcisos'
    cipher = AES.new(key, AES.MODE_ECB)
    datadecrypted = cipher.decrypt(datatodecrypt)
    datadecrypted = unpad(datadecrypted, block_size)

    image = Image.open(io.BytesIO(datadecrypted))
    image.show()
    image.save("decrypted.png")
    return datadecrypted


# create hash of image
def hashimage(img):
    hash = SHA256.new()
    hash.update(img)
    return hash.hexdigest()


# img = Image.open('logoxImagens.png').convert('RGBA')  # watermark
# img.putalpha(130)
# img.save('watermark.png')

input_image_path = 'RGB.png'  # image to apply watermark
watermark_image_path = 'watermark.png'  # watermark in png
output_image_path = 'img_watermarked.png'  # image watermarked



# apply watermark
def watermark(input_image_path, output_image_path, watermark_image_path):
    base_image = Image.open(input_image_path).convert('RGBA')
    watermark = Image.open(watermark_image_path).convert('RGBA')
    width, height = base_image.size
    watermark_ratio = watermark.size[1] / watermark.size[0]
    watermark.thumbnail((int((0.2 * base_image.size[0])), int(base_image.size[1] * watermark_ratio)))

    shape = Image.new("RGBA", (width, int(2 * watermark.size[1])), (0, 0, 0, 100))

    shape.save("shape.png")

    transparent = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    transparent.paste(base_image, (0, 0))


    color = (255, 255, 255)
    text = "Teste de texto"
    

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

        font = ImageFont.truetype("arial.ttf", fontsize)
        while font.getsize(text)[0] < img_fraction*base_image.size[0] and font.getsize(text)[1] < watermark.height / 2:
            fontsize += 1
            font = ImageFont.truetype("arial.ttf", fontsize)
            
        fontsize -= 1

        draw = ImageDraw.Draw(transparent)
        position = (int(width/2-font.getsize(text)[0]/2), int(height/2-font.getsize(text)[1]/2 + watermark.size[1]/2 + watermark.size[1] / 2))

        draw.text(position, text, fill=color, font=font)
        transparent.save(output_image_path)


def main():
    img = input_image_path

    watermark(img, output_image_path, watermark_image_path)

    #img = Image.open(input_image_path)
    #width, height = img.size
    #print("Largura: %dpx" % width)
    #print("Altura: %dpx" % height)
    #print("Formato: %s" % img.format)
    #
    #
    #imgbytes = TransformToBytes(input_image_path)
    #imageEncrypted = encryptImage(imgbytes)
    #imageDecrypted = decryptImage(imageEncrypted)
    #hash_id = hashimage(imgbytes)
    ## print(imageEncrypted)
    ## print("\n")
    ## print("\n")
    ## print(imageDecrypted)
    #print(hash_id)
    ##TransformToImage(imageDecrypted)
    print("DONE")


main()
