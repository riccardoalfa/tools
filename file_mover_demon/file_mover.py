from __future__ import print_function
import os
import os.path
import time
import sys
import getopt
import requests
import ConfigParser
import settings


"""
Send file to remote Alfa dispenser
"""
__author__ = 'Mario Orlandi, Riccardo Schiavoni'


def read_config(filename):
    """
    Sample result:

        {'general': {'input_file': '~/alfaweb/resources/tools/astec_dispatcher/data/A.txt'},
         'printer': {'printer_name': 'DYMO LabelWriter 45',
                      'label_template': './default.labe',
                      'num_copies': '2'},
         'machine1': {'calibration_sets': 'ACCENT IR,MID IR,WHITE IR',
                      'ip': '192.168.15.129',
                      'password': 'alfakiosk',
                      'username': 'alfakiosk'},
         'machine2': {'calibration_sets': 'ACCENT CF,MID CF,WHITE CF',
                      'ip': '192.168.15.132',
                      'password': 'alfakiosk',
                      'username': 'alfakiosk'},
         'machine3': {'calibration_sets': 'ACCENT MC,MID MC,WHITE MC',
                      'ip': '192.168.15.140',
                      'password': 'alfakiosk',
                      'username': 'alfakiosk'}}
    """

    config_filename = os.path.splitext(sys.argv[0])[0] + os.path.extsep + "cfg"
    config = ConfigParser.ConfigParser()
    config.read(config_filename)

    config_data = {}
    for key in config.sections():
        config_data[key] = dict(config.items(key))
    return config_data


def usage():
    filename = os.path.splitext(sys.argv[0])[0]
    print ("""
Send file to remote Alfa dispensers
version: %s

Please edit "%s.cfg" to configure this application

""" % (settings.VERSION, filename)

)

    """)
    #     print ("""
    # Send file to remote Alfa dispenser
    #
    # Usage:   $ python fsend.py  [options]  datafile  host username password
    #
    # Example: $ python fsend.py  -q  ./fsend.dat  192.168.15.101  alfakiosk  ********
    #
    # Options:
    #     -h = help
    #     -q = quiet
    #     -p N = loop period (in seconds; 0 = execute once then exit; default is 0)
    # """)


def fail(message):
    print ('ERROR: ' + message)
    # Eventually raise exception
    # raise Exception(message)
    sys.exit(1)


def safe_rename_file(sourcename, destname):
    """
    Must work on win32 :<
    """
    if os.path.exists(destname):
        os.remove(destname)
    os.rename(sourcename, destname)


def send_data_to_remote_server(content):
    # First, login
    # See:
    # http://stackoverflow.com/questions/10134690/using-requests-python-library-to-connect-django-app-failed-on-authentication#16022262
    #host = 'http://192.168.15.101/'

    login_url = 'http://' + settings.DEST.host + settings.DEST.login_url
    upload_url = 'http://' + settings.DEST.host + settings.DEST.upload_url
    response = requests.post(login_url,
                             {'username': settings.DEST.username,
                              'password': settings.DEST.password})

    # print(response.content)
    if response.status_code == 200:
        cookies = dict(sessionid=response.cookies['sessionid'],
                       csrftoken=response.cookies['csrftoken'])
        # print(cookies)
        csrftoken = response.cookies['csrftoken']
        # Then, send data
        response = requests.post(
            upload_url,
            files={'file': content, },
            cookies=cookies,
            headers={'X-CSRFToken': csrftoken, }
        )

    return response


def send_data_to_path(content):
    # todo
    pass


def sendfile(filename):

    with open(filename, "r") as f:
        data = f.read()
    response = send_data_to_remote_server(data)
    if settings.VERBOSE:
        # print('\nHost returns: %d (%s)' % (response.status_code, response.content))
        print('\nHost returns: %d' % response.status_code)


def tick():

    if settings.VERBOSE:
        print('.', end='')
        sys.stdout.flush()

    fullfilename = settings.SOURCE.fullfilename
    if os.path.isfile(fullfilename):
        if settings.VERBOSE:
            print('\nnew file detected')
        # make sure new file has been completed
        time.sleep(1.0)
        # rename, then send
        safe_rename_file(fullfilename, fullfilename+'.bak')
        sendfile(fullfilename+'.bak')


def main():

    config_data = read_config(os.path.splitext(sys.argv[0])[0] + os.path.extsep + "cfg")
    if not config_data:
        print("WARNING: No valid config data file!")

    if "general" in config_data:
        gcfg = config_data['general']
        if "source_file_fullname" in gcfg:
            settings.SOURCE.fullfilename = gcfg['source_file_fullname']
        if "dest_host" in gcfg:
            settings.DEST.host = gcfg['dest_host']
        if "dest_username" in gcfg:
            settings.DEST.username = gcfg['dest_username']
        if "dest_password" in gcfg:
            settings.DEST.password = gcfg['dest_password']

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi?qp:", ["help", "quiet"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print(str(err))  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    # scan options
    for o, a in opts:
        if o in ("-h", "--help", "-?"):
            usage()
            sys.exit()
        elif o in ("-q", "--quiet"):
            settings.VERBOSE = False
        elif o in ("-p", ):
            settings.LOOP_PERIOD = int(a)
        else:
            assert False, "unhandled option"

    if len(args) not in (0, 1, 4):
        # user should either pass all arguments or none. If none, all
        # needed values should be set in settings.py!
        usage()
        sys.exit()

    if len(args) >= 1:
        settings.SOURCE.fullfilename = args[0]
    if len(args) == 4:
        settings.DEST.host = args[1]
        settings.DEST.username = args[2]
        settings.DEST.password = args[3]

    while True:
        try:
            tick()
        except Exception, e:
            print('ERROR: ' + str(e))
        if settings.LOOP_PERIOD <= 0:
            break
        time.sleep(settings.LOOP_PERIOD)

if __name__ == "__main__":
    main()

