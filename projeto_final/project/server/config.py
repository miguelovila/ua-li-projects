import os

SERVER  = os.path.abspath(os.path.dirname(__file__))
STORAGE = os.path.normpath(os.path.join(SERVER, '../storage'))
STORAGE_DB = os.path.normpath(os.path.join(STORAGE, '../storage/database.db'))
WATERMARK = os.path.normpath(os.path.join(SERVER, '../client/img/logo.png'))
SHAPE = os.path.normpath(os.path.join(STORAGE, 'temporary/shape.png'))
FONT = os.path.normpath(os.path.join(STORAGE, 'arial.ttf'))
KEY = 'umapasswordfixe!'

LANDING_PAGE = os.path.normpath(os.path.join(SERVER, '../client/landing.html'))

SIGNIN_PAGE_BODY = os.path.normpath(os.path.join(SERVER, '../client/body-signin.html'))
SCRIPT_SIGNIN= os.path.normpath(os.path.join(SERVER, '../client/script-signin.html'))

SIGNUP_PAGE_BODY = os.path.normpath(os.path.join(SERVER, '../client/body-signup.html'))
SCRIPT_SIGNUP = os.path.normpath(os.path.join(SERVER, '../client/script-signup.html'))

UPLOAD_PAGE_BODY = os.path.normpath(os.path.join(SERVER, '../client/body-upload.html'))
SCRIPT_UPLOAD = os.path.normpath(os.path.join(SERVER, '../client/script-upload.html'))

COLLECTIONS_PAGE_BODY= os.path.normpath(os.path.join(SERVER, '../client/body-collections.html'))
SCRIPT_COLLECTIONS = os.path.normpath(os.path.join(SERVER, '../client/script-collections.html'))

COLLECTION_PAGE_BODY= os.path.normpath(os.path.join(SERVER, '../client/body-collection.html'))
SCRIPT_COLLECTION = os.path.normpath(os.path.join(SERVER, '../client/script-collection.html'))

IMAGE_PAGE_BODY= os.path.normpath(os.path.join(SERVER, '../client/body-image.html'))
SCRIPT_IMAGE = os.path.normpath(os.path.join(SERVER, '../client/script-image.html'))

ABOUT_PAGE= os.path.normpath(os.path.join(SERVER, '../client/about.html'))

PROFILE_PAGE_BODY= os.path.normpath(os.path.join(SERVER, '../client/body-profile.html'))
SCRIPT_PROFILE = os.path.normpath(os.path.join(SERVER, '../client/script-profile.html'))


SERVER_CONFIG = {
    '/': {
        'tools.sessions.on': True,
        'tools.staticdir.root': SERVER
    },
    '/css': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.normpath(os.path.join(SERVER, '../client/css/'))
    },
    '/img': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.normpath(os.path.join(SERVER, '../client/img/'))
    },
    '/js': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.normpath(os.path.join(SERVER, '../client/js/'))
    }
}