import os
import subprocess
import datetime
import Tkinter as tkinter
import ttk
def _(x): return x


TESTDATA="""INFO: N/A

VERSION:  N/A

IP_eth2=192.168.56.102
MACADDR_eth2=08:00:27:92:48:7d=08002792487d

IP_eth3=10.0.2.15
MACADDR_eth3=08:00:27:87:92:b7=0800278792b7

 - - - - - - - - - - - - - - - - -
INFO[root]:
alfaserial: -----
alfawhich: alfakiosk
alfahw: colortester

VERSION[root]:  1.0.1

IP_eth0=
MACADDR_eth0=b8:27:eb:9c:36:1e=b827eb9c361e

IP_wlan0=192.168.1.20
MACADDR_wlan0=b8:27:eb:c9:63:4b=b827ebc9634b

 - - - - - - - - - - - - - - - - -
"""

DEBUG = True


class CONST:
    iso_source = '/mnt/ISO/'
    def_scan_ip = '192.168.1'
    hosts_list_file = 'ui_data/hosts_list.dat'
    logs_dir = 'ui_data/logs'

    def __init__(self):
        pass


class Window:
    WINDOWS = {}
    DEFAULT_SETTINGS = {
        "WINDOW_SIZE": "1024x768"
    }

    class PopUp:
        def __init__(self):
            pass

    class AlreadyExistsError(Exception):
        pass

    @staticmethod
    def separator(win, master, orient='horizontal', frame=None,
                  color='black', thickness=7, length=None, Dlenght=50,
                  pack_reverse=False, grid=None):

        height = 69
        width = 69
        if orient == 'horizontal':
            height = thickness
            if length:
                width = length
            else:
                win_width = int(win.get_config('WINDOW_SIZE').split('x')[0])
                width = win_width - Dlenght

        elif orient == 'vertical':
            width = thickness
            if length:
                height = length
            else:
                win_height = int(win.get_config('WINDOW_SIZE').split('x')[1])
                width = win_height - Dlenght

        sep = tkinter.Frame(master, height=height, width=width, background=color)

        if grid:
            sep.grid(**grid)
        else:
            if orient == 'horizontal':
                if pack_reverse:
                    sep.pack(side=tkinter.BOTTOM)
                else:
                    sep.pack(side=tkinter.TOP)
            elif orient == 'vertical':
                if pack_reverse:
                    sep.pack(side=tkinter.RIGHT)
                else:
                    sep.pack(side=tkinter.LEFT)

    def alert(self, txt='<Empty alert>'):
        alert = self.PopUp()    # just wrapper class, like Bunch()
        alert.fr_root = tkinter.Toplevel(self.tk)
        alert.fr_root.wm_title("Alert")

        # add content
        alert.wi_editor = tkinter.Text(alert.fr_root, width=69, height=3)
        alert.wi_editor.pack(side=tkinter.TOP)
        alert.wi_editor.insert(tkinter.END, '\n   ' + txt)
        alert.wi_editor.configure(state=tkinter.DISABLED, font=("", 18, "bold"))

        #       Button - Close
        alert.bt_close = tkinter.Button(
            alert.fr_root, text=_("Close"), command=alert.fr_root.destroy)
        alert.bt_close.pack(side=tkinter.TOP)

        # position in center of main windows
        self.loop_once()    # needed to update window size
        root = self.tk
        x = root.winfo_x()
        y = root.winfo_y()

        w = alert.fr_root.winfo_width()
        h = alert.fr_root.winfo_height()
        alert.fr_root.geometry("%dx%d+%d+%d" % (w, h, x + 100, y + 200))

    def __init__(self, name, **kwargs):
        if name in self.WINDOWS:
            raise self.AlreadyExistsError

        self.tk = tkinter.Tk()
        self.name = str(name)
        self.settings = {}
        self.WINDOWS[name] = self
        self.config(**dict(self.DEFAULT_SETTINGS.items() + kwargs.items()))

    def loop_once(self):
        self.tk.update_idletasks()
        self.tk.update()

    def mainloop(self):
        self.tk.mainloop()

    def config(self, **kwargs):
        if 'WINDOW_SIZE' in kwargs:
            self.tk.geometry(kwargs['WINDOW_SIZE'])
            self.settings['WINDOW_SIZE'] = kwargs['WINDOW_SIZE']

    def get_config(self, cfg):
        if cfg in self.settings:
            return self.settings[cfg]
        return self.DEFAULT_SETTINGS[cfg]

    def close(self):
        self.tk.destroy()
        del self.WINDOWS[self.name]

    @classmethod
    def close_all(cls):
        for w in cls.WINDOWS.values():
            w.close()

    @classmethod
    def get(cls, name, **kwargs):
        name = str(name)
        if name in cls.WINDOWS:
            ret = cls.WINDOWS[name]
            ret.config(**kwargs)
        else:
            ret = cls(name, **kwargs)

        return ret


class RtOutput:
    # Real Time display of bash file output

    def __init__(self, master, reader, write_log=True):
        self.log = ''
        self.master = master
        self.reader = reader
        self.fr_root = tkinter.Toplevel(self.master)

        self.wi_output = tkinter.Text(self.fr_root, width=120, height=49)
        self.wi_output.pack(side=tkinter.TOP)

        while True:
            out = self.reader.stdout.readline()
            if out == '' and self.reader.poll() is not None:
                break
            self.log += out
            self.append(out)

        if write_log:
            log_file_name = os.path.join(CONST.logs_dir,
                                         str(datetime.datetime.now()) + '.log')
            with open(log_file_name, 'w') as fp:
                fp.write(self.log)

        #       Button - Close
        self.bt_close = tkinter.Button(
            self.fr_root, text=_("Close"), command=self.fr_root.destroy)
        self.bt_close.pack(side=tkinter.TOP)

    def append(self, data):
        if data:
            self.wi_output.insert(tkinter.END, data)
            self.wi_output.see(tkinter.END)
            self.wi_output.update_idletasks()


class HostsFileEdit:

    def __init__(self, deployer, content=None):
        self.deployer = deployer
        self.fr_root = tkinter.Toplevel(self.deployer.win.tk)

        self.wi_editor = tkinter.Text(self.fr_root, width=120, height=30)
        self.wi_editor.pack(side=tkinter.TOP)

        self.fr_btns = tkinter.Frame(self.fr_root)
        self.fr_btns.pack(side=tkinter.TOP)
        #       Button - Cancel
        self.bt_close = tkinter.Button(
            self.fr_btns, text=_("Cancel"), command=self.close)
        self.bt_close.pack(side=tkinter.LEFT)
        #       Button - Deploy
        self.bt_deploy = tkinter.Button(
            self.fr_btns, text=_("Deploy!!"),
            fg="red", command=self.deploy)
        self.bt_deploy.pack(side=tkinter.LEFT)

        if content is not None:
            self.set_content(content)

    def set_content(self, content=''):
        self.wi_editor.delete('1.0', tkinter.END)
        self.wi_editor.insert(tkinter.END, content)

    def get_content(self):
        ret = self.wi_editor.get("1.0", 'end-1c')
        return ret

    def close(self):
        self.fr_root.destroy()
        self.deployer.deploy(action='abort')

    def deploy(self):
        data = self.get_content()
        if not data:
            return

        content = self.get_content()
        self.fr_root.destroy()
        self.deployer.deploy(action='deploy', data=content)


class Cloner:

    class InvalidDeployerError(Exception):
        pass

    def __init__(self):
        self.win = Window('deployer')

        # names of all directories in folder (which contains only deployers)
        # i.e. ['KioskDep_1.0.1', 'KioskDep_1.0.3']
        self.deps = []

        # Structure
        # root
        self.fr_root = tkinter.Frame(self.win.tk)
        self.fr_root.pack()

        #    Widget - Window Title
        self.wi_title_root = tkinter.Text(self.fr_root, height=1)
        self.wi_title_root.pack(side=tkinter.TOP)
        self.wi_title_root.insert(tkinter.END, _("AMAZING DISK Cloner"))
        self.wi_title_root.configure(state=tkinter.DISABLED, font=("", 21, "bold"))

        #    Widget - Clone FROM device
        self.wi_title_read = tkinter.Text(self.fr_root, height=1, width=69)
        self.wi_title_read.pack(side=tkinter.TOP)
        self.wi_title_read.insert(tkinter.END, _("Option 1: Read (Create image FROM device)"))
        self.wi_title_read.configure(state=tkinter.DISABLED, font=("", 16))
        #    Frame - Clone FROM device
        self.fr_read = tkinter.Frame(self.fr_root)
        self.fr_read.pack(side=tkinter.TOP)
        #       Widget - Intro read
        self.wi_title_read = tkinter.Text(self.fr_read, height=1, width=30)
        self.wi_title_read.pack(side=tkinter.LEFT)
        self.wi_title_read.insert(tkinter.END, _("Insert image name (min 3 chars): "))
        self.wi_title_read.configure(state=tkinter.DISABLED)
        #       Widget - iso name input field
        self.wi_read_input = tkinter.Text(self.fr_read, height=1, width=69)
        self.wi_read_input.pack(side=tkinter.LEFT)
        #       Button - read device
        self.bt_read = tkinter.Button(self.fr_read, text=_("Read!"), fg="blue", command=self.read_device)
        self.bt_read.pack(side=tkinter.TOP)

        #    Frame - Separator
        Window.separator(self.win, self.fr_root, color='orange', thickness=17)

        #    Widget - Clone TO device
        self.wi_title_write = tkinter.Text(self.fr_root, height=1, width=69)
        self.wi_title_write.pack(side=tkinter.TOP)
        self.wi_title_write.insert(tkinter.END, _("Option 2: Write (write image TO device)"))
        self.wi_title_write.configure(state=tkinter.DISABLED, font=("", 16))
        #    Frame - select image to write
        self.fr_write_select_iso = tkinter.Frame(self.fr_root)
        self.fr_write_select_iso.pack(side=tkinter.TOP)
        #       Button - read device
        self.bt_read = tkinter.Button(self.fr_root, text=_("Write!"), fg="blue", command=self.write_device)
        self.bt_read.pack(side=tkinter.TOP)

        # used self variables
        self.selected_iso = tkinter.StringVar()

        # Start
        # self.read_iso()
        # self.read_targets()

        self.win.mainloop()

    def read_device(self):
        pass

    def write_device(self):
        pass

    def read_iso(self):
        if not DEBUG:
            self.deps = [x for x in os.listdir(CONST.iso_source)]
        else:
            self.deps = ['ISO_debug__1', 'ISO_debug__2']
        # self.deps = [x for x in os.listdir(CONST.dep_source)
        #              if os.path.isdir(os.path.join(CONST.dep_source, x))]

        for i, dep in enumerate(self.deps):
            chbt = tkinter.Radiobutton(
                self.fr_deps, text=dep,
                variable=self.selected_iso, value=dep,
                command=self.test)
            chbt.grid(row=i / 3, column=i % 3)
        # self.selected_deployer.set(self.deps[-3])

    def get_selected_dep_alfawhich(self):
        selected_dep_name = self.selected_deployer.get().lower()
        if 'kiosk' in selected_dep_name:
            return 'alfakiosk'
        elif 'desk' in selected_dep_name:
            return 'alfadesk'
        else:
            self.win.alert(_('To proceed, please select Deployer'))
            raise self.InvalidDeployerError

    def read_targets(self):
        if self.scan_begun:
            return
        try:
            self.scan_begun = True
            for target in self.targets:
                target['chbt'].destroy()
            self.targets = []

            self.wi_targets_loading = tkinter.Text(self.fr_targets, height=3)
            self.wi_targets_loading.pack(side=tkinter.TOP)
            self.wi_targets_loading.insert(tkinter.END,
                                         _("Scanning network,\nplease wait..."))
            self.wi_targets_loading.configure(state=tkinter.DISABLED,
                                            font=("", 17, "italic"))

            self.win.loop_once()

            self.targets = []
            subnet = self.wi_subnet_input.get("1.0", 'end-1c').replace(' ', '')
            if not DEBUG:
                scan = subprocess.check_output(
                    '~/bin/ssh_responder.sh scan ' + subnet, shell=True)
            else:
                scan = TESTDATA
            self.wi_targets_loading.destroy()

            mode = None
            net = None
            target = {}
            for line in scan.splitlines():
                if line.startswith("INFO"):
                    mode = 'INFO'
                    if target:
                        self.targets.append(target)

                    target = {
                        'alfaserial': '',
                        'alfawhich': '',
                        'alfahw': '',
                        'version': '',
                        'network': [
                            # {'ip': '...', macaddr: '...'},
                            # {'ip': '...', macaddr: '...'},
                            # ...
                        ],
                    }
                elif line.startswith("VERSION"):
                    mode = 'VERSION'
                    target['version'] = line[line.find(':') + 1:].strip()
                elif line.startswith("IP_") and mode in ('VERSION', 'MACADDR'):
                    mode = 'IP'
                    ip = line.split('=')[1].strip()
                    if not ip:
                        # invalid, return to previous mode to skip related macaddr
                        mode = 'VERSION'
                        continue
                    net = {'ip': ip}
                elif line.startswith("MACADDR_") and mode == 'IP':
                    mode = 'MACADDR'
                    net['macaddr'] = line.split('=')[1].strip()
                    target['network'].append(net)
                elif line and mode == 'INFO':
                        for code in ('alfaserial', 'alfawhich', 'alfahw'):
                            if line.startswith(code):
                                target[code] = line[line.find(':') + 1:].strip()
            if target:
                self.targets.append(target)

            for i, target in enumerate(self.targets):
                ip = None
                if target['network']:
                    if not target['network'][0]['ip'].endswith('10.100'):
                        ip = target['network'][0]['ip']
                    elif len(target['network']) > 1:
                        ip = target['network'][1]['ip']

                if not ip:
                    print("WARNING - cannot deploy to: no ip for " + str(target))
                    continue

                tag = "SN: {0}\n{1}\nv: {2}\nIP: {3}".format(
                    target['alfaserial'],
                    target['alfawhich'],
                    target['version'],
                    ip,
                )
                target['val'] = tkinter.IntVar()
                target['val'].set(0)
                target['chbt'] = tkinter.Checkbutton(
                    self.fr_targets, text=tag, variable=target['val'])
                target['chbt'].grid(row=i / 7, column=i % 7)
        finally:
            self.scan_begun = False

    def select_all_targets(self):
        for target in self.targets:
            target['val'].set(1)

    def get_selected_targets(self):
        ret = []
        for target in self.targets:
            if target['val'].get():
                ret.append(target)
        return ret

    def clear(self):
        self.selected_deployer.set(None)
        for target in self.targets:
            target['val'].set(0)
        print("FUCKING CLEARED!")

    def deploy(self, action=None, data=None):
        if action is None:
            hosts_lines = ''
            targets = self.get_selected_targets()
            selected_dep_alfawhich = self.get_selected_dep_alfawhich()
            for target in targets:
                hosts_lines += '{0}    embedded_system=True    username={1}\n'.format(
                    target['network'][0]['ip'],
                    selected_dep_alfawhich
                )

            self.hosts_file_edit = HostsFileEdit(self, hosts_lines)

        elif action == 'abort':
            self.hosts_file_edit = None

        elif action == 'deploy':
            with open(CONST.hosts_list_file, 'w') as fp:
                fp.write(data)

            reader = subprocess.Popen(
                './deploy_now.sh {alfawhich} {dep_branch} {deployer}'.format(
                    alfawhich=self.get_selected_dep_alfawhich(),
                    dep_branch='usb',
                    deployer=self.selected_deployer.get()
                ), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            RtOutput(self.win.tk, reader)

            print("vanita delle vanita tutto est vanita!")

    def test(self):
        print("Dep Selected: " + str(self.selected_deployer.get()))


def main():
    dep = Cloner()

if __name__ == '__main__':
    main()

