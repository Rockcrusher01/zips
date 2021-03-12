
import time,xbmc,xbmcaddon,os
from distutils.util import strtobool
from clean import DeleteFiles
from clean import CompactDatabases
from clean import CleanTextures
from clean import deleteAddonData

class SettingMonitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)

    def onSettingsChanged(self):
        GetSetting()

def GetSetting():
    global RockBackgroundRun
    global lastrundays

    __addon__ = xbmcaddon.Addon(id='program.RockClean')

    RockBackgroundRun = bool(strtobool(str(__addon__.getSetting('autoclean').title())))

    auto_interval = int(__addon__.getSetting('auto_interval'))

    if auto_interval == 0:
        lastrundays = 1
    elif auto_interval == 1:
        lastrundays = 7
    elif auto_interval == 2:
        lastrundays = 30
    elif auto_interval == 3:
        lastrundays = 90
    else:
        lastrundays = 0

    xbmc.log('RockClean SERVICE >> SETTINGS CHANGED >> SERVICE RUN: ' + str(RockBackgroundRun))
    xbmc.log('RockClean SERVICE >> SETTINGS CHANGED >> RUN EVERY DAYS: ' + str(lastrundays))

def AutoClean():
    global __addon__
    global __addonname__

    intMbDel = 0
    intMbCom = 0
    intMbTxt = 0
    intMbAdn = 0

    auto_cache = bool(strtobool(str(__addon__.getSetting('auto_cache').title())))
    auto_packages = bool(strtobool(str(__addon__.getSetting('auto_packages').title())))
    auto_thumbnails = bool(strtobool(str(__addon__.getSetting('auto_thumbnails').title())))
    auto_addons = bool(strtobool(str(__addon__.getSetting('auto_addons').title())))
    auto_compact = bool(strtobool(str(__addon__.getSetting('auto_compact').title())))
    auto_textures = bool(strtobool(str(__addon__.getSetting('auto_textures').title())))
    auto_userdata = bool(strtobool(str(__addon__.getSetting('auto_userdata').title())))
    auto_notification = int(__addon__.getSetting('auto_notification'))

    if auto_notification == 0:
        a_progress = 1
        a_notif = 1
    elif auto_notification == 1:
        a_progress = 1
        a_notif = 0
    elif auto_notification == 2:
        a_progress = 2
        a_notif = 1
    elif auto_notification == 3:
        a_progress = 2
        a_notif = 0

    actionToken = []

    if auto_cache:
        actionToken.append("cache")
    if auto_packages:
        actionToken.append("packages")
    if auto_thumbnails:
        actionToken.append("thumbnails")
    if auto_addons:
        actionToken.append("addons")

    if os.path.exists('/private/var/mobile/Library/Caches/AppleTV/Video/Other'):
        actionToken.append("atv")

    intC, intMbDel = DeleteFiles(actionToken, a_progress)

    if auto_textures:
        intC, intMbTxt = CleanTextures(a_progress)

    if auto_compact:
        intC, intMbCom = CompactDatabases(a_progress)

    if auto_userdata:
        intC, intMbAdn = deleteAddonData(a_progress)

    intMbTot = intMbDel + intMbCom + intMbTxt + intMbAdn
    mess = __addon__.getLocalizedString(30112)
    mess2 = " [COLOR red](%0.2f %s)[/COLOR]" % (intMbTot, mess,)
    strMess = __addon__.getLocalizedString(30031) + mess2

    if a_notif == 1:
        xbmc.executebuiltin("XBMC.Notification(%s,%s,5000,%s)" % (__addonname__.encode('utf8'), strMess, __addon__.getAddonInfo('icon')))

__addon__ = xbmcaddon.Addon(id='program.RockClean')
__addonwd__ = xbmc.translatePath(__addon__.getAddonInfo('path').decode("utf-8"))
__addondir__ = xbmc.translatePath(__addon__.getAddonInfo('profile').decode('utf8'))
__addonname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')

RockBackgroundRun = False
lastrundays = 0

__addon__.setSetting('lock', 'false')

if __name__ == '__main__':
    xbmc.log("RockClean SERVICE >> STARTED VERSION %s" % (__version__))

    RockBackgroundRun = bool(strtobool(str(__addon__.getSetting('autoclean').title())))

    auto_lastrun = __addon__.getSetting('auto_lastrun')
    date_now = int(round(time.time()))

    if auto_lastrun != "":
        date_auto_lastrun = int(auto_lastrun)
        time_difference = date_now - date_auto_lastrun
        time_difference_days = int(time_difference) / 86400
    else:
        __addon__.setSetting('auto_lastrun', str(int(date_now - 31536000)))
        date_auto_lastrun = 365
        time_difference_days = 365

    auto_interval = int(__addon__.getSetting('auto_interval'))

    if auto_interval == 0:
        lastrundays = 1
    elif auto_interval == 1:
        lastrundays = 7
    elif auto_interval == 2:
        lastrundays = 30
    elif auto_interval == 3:
        lastrundays = 90
    else:
        lastrundays = 0

    autostart_delay = int(__addon__.getSetting('autostart_delay'))

    if RockBackgroundRun:
        xbmc.log("RockClean SERVICE >> SERVICE INIT >> LAST RUN " + str(time_difference_days) + " DAYS AGO, SET TO RUN EVERY " + str(lastrundays) + " DAYS, WITH DELAY OF " + str(autostart_delay) + " MINUTE(S)")

        if time_difference_days > lastrundays or lastrundays == 0:
            xbmc.sleep(autostart_delay * 60000)

            if __addon__.getSetting('lock') != 'true':
                __addon__.setSetting('lock', 'true')
                xbmc.log('RockClean SERVICE >> RUNNING AUTO...')
                AutoClean()
                __addon__.setSetting('auto_lastrun', str(int(round(time.time()))))
                __addon__.setSetting('lock', 'false')
    else:
        xbmc.log("RockClean SERVICE >> SERVICE OFF")

    monitor = xbmc.Monitor()
    monsettings = SettingMonitor()

    iCounter = 0

    while True:
        if monitor.waitForAbort(2):
            xbmc.log('RockClean SERVICE >> EXIT')
            break
        else:
            if RockBackgroundRun:
                iCounter += 1

                if iCounter > 1800:
                    iCounter = 0
                    date_now = int(round(time.time()))
                    time_difference = date_now - date_auto_lastrun
                    time_difference_days = int(time_difference) / 86400

                    xbmc.log("RockClean SERVICE >> LAST RUN " + str(time_difference_days) + " DAYS AGO, SET TO RUN EVERY " + str(lastrundays) + " DAYS (NOW: " + str(date_now) + ")")

                    if time_difference_days > lastrundays:
                        if __addon__.getSetting('lock') != 'true':
                            __addon__.setSetting('lock', 'true')
                            xbmc.log('RockClean SERVICE >> RUNNING AUTO...')
                            AutoClean()
                            date_auto_lastrun = int(round(time.time()))
                            __addon__.setSetting('auto_lastrun', str(date_auto_lastrun))
                            __addon__.setSetting('lock', 'false')
                            xbmc.log('RockClean SERVICE >> END AUTO...')
                            
# Original code by D. Lanik forked and modified by Rock.#