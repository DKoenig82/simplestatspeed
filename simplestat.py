import os
import psutil
import rumps
import subprocess
import time
import socket
import Foundation
import webbrowser

basedir = os.path.dirname(__file__)

try:
    from ctypes import windll

    myappid = "de.davidkoenig.simple-stat-speed.1.0.1"

    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

def get_ip_addresses(family):
    for interface, snics in psutil.net_if_addrs().items():
        mac = None
        for snic in snics:
            if snic.family == -1:
                mac = snic.address
            if snic.family == 2:
                yield (interface, snic.address, snic.netmask, mac)


def on_calculate_speed(interface):
    dt = 0.6
    t0 = time.time()
    try:
        counter = psutil.net_io_counters(pernic=True)[interface]
    except KeyError:
        return []

    tot = (counter.bytes_sent, counter.bytes_recv)
    while True:
        last_tot = tot
        time.sleep(dt)
        try:
            counter = psutil.net_io_counters(pernic=True)[interface]
        except KeyError:
            break
        t1 = time.time()
        tot = (counter.bytes_sent, counter.bytes_recv)
        ul, dl = [
            (now - last) / (t1 - t0) / 1024.0
            for now, last
            in zip(tot, last_tot)
        ]
        return [int(ul), int(dl)]
        t0 = time.time()


def check_appearance():
    cmd = 'defaults read -g AppleInterfaceStyle'
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    return bool(p.communicate()[0])


def get_cpu_usage():
    run = True
    if run is True:
        return psutil.cpu_percent(interval=0.5)


def get_ram_perc_usage():
    run = True
    if run is True:
        mem_usage = psutil.virtual_memory()
        return mem_usage.percent


def get_ram_gb_usage():
    run = True
    if run is True:
        mem_usage = psutil.virtual_memory()
        return mem_usage.percent*(mem_usage.total/(1024**3))/100


class SimpleStatApp(rumps.App):
    def __init__(self):
        super(SimpleStatApp, self).__init__("⚡️SimpleStatSpeed ⚡️")
        mem_usage = psutil.virtual_memory()
        iostat = psutil.net_io_counters(pernic=False)
        upload = iostat[0]
        download = iostat[1]
        self.interval = 1200
        self.show_All_button = rumps.MenuItem(title="Show All", callback=self.show_All)
        self.show_Cpu_button = rumps.MenuItem(title="Show CPU", callback=self.show_Cpu)
        self.show_Ram_button = rumps.MenuItem(title="Show RAM", callback=self.show_Ram)
        self.show_Cpu_Ram_button = rumps.MenuItem(title="Show CPU & RAM", callback=self.show_cpu_ram)
        self.show_Network_button = rumps.MenuItem(title="Show Network", callback=self.show_Network)
        self.show_Network_cpu_button = rumps.MenuItem(title="Show CPU & Network", callback=self.show_cpu_network)
        self.show_Network_ram_button = rumps.MenuItem(title="Show RAM & Network", callback=self.show_ram_network)
        self.upload_button = rumps.MenuItem(title=("{}".format(self.calculate_speed_unit(upload))), callback=self.update_count)
        self.download_button = rumps.MenuItem(title=("{}".format(self.calculate_speed_unit(download)) + " Pieces"), callback=self.update_count)
        self.count_button = rumps.MenuItem(title= ("{}".format(psutil.cpu_count()) + " Pieces"), callback=self.update_count)
        self.update_button = rumps.MenuItem(title= ("{:.2f}".format(get_ram_gb_usage()) + " / " + "{:.2f}".format(mem_usage.total/(1024**3))), callback=self.update)
        self.logo_button = rumps.MenuItem(title="SimpleStatSpeed", icon=(os.path.join(basedir, "media/icon.svg")), callback=self.update_logo)
        self.open_mail = rumps.MenuItem(title="Send Mail", callback=self.mail_me)
        self.open_app_page = rumps.MenuItem(title="App Page", callback=self.go_to_app_page)
        self.stop = rumps.MenuItem(title=get_cpu_usage())
        self.menu = []
        self.sub_menu = rumps.MenuItem('View/Show')
        self.about_menu = rumps.MenuItem('About')

        self.sub_menu[0] = self.show_All_button
        self.sub_menu[1] = self.show_Cpu_button
        self.sub_menu[2] = self.show_Cpu_Ram_button
        self.sub_menu[3] = self.show_Ram_button
        self.sub_menu[4] = self.show_Network_button
        self.sub_menu[5] = self.show_Network_cpu_button
        self.sub_menu[6] = self.show_Network_ram_button

        self.about_menu[0] = self.logo_button
        self.about_menu[1] = rumps.separator
        self.about_menu[2] = "Version 1.0.1"
        self.about_menu[3] = "created by David Koenig"
        self.about_menu[4] = rumps.separator
        self.about_menu[5] = "When you need help please visit... "
        self.about_menu[6] = "... my App WebPage and contact me."
        self.about_menu[7] = rumps.separator
        self.about_menu[8] = self.open_mail
        self.about_menu[9] = self.open_app_page

        self.menu[0] = "Total Down/Up since Boot: "
        self.menu[1] = self.download_button
        self.menu[2] = self.upload_button
        self.menu[3] = rumps.separator
        self.menu[4] = "Numbers of CPU:"
        self.menu[5] = self.count_button
        self.menu[6] = rumps.separator
        self.menu[7] = "RAM Usage GB:"
        self.menu[8] = self.update_button
        self.menu[9] = rumps.separator
        self.menu[10] = self.sub_menu
        self.menu[11] = rumps.separator
        self.menu[12] = self.about_menu

    @staticmethod
    def update(sender):
        mem_usage = psutil.virtual_memory()
        run = True
        if run is True:
            get_ram_gb_usage()
            new_ram_gb_usage = get_ram_gb_usage()
            sender.title = "{:.2f}".format(new_ram_gb_usage) + " / " + "{:.2f}".format(mem_usage.total/(1024**3))

    @staticmethod
    def update_count(sender):
        run = True
        if run is True:
            new_ram_cpu_count = psutil.cpu_count()
            sender.title = "{}".format(new_ram_cpu_count) + " Pieces"

    @staticmethod
    def update_logo(sender):
        run = True
        if run is True:
            sender.title = "⚡️ SimpleStatSpeed ⚡️"

    @rumps.timer(0.5)
    def bar_menu(self, _):
        iostat = psutil.net_io_counters(pernic=False)
        upload = iostat[0]
        download = iostat[1]
        mem_usage = psutil.virtual_memory()
        ud = Foundation.NSUserDefaults.standardUserDefaults()
        run = True
        if run is True:
            ipv4 = list(get_ip_addresses(socket.AF_INET))
            interface = ipv4[1]
            info = interface[0]
            result_speed = on_calculate_speed(info)
            upload_recent = result_speed[0]
            download_recent = result_speed[1]
            get_cpu_usage()
            get_ram_perc_usage()
            get_ram_gb_usage()
            if ud.boolForKey_("showAll") == True:
                self.show_All_button.state = True
                self.show_Cpu_button.state = False
                self.show_Ram_button.state = False
                self.show_Network_button.state = False
                self.show_Cpu_Ram_button.state = False
                self.show_Network_cpu_button.state = False
                self.show_Network_ram_button.state = False
                self.title = "CPU: {}%".format(get_cpu_usage()) + "  " + "RAM: {:.1f}%".format(get_ram_perc_usage()) + " " + "{}".format(self.calculate_speedtest_unit(download_recent)) + " ↓ " + "{}".format(self.calculate_speedtest_unit(upload_recent)) + " ↑"
            elif ud.boolForKey_("showCpu") == True:
                self.show_All_button.state = False
                self.show_Cpu_button.state = True
                self.show_Ram_button.state = False
                self.show_Network_button.state = False
                self.show_Cpu_Ram_button.state = False
                self.show_Network_cpu_button.state = False
                self.show_Network_ram_button.state = False
                self.title = "CPU: {}%".format(get_cpu_usage())
            elif ud.boolForKey_("showRam") == True:
                self.show_All_button.state = False
                self.show_Cpu_button.state = False
                self.show_Ram_button.state = True
                self.show_Network_button.state = False
                self.show_Cpu_Ram_button.state = False
                self.show_Network_cpu_button.state = False
                self.show_Network_ram_button.state = False
                self.title = "RAM: {:.1f}%".format(get_ram_perc_usage())
            elif ud.boolForKey_("showRamAndCpu") == True:
                self.show_All_button.state = False
                self.show_Cpu_button.state = False
                self.show_Ram_button.state = False
                self.show_Network_button.state = False
                self.show_Cpu_Ram_button.state = True
                self.show_Network_cpu_button.state = False
                self.show_Network_ram_button.state = False
                self.title = "CPU: {}%".format(get_cpu_usage()) + "  " + "RAM: {:.1f}%".format(get_ram_perc_usage())
            elif ud.boolForKey_("showNetwork") == True:
                self.show_All_button.state = False
                self.show_Cpu_button.state = False
                self.show_Ram_button.state = False
                self.show_Network_button.state = True
                self.show_Cpu_Ram_button.state = False
                self.show_Network_cpu_button.state = False
                self.show_Network_ram_button.state = False
                self.title = "{}".format(self.calculate_speedtest_unit(download_recent)) + " ↓ " + "{}".format(self.calculate_speedtest_unit(upload_recent)) + " ↑"
            elif ud.boolForKey_("showNetworkAndCpu") == True:
                self.show_All_button.state = False
                self.show_Cpu_button.state = False
                self.show_Ram_button.state = False
                self.show_Network_button.state = False
                self.show_Cpu_Ram_button.state = False
                self.show_Network_cpu_button.state = True
                self.show_Network_ram_button.state = False
                self.title = "CPU: {}%".format(get_cpu_usage()) + "  " + "{}".format(self.calculate_speedtest_unit(download_recent)) + " ↓ " + "{}".format(
                    self.calculate_speedtest_unit(upload_recent)) + " ↑"
            elif ud.boolForKey_("showNetworkAndRam") == True:
                self.show_All_button.state = False
                self.show_Cpu_button.state = False
                self.show_Ram_button.state = False
                self.show_Network_button.state = False
                self.show_Cpu_Ram_button.state = False
                self.show_Network_cpu_button.state = False
                self.show_Network_ram_button.state = True
                self.title = "RAM: {:.1f}%".format(get_ram_perc_usage()) + "  " + "{}".format(self.calculate_speedtest_unit(download_recent)) + " ↓ " + "{}".format(
                    self.calculate_speedtest_unit(upload_recent)) + " ↑"
            else:
                self.show_All_button.state = True
                self.show_Cpu_button.state = False
                self.show_Ram_button.state = False
                self.show_Network_button.state = False
                self.show_Cpu_Ram_button.state = False
                self.show_Network_cpu_button.state = False
                self.show_Network_ram_button.state = False
                self.title = "CPU: {}%".format(get_cpu_usage()) + "  " + "RAM: {:.1f}%".format(get_ram_perc_usage()) + "  " + "{}".format(self.calculate_speedtest_unit(download_recent)) + " ↓ " + "{}".format(self.calculate_speedtest_unit(upload_recent)) + " ↑"
            self.update_button.title = "{:.2f}".format(get_ram_gb_usage()) + " / " + "{:.2f}".format(mem_usage.total/(1024**3))
            self.upload_button.title = "Upload: " + self.calculate_speed_unit(upload)
            self.download_button.title = "Download: " + self.calculate_speed_unit(download)

    def mail_me(self, _):
        print('Button Mail Me Link Clicked!')
        url = "mailto:apps@davidkoenig.de"
        webbrowser.open_new(url)

    def go_to_app_page(self, _):
        print('Button App Page Link Clicked!')
        url = "https://statspeed.davidkoenig.de"
        webbrowser.open_new(url)

    def calculate_speed_unit(self, speed: float):
        if speed <= 1000000.0:
            return "{:.2f}".format((speed / 1024.0)) + " KB"
        elif speed <= 1000000000.0:
            return "{:.2f}".format((speed / 1000024.0)) + " MB"
        elif speed >= 1000000000.0:
            return "{:.2f}".format((speed / 1000000024.0)) + " GB"
        else:
            return "{:.2f}".format(speed) + " Bytes"

    def calculate_speedtest_unit(self, speed: float):
        if speed <= 1000.0:
            return "{:.2f}".format(speed) + " KB/s"
        elif speed <= 1000000.0:
            return "{:.2f}".format((speed / 1024.0)) + " MB/s"
        elif speed >= 1000000.0:
            return "{:.2f}".format((speed / 1000024.0)) + " GB/s"
        else:
            return "{:.2f}".format(speed) + " KB/s"

    def show_All(self, sender):
        sender.state = not sender.state
        self.show_All_button.state = True
        self.show_Cpu_button.state = False
        self.show_Ram_button.state = False
        self.show_Network_button.state = False
        self.show_Cpu_Ram_button.state = False
        self.show_Network_cpu_button.state = False
        self.show_Network_ram_button.state = False
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(True, "showAll")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showRam")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetwork")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showRamAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetworkAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetworkAndRam")

    def show_Cpu(self, sender):
        sender.state = not sender.state
        self.show_All_button.state = False
        self.show_Cpu_button.state = True
        self.show_Ram_button.state = False
        self.show_Network_button.state = False
        self.show_Cpu_Ram_button.state = False
        self.show_Network_cpu_button.state = False
        self.show_Network_ram_button.state = False
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showAll")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(True, "showCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showRam")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetwork")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showRamAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetworkAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetworkAndRam")

    def show_Ram(self, sender):
        sender.state = not sender.state
        self.show_All_button.state = False
        self.show_Cpu_button.state = False
        self.show_Ram_button.state = True
        self.show_Network_button.state = False
        self.show_Cpu_Ram_button.state = False
        self.show_Network_cpu_button.state = False
        self.show_Network_ram_button.state = False
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showAll")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(True, "showRam")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetwork")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showRamAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetworkAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetworkAndRam")

    def show_Network(self, sender):
        sender.state = not sender.state
        self.show_All_button.state = False
        self.show_Cpu_button.state = False
        self.show_Ram_button.state = False
        self.show_Network_button.state = True
        self.show_Cpu_Ram_button.state = False
        self.show_Network_cpu_button.state = False
        self.show_Network_ram_button.state = False
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showAll")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showRam")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(True, "showNetwork")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showRamAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetworkAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetworkAndRam")

    def show_cpu_ram(self, sender):
        sender.state = not sender.state
        self.show_All_button.state = False
        self.show_Cpu_button.state = False
        self.show_Ram_button.state = False
        self.show_Network_button.state = False
        self.show_Cpu_Ram_button.state = True
        self.show_Network_cpu_button.state = False
        self.show_Network_ram_button.state = False
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showAll")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showRam")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetwork")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(True, "showRamAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetworkAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetworkAndRam")

    def show_cpu_network(self, sender):
        sender.state = not sender.state
        self.show_All_button.state = False
        self.show_Cpu_button.state = False
        self.show_Ram_button.state = False
        self.show_Network_button.state = False
        self.show_Cpu_Ram_button.state = False
        self.show_Network_cpu_button.state = True
        self.show_Network_ram_button.state = False
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showAll")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showRam")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetwork")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showRamAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(True, "showNetworkAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetworkAndRam")

    def show_ram_network(self, sender):
        sender.state = not sender.state
        self.show_All_button.state = False
        self.show_Cpu_button.state = False
        self.show_Ram_button.state = False
        self.show_Network_button.state = False
        self.show_Cpu_Ram_button.state = False
        self.show_Network_cpu_button.state = False
        self.show_Network_ram_button.state = True
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showAll")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showRam")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetwork")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showRamAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(False, "showNetworkAndCpu")
        Foundation.NSUserDefaults.standardUserDefaults().setBool_forKey_(True, "showNetworkAndRam")


if __name__ == '__main__':
    app = SimpleStatApp()
    app.run()
