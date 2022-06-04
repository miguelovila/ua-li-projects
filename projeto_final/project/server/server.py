import cherrypy
import secrets
import string
import random
import time
import json
import os
import io

from cherrypy.lib import file_generator
from config import *
from sqlcon import *
from imgproc import *


class Root(object):
	def __init__(self):
			self.api = Api()
	@cherrypy.expose
	def index(self):
		return open(LANDING_PAGE).read()
		
	@cherrypy.expose
	def about(self):
		return open(ABOUT_PAGE).read()
		
	@cherrypy.expose
	def profile(self):
		return open(SCRIPT_PROFILE).read()
		
	@cherrypy.expose
	def upload(self):
		return open(SCRIPT_UPLOAD).read()

	@cherrypy.expose
	def signin(self):
		return open(SCRIPT_SIGNIN).read()

	@cherrypy.expose
	def signup(self):
		return open(SCRIPT_SIGNUP).read()

	@cherrypy.expose
	def collections(self, id = None):
		if id == None:
			return open(SCRIPT_COLLECTIONS).read()
		else:
			return open(SCRIPT_COLLECTION).read()

	@cherrypy.expose()
	def image(self, id = None):
		if id == None:
			raise cherrypy.HTTPRedirect("/")
		else:
			return open(SCRIPT_IMAGE).read()

class Api(object):
	def __init__(self):
		self.users = Users()
		self.pages = Pages()
		self.cromos = Cromos()

	@cherrypy.expose
	def index(self):
		raise cherrypy.HTTPRedirect("/")

class Pages():
	@cherrypy.expose
	def index(self):
		raise cherrypy.HTTPRedirect("/")

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def landing(self):
		body = cherrypy.request.json
		expiration = selector("SELECT expiry FROM tokens WHERE token = ?", (body['token'],))
		if body['token'] == None or len(expiration) == 0 or expiration[0][0] < int(time.time()):
			return {'status': 'OK1', 'body': '<a id="a-button-action" href="./signin"><button id="button-action" type="button" class="btn btn-primary">Autenticação <i class="fa-solid fa-key"></i></button></a>'}
		else:
			return {'status': 'OK', 'body': '<a id="a-button-action" href="./collections"><button id="button-action" type="button" class="btn btn-primary">Ver Coleções <i class="fa-solid fa-images"></i></button></a>'}

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def signin(self):
		body = cherrypy.request.json
		expiration = selector("SELECT expiry FROM tokens WHERE token = ?", (body['token'],))
		if body["token"] == None or len(expiration) == 0 or expiration[0][0] < int(time.time()):
			return {"status": "OK", "body": open(SIGNIN_PAGE_BODY).read()}
		else:
			return {"status": "FORBIDDEN", "body": ""}
		
	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def signup(self):
		body = cherrypy.request.json
		expiration = selector("SELECT expiry FROM tokens WHERE token = ?", (body['token'],))
		if body["token"] == None or len(expiration) == 0 or expiration[0][0] < int(time.time()):
			return {"status": "OK", "body": open(SIGNUP_PAGE_BODY).read()}
		else:
			return {"status": "FORBIDDEN", "body": ""}

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def upload(self):
		body = cherrypy.request.json
		expiration = selector("SELECT expiry FROM tokens WHERE token = ?", (body['token'],))
		if body["token"] == None or len(expiration) == 0 or expiration[0][0] < int(time.time()):
			return {"status": "FORBIDDEN", "body": ""}
		else:
			return {"status": "OK", "body": open(UPLOAD_PAGE_BODY).read()}

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def collections(self):
		body = cherrypy.request.json
		expiration = selector("SELECT expiry FROM tokens WHERE token = ?", (body['token'],))
		if body["token"] == None or len(expiration) == 0 or expiration[0][0] < int(time.time()):
			return {"status": "FORBIDDEN", "body": ""}
		else:
			return {"status": "OK", "body": open(COLLECTIONS_PAGE_BODY).read()}

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def collection(self):
		body = cherrypy.request.json
		expiration = selector("SELECT expiry FROM tokens WHERE token = ?", (body['token'],))
		if body["token"] == None or len(expiration) == 0 or expiration[0][0] < int(time.time()):
			return {"status": "FORBIDDEN", "body": ""}
		else:
			return {"status": "OK", "body": open(COLLECTION_PAGE_BODY).read()}

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def profile(self):
		body = cherrypy.request.json
		expiration = selector("SELECT expiry FROM tokens WHERE token = ?", (body['token'],))
		if body["token"] == None or len(expiration) == 0 or expiration[0][0] < int(time.time()):
			return {"status": "FORBIDDEN", "body": ""}
		else:
			return {"status": "OK", "body": open(PROFILE_PAGE_BODY).read()}

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def image(self):
		body = cherrypy.request.json
		image_owner = selector("SELECT owner FROM images WHERE identifier = ?", (body['img_id'],))
		data = selector("SELECT expiry, username FROM tokens WHERE token = ?", (body['token'],))
		expiration = data[0][0]
		username = data[0][1]
		if body["token"] == None or len(data) == 0 or expiration < int(time.time()):
			return {"status": "FORBIDDEN", "body": ""}
		else:
			if image_owner[0][0] == username:
				return {"status": "OK", "type": "owner", "body": open(COLLECTION_PAGE_BODY).read()}
			elif image_owner[0][0] == None:
				return {"status": "OK", "type": "free", "body": open(COLLECTION_PAGE_BODY).read()}
			else:
				return {"status": "OK", "type": "viewer", "body": open(COLLECTION_PAGE_BODY).read()}

class Users():
	@cherrypy.expose
	def index(self):
		raise cherrypy.HTTPRedirect("/")

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def auth(self):
		body = cherrypy.request.json
		user = selector("SELECT * FROM users WHERE username = ? AND password = ?", (body["username"], body["password"]))
		if len(user) == 1:
			token = secrets.token_hex(4)
			expire = int(time.time()) + 7200
			executor("INSERT INTO tokens (token, expiry, username) VALUES (?, ?, ?)",(token, expire, body["username"],))
			return {"authentication": "OK","token": "{}".format(token)}
		else:
			return {"authentication": "ERROR","token": ""}

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def valid(self):
		body = cherrypy.request.json
		expiration = selector("SELECT expiry FROM tokens WHERE token = ?", (body["token"],))
		if body["token"] == None or len(expiration) == 0 or expiration[0][0] < int(time.time()):
			return {"authentication": "ERROR"}
		else:
			return {"authentication": "OK"}

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def create(self):
		body = cherrypy.request.json
		invalid = False
		for c in body["username"]:
			if c not in string.ascii_letters + string.digits:
				invalid = True
		if body["username"].rstrip() == "" or selector("SELECT * FROM users WHERE username = ?", (body["username"],)) or invalid:
			return {"creation": "ERROR","password": ""}
		else:
			password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
			executor("INSERT INTO users (username, password, owimages) VALUES (?, ?, '')",(body["username"], password))
			return {"creation": "OK", "password": "{}".format(password)}

@cherrypy.popargs("id")
class Cromos():
	def __init__(self):
		self.image = ImgEndpoint()

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def index(self, id = None):
		if id == None:
			images = selector("SELECT * FROM images", ())
		else:
			collection_name = selector("SELECT name FROM collections WHERE identifier = ?", (id,))
			images = selector("SELECT * FROM images WHERE collection = ?", (collection_name[0][0],))
		return images if len(images) > 0 else {"status": "ERROR", "message": "No images found"}

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def profile(self, id = None):
		if id == None:
			images = selector("SELECT * FROM images", ())
		else:
			username = selector("SELECT username FROM tokens WHERE token = ?", (id,))
			images = selector("SELECT * FROM images WHERE owner = ?", (username[0][0],))
		return images if len(images) > 0 else {"status": "OK1", "message": "No images found"}

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def data(self, id = None):
		if id == None:
			return {"status": "ERROR", "message": "No image specified"}
		else:
			images = selector("SELECT * FROM images WHERE identifier = ?", (id,))
		return images if len(images) > 0 else {"status": "ERROR", "message": "No image found"}

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def collections(self):
		body = cherrypy.request.json
		expiration = selector("SELECT expiry FROM tokens WHERE token = ?", (body["token"],))
		if body["token"] == None or len(expiration) == 0 or expiration[0][0] < int(time.time()):
			return {'status': 'ERROR'}
		else:
			collections = selector("SELECT * FROM collections", ())
			return {"status": "OK", "message": "Got collections", "body": collections} if len(collections) > 0 else {"status": "OK", "message": "No collections found"}

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def claim(self):
		body = cherrypy.request.json
		data = selector("SELECT expiry, username FROM tokens WHERE token = ?", (body['token'],))
		imgid = body['id']
		expiration = data[0][0]
		username = data[0][1]
		if body["token"] == None or len(data) == 0 or expiration < int(time.time()):
			return {"status": "ERROR"}
		else:
			if body["username"] != "":
				if body["username"].rstrip() == "" or selector("SELECT * FROM users WHERE username = ?", (body["username"],)):
					username = body["username"]
				else:
					return {"status": "ERROR"}
			executor("UPDATE images SET owner = ? WHERE identifier = ?", (username, imgid,))
			prev_hist_db = selector("SELECT history FROM images WHERE identifier = ?", (imgid,))[0][0]
			prev_hist = json.loads(prev_hist_db) if prev_hist_db != None else json.loads('[]')
			prev_hist.append({"ts": int(time.time()), "action": "claim", "username": username})
			executor("UPDATE images SET history = ? WHERE identifier = ?", (json.dumps(prev_hist), imgid,))
			image_hash = selector("SELECT hash FROM images WHERE identifier = ?", (imgid,))[0][0]
			original_image_path = os.path.normpath(os.path.join(STORAGE,f"original/{image_hash}.png"))
			water_image_path = os.path.normpath(os.path.join(STORAGE,f"protected/{image_hash}.png"))
			temp_image_path = os.path.normpath(os.path.join(STORAGE,f"temporary/{image_hash}.png"))
			img_file = open(original_image_path, "rb")
			img_dec = decryptImage(img_file.read())
			img_file.close()
			writeImage(img_dec, temp_image_path, False)
			writeWatermarkedImage(temp_image_path, water_image_path, WATERMARK, username)
			os.remove(temp_image_path)
			return {"status": "OK"}

	@cherrypy.expose
	@cherrypy.tools.json_in()
	@cherrypy.tools.json_out()
	def upload(self):
		body = cherrypy.request.json
		text_to_remove = body["image"][:body["image"].index(",")]
		base64_image = body["image"].replace(text_to_remove, "")

		image_name = body["name"].capitalize()
		image_collection = body["collection"].title()
		image_extension = "png"
		image_hash = hashImage(base64_image)
		if selector("SELECT * FROM images WHERE hash = ?", (image_hash,)):
			return {"status": "ERROR","message": "similar image already exists"}

		os.makedirs(os.path.normpath(os.path.join(STORAGE,"temporary/")), exist_ok=True)
		os.makedirs(os.path.normpath(os.path.join(STORAGE,"protected/")), exist_ok=True)
		os.makedirs(os.path.normpath(os.path.join(STORAGE,"original/")), exist_ok=True)

		temp_image_path = os.path.normpath(os.path.join(STORAGE,f"temporary/{image_hash}.{image_extension}"))
		water_image_path = os.path.normpath(os.path.join(STORAGE,f"protected/{image_hash}.{image_extension}"))
		original_image_path = os.path.normpath(os.path.join(STORAGE,f"original/{image_hash}.{image_extension}"))

		image_bytes = base64.b64decode(base64_image)

		writeImage(base64_image, temp_image_path)
		writeWatermarkedImage(temp_image_path, water_image_path, WATERMARK)
		writeImage(encryptImage(image_bytes), original_image_path)

		owner = selector("SELECT username FROM tokens WHERE token = ?", (body["token"],))[0][0]
		hist = json.loads('[]')
		hist.append({"ts": int(time.time()), "action": "upload", "username": owner})
		executor("INSERT INTO images (name, collection, hash, extension, history) VALUES (?, ?, ?, ?, ?)",(image_name, image_collection, image_hash, image_extension, json.dumps(hist)))

		if not selector("SELECT * FROM collections WHERE name = ?", (image_collection,)):
			executor("INSERT INTO collections (name, owner) VALUES (?, ?)",(image_collection, owner,))

		os.remove(temp_image_path)

		return {"status": "OK"}

class ImgEndpoint(object):
	@cherrypy.expose
	def index(self, id):
		cherrypy.response.headers['Content-Type'] = "image/png"
		image_data = selector("SELECT * FROM images WHERE identifier = ?", (id,))
		if len(image_data) == 0:
			return {"status": "ERROR", "message": "Image not found"}
		image_path = os.path.normpath(os.path.join(STORAGE,f"protected/{image_data[0][3]}.{image_data[0][2]}"))
		with open(image_path, "rb") as image:
			image_bytes = image.read()
		image_buffer = io.BytesIO(image_bytes)
		image_buffer.seek(0)
		return file_generator(image_buffer)

if __name__ == '__main__':
		cherrypy.config.update({'server.socket_port': 10005})
		initializeDatabase()
		cherrypy.quickstart(Root(), '/', SERVER_CONFIG)