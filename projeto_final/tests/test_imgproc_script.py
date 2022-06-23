from subprocess import Popen, PIPE

from imgproc_script import *

def imgproc_script(args=""):
    proc = Popen(f"python3 imgproc_script.py {args}", shell=True, stdout=PIPE)
    return proc.stdout.read()


input_image_path = "./RGB.png"
output_image_path = "./output.png"
watermark_image_path = "./watermark.png"
text= ""




def test_imgproc_script():
    print("Testing imgproc_script.py")
    assert "No input image specified" in imgproc_script(writeWatermarkedImage("", output_image_path, watermark_image_path, text))
    
    