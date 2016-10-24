class Bunch():
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

VERSION = "0.1"
VERBOSE = True
LOOP_PERIOD = 1  # seconds; 0 = run once then exit

SOURCE = Bunch(
    type='path',    # only path supported for now
    fullfilename=None,
)

DEST = Bunch(
    type='http-post',   # 'http-post' | 'path'
    host=None,		    # used only if type == 'http-XXX'
    login_url=None,     # used only if type == 'http-XXX'
    upload_url=None,    # used only if type == 'http-XXX'
    filename=None,      # used only if type == 'path', None to keep source name
    username=None,	    # used only if needed
    password=None,	    # used only if needed
)

SOURCE.fullfilename = 'c:\\prova.tmp\\fsend.dat'

DEST.host = '192.168.56.101'
DEST.login_url = '/a9fb26d39e8b7c99/api/login_user/'
DEST.upload_url = '/admin/client/dispensationqueue/upload-recipe/'
DEST.username = 'test_f'
DEST.password = 'xxx1'
