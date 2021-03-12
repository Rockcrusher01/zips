# ============================================================
import xbmc,xbmcgui,xbmcvfs,xbmcplugin,xbmcaddon,os,shutil,sqlite3,json,urllib2,gzip,urllib,sys,codecs,pickle
from distutils.util import strtobool
from xml.dom import minidom
addon_id = 'program.RockClean'
fanart = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))

def mainMenu():
    global __addon__
    global totalSizes
    global ignore_existing_thumbs

    addItem(__addon__.getLocalizedString(30160) + " [COLOR red](" + str(totalSizes[0][1]) + __addon__.getLocalizedString(30112) + ")[/COLOR]",
            'url', 10, os.path.join(mediaPath, "cache.png"))
    addItem(__addon__.getLocalizedString(30161) + " [COLOR red](" + str(totalSizes[1][1]) + __addon__.getLocalizedString(30112) + ")[/COLOR]",
            'url', 11, os.path.join(mediaPath, "packages.png"))

    ignore_existing_thumbs = bool(strtobool(str(__addon__.getSetting('ignore_existing_thumbs').title())))

    if ignore_existing_thumbs:

        mess = __addon__.getLocalizedString(30171)
    else:
        mess = __addon__.getLocalizedString(30170)

    addItem(__addon__.getLocalizedString(30162) + " [COLOR red](" + str(totalSizes[2][1]) + __addon__.getLocalizedString(30112) + ")[/COLOR] ",
            'url', 12, os.path.join(mediaPath, "thumb.png"))

    addItem(__addon__.getLocalizedString(30100) + " [COLOR red](" + str(totalSizes[5][1]) + __addon__.getLocalizedString(30112) + ")[/COLOR]",
            'url', 14, os.path.join(mediaPath, "data.png"))

    if os.path.exists('/private/var/mobile/Library/Caches/AppleTV/Video/Other'):
        addItem(__addon__.getLocalizedString(30101) + " [COLOR red](" + str(totalSizes[6][1]) + __addon__.getLocalizedString(30112) + ")[/COLOR]",
                'url', 16, os.path.join(mediaPath, "clean.png"))

    addItem(__addon__.getLocalizedString(30004) + " [COLOR red](" + str(totalSizes[7][1]) + __addon__.getLocalizedString(30112) + ")[/COLOR]",
            'url', 17, os.path.join(mediaPath, "all.png"))

    addItem(__addon__.getLocalizedString(30185), 'url', 3, os.path.join(mediaPath, "update.png"))
        
    addItem(__addon__.getLocalizedString(30022), 'url', 5, os.path.join(mediaPath, "settings.png"))
    
    addLink(__addon__.getLocalizedString(30188), 'url', os.path.join(mediaPath, "icon.png"))


########################################forceUpdate########################################

def forceUpdate():
  dialog = xbmcgui.Dialog()
  if dialog.yesno(__addon__.getLocalizedString(30186), __addon__.getLocalizedString(30187)):
     xbmc.executebuiltin('UpdateAddonRepos()')
     xbmc.executebuiltin('UpdateLocalAddons()') 

######################################## Check Broken Sources########################################

def ProcessBrokenSources(iMode):
    global RockDebug
    global strEndMessage

    intCancel = 0
    intObjects = 0
    c = 0

    strMess = __addon__.getLocalizedString(30019)
    strMess2 = __addon__.getLocalizedString(30012)


    if iMode:
        progress = xbmcgui.DialogProgressBG()
    else:
        progress = xbmcgui.DialogProgress()

    progress.create(strMess, strMess2)

    sourcesS = ['pictures', 'music', 'video', 'files',]
    Ppaths = []

    intObjects += len(sourcesS)
    intObjects += 0.1


    for k in sourcesS:

        paths = getJson("Files.GetSources", "media", k, "sources")

        percent = (c / len(sourcesS)) * 100

        message1 = strMess + k
        message2 = strMess2 + str(int(c)) + " / " + str(int(intObjects))

        progress.update(int(percent), unicode(message1), unicode(message2))

        c += 1

        for i, jj in enumerate(paths[:]):
            if jj["file"][:9] != "addons://" and jj["file"][:6] != "rss://" and jj["file"][:6] != "ftp://" \
                and jj["file"][:7] != "sftp://" and jj["file"][:7] != "http://" and jj["file"][:10] != "videodb://" \
                and jj["file"][:10] != "musicdb://" and jj["file"][:7] != "cdda://":
                    afg = xbmc.translatePath(jj["file"])

                    if xbmcvfs.exists(afg):
                        xbmc.log("RockClean >> SOURCE PATHS (" + k.encode('utf8') +") >> " + afg.encode('utf8') + " >> ok")
                    else:
                        xbmc.log("RockClean >> SOURCE PATHS (" + k.encode('utf8') +") >> " + afg.encode('utf8') + " >> error")
                        mess1 = __addon__.getLocalizedString(30123)             # CAN NOT BE FOUND
                        strEndMessage += "[SOURCE:" + k.encode('utf8') + "] " + afg.encode('utf8') + " [B][COLOR red]" + mess1 + "[/B][/COLOR]\n"

    progress.close()

    return intCancel

########################################Define Sizes Class########################################

class Sizes():
    def __init__(self, subcat, cat, size):
        self.subcat = subcat
        self.cat = cat
        self.size = size

    def __repr__(self):
        return "%s %s %s" % (self.subcat, self.cat, self.size)

    def __str__(self):
        return "%s %s %s" % (self.subcat, self.cat, self.size)

########################################Calculate how much space would be reclaimed########################################

def CalcDeleted():
    global __addon__
    global arr
    global ignore_existing_thumbs
    global ignore_packages

    TotalfileSize = 0.0
    fileSize = 0.0

    ignore_existing_thumbs = bool(strtobool(str(__addon__.getSetting('ignore_existing_thumbs').title())))

    totSizeArr = []

    for j, entry in enumerate(arr):
        clear_cache_path = xbmc.translatePath(entry[1])

        if os.path.exists(clear_cache_path):
            anigPath = os.path.join(clear_cache_path, "animatedgifs")
            arccPath = os.path.join(xbmc.translatePath("special://temp"), "archive_cache")

            if entry[3] == 'thumbnails':
                dataBase = os.path.join(xbmc.translatePath("special://database/"), "Textures13.db")
                conn = sqlite3.connect(dataBase)
                c = conn.cursor()

            if entry[3] == 'packages' and ignore_packages > 0:
                plist = getPackages()

            for root, dirs, files in os.walk(clear_cache_path):
                if (root != anigPath and root != arccPath) or (root == anigPath):
                    for f in files:
                        try:
                            fileSize = os.path.getsize(os.path.join(root, f))
                        except Exception:
                            fileSize = 0

                        if entry[3] == 'packages' and ignore_packages > 0:
                            if f in plist:
                                TotalfileSize += fileSize

                        elif entry[3] == 'thumbnails' and ignore_existing_thumbs:
                            thumbFolder = os.path.split(root)[1]
                            thumbPath = thumbFolder + "/" + f

                            sqlstr = "SELECT * FROM texture WHERE cachedurl=" + "'" + thumbPath + "'"
                            c.execute(sqlstr)
                            data = c.fetchone()

                            if not data:
                                TotalfileSize += fileSize

                        elif entry[3] == 'addons':
                            if not entry[4]:
                                TotalfileSize += fileSize
                        else:
                            TotalfileSize += fileSize

                    if entry[2]:
                        for d in dirs:
                            if os.path.join(root, d) != anigPath and os.path.join(root, d) != arccPath:
                                TotalfileSize += getFolderSize(os.path.join(root, d))

            if entry[3] == 'thumbnails':
                conn.close()

            mess3 = " [COLOR red]%0.2f[/COLOR] " % ((TotalfileSize / (1048576.00000001)),)
            mess = entry[0] + mess3

            totSizeArr.append(Sizes(entry[0], entry[3], str(TotalfileSize)))
            TotalfileSize = 0.0

    addontot = 0.0
    custtot = 0.0
    atvtot = 0.0
    totalsize = 0.0

    msizes = []

    for i, line in enumerate(totSizeArr):
        if line.cat == 'addons':
            addontot += float(line.size)
            totalsize += addontot
        elif line.cat == 'custom':
            custtot += float(line.size)
            totalsize += custtot
        elif line.cat == 'atv':
            atvtot += float(line.size)
            totalsize += atvtot
        else:
            mess = " [COLOR red]%0.2f[/COLOR] " % ((float(line.size) / (1048576.00000001)),)
            msizes.append([line.cat, mess])
            totalsize += float(line.size)

    mess = " [COLOR red]%0.2f[/COLOR] " % ((addontot / (1048576.00000001)),)
    msizes.append(['addons', mess])

    mess = " [COLOR red]%0.2f[/COLOR] " % ((custtot / (1048576.00000001)),)
    msizes.append(['custom', mess])

    mess = " [COLOR red]%0.2f[/COLOR] " % ((atvtot / (1048576.00000001)),)
    msizes.append(['atv', mess])

    TotalfileSize = 0
    data_path = xbmc.translatePath('special://profile/addon_data/')

    installedAddons, countInstalledAddons = getLocalAddons()
    addonData, intObjects = getLocalAddonDataFolders()
    for d in addonData:
        if d not in installedAddons:
            fullName = os.path.join(data_path, d)
            TotalfileSize += getFolderSize(fullName)

    mess = " [COLOR red]%0.2f[/COLOR] " % ((TotalfileSize / (1048576.00000001)),)
    msizes.append(['emptyaddon', mess])
    totalsize += float(TotalfileSize)

    mess = " [COLOR red]%0.2f[/COLOR] " % ((totalsize / (1048576.00000001)),)
    msizes.append(['total', mess])

    for i, line in enumerate(msizes):
        xbmc.log("RockClean >> CALCULATED SAVINGS >> " + str(line).encode('utf8'))

    return msizes

########################################Change local path(s) in settings to special://########################################

def ProcessSpecial(iMode):
    global strEndMessage
    global __addon__

    __addon__.setSetting('lock', 'true')
    intCancel = 0
    intObjects = 0
    counter = 0
    intTot = 0

    strMess = __addon__.getLocalizedString(30118)
    strMess2 = __addon__.getLocalizedString(30115)

    if iMode:
        progress = xbmcgui.DialogProgressBG()
    else:
        progress = xbmcgui.DialogProgress()

    progress.create(strMess, strMess2)

    userDataPath = xbmc.translatePath("special://userdata")

    for root, dirs, files in os.walk(userDataPath):
        for f in files:
            if get_extension(f) == "xml":
                intObjects += 1

    intObjects += 0.1

    for root, dirs, files in os.walk(userDataPath):
        for f in files:
            if get_extension(f) == "xml":
                if get_filename(f) == "settings" or root == userDataPath:
                    p = os.path.join(root, f)
                    pout = os.path.join(root, f + "_NEW")

                    strMess = __addon__.getLocalizedString(30025)
                    strMess2 = __addon__.getLocalizedString(30018)

                    percent = (counter / intObjects) * 100

                    message1 = strMess + str(f)
                    message2 = strMess2 + str(int(counter)) + " / " + str(int(intObjects))

                    progress.update(int(percent), unicode(message1), unicode(message2))

                    if not iMode:
                        try:
                            if progress.iscanceled():
                                intCancel = 1
                                break
                        except Exception:
                            pass

                    fp = codecs.open(p, "r", "utf-8")

                    if os.path.isfile(pout):
                        try:
                            os.remove(pout)
                        except Exception:
                            xbmc.log("RockClean >> COULDN'T DELETE OLD _NEW FILE")

                    fpout = codecs.open(pout, "w", "utf-8")

                    wasChanged = False

                    for line in fp:
                        if userDataPath in line:
                            newline = line.replace(userDataPath, "special://userdata/")
                            newline = newline.replace("\\", "/")
                            xbmc.log("RockClean >> COMPACTING PATH: " + root.encode('utf8') + "\\" + f.encode('utf8'))
                            wasChanged = True
                        else:
                            newline = line

                        fpout.write(newline)

                    fp.close()
                    fpout.close()

                    counter += 1

                    if wasChanged:
                        intTot += 1
                        try:
                            if os.path.isfile(p + "_ORIG"):
                                os.remove(p + "_ORIG")
                            os.rename(p, p + "_ORIG")
                            os.rename(pout, p)
                            pass
                        except Exception:
                            xbmc.log("RockClean >> COULDN'T DELETE OR RENAME ORIGINAL FILE")
                    else:
                        try:
                            os.remove(pout)
                        except Exception:
                            xbmc.log("RockClean >> COULDN'T DELETE NEW FILE")

    if intTot > 0:
        strMess = __addon__.getLocalizedString(30139)
        strEndMessage = strMess + " " + str(intTot) + "\n"
    else:
        strEndMessage = __addon__.getLocalizedString(30139) + " " + __addon__.getLocalizedString(30153) + "\n"

    progress.close()

    return intCancel, intTot

########################################Clean texture database########################################

def CleanTextures(iMode):
    global __addon__
    global RockDebug
    global strEndMessage

    __addon__.setSetting('lock', 'true')
    intCancel = 0
    intObjects = 0
    counter = 0

    strMess = __addon__.getLocalizedString(30114)
    strMess2 = __addon__.getLocalizedString(30115)

    if iMode == 1:
        progress = xbmcgui.DialogProgressBG()
        progress.create(strMess, strMess2)
    elif iMode == 0:
        progress = xbmcgui.DialogProgress()
        progress.create(strMess, strMess2)

    dataBase = os.path.join(xbmc.translatePath("special://database/"), "Textures13.db")
    oldfileSize = os.path.getsize(dataBase)
    conn = sqlite3.connect(dataBase)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM texture")
    intObjects = c.fetchone()[0]
    intObjects += 0.1

    try:
        c.execute("SELECT * FROM texture")
        data = c.fetchall()
    except Exception as e:
        xbmc.log("RockClean >> SQL ERROR IN Textures13: " + str(e))
        data = None

    for d in data:
        recID = d[0]
        textureName = d[2].replace('/', os.sep)
        thumbPath = os.path.join(xbmc.translatePath("special://thumbnails"), textureName)
        fileName = xbmc.translatePath(d[1])

        strMess = __addon__.getLocalizedString(30116)
        strMess2 = __addon__.getLocalizedString(30014)

        percent = (counter / intObjects) * 100

        message1 = strMess + str(recID)
        message2 = strMess2 + str(int(counter)) + " / " + str(int(intObjects))

        if iMode < 2:
            progress.update(int(percent), unicode(message1), unicode(message2))

        if iMode == 0:
            try:
                if progress.iscanceled():
                    intCancel = 1
                    break
            except Exception:
                pass

        if not os.path.isfile(thumbPath):
            try:
                c.execute("DELETE FROM texture WHERE id=?", (recID,))
                conn.commit()

                c.execute("DELETE FROM sizes WHERE idtexture=?", (recID,))
                conn.commit()

                if RockDebug:
                    xbmc.log("RockClean >> DELETED RECORD FROM DB: " + str(thumbPath))

                counter += 1
            except Exception as e:
                xbmc.log("RockClean >> SQL ERROR IN Textures13 DELETING ID: " + str(recID) + " >> " + str(e))

        if fileName.startswith("http://") or fileName.startswith("https://") or fileName.startswith("image://") or fileName.endswith("/transform?size=thumb"):
            pass
        else:
            if not os.path.isfile(fileName):
                try:
                    c.execute("DELETE FROM texture WHERE id=?", (recID,))
                    conn.commit()

                    c.execute("DELETE FROM sizes WHERE idtexture=?", (recID,))
                    conn.commit()

                    if RockDebug:
                        xbmc.log("RockClean >> DELETED RECORD FROM DB: " + str(fileName))

                    counter += 1
                except Exception as e:
                    xbmc.log("RockClean >> SQL ERROR IN Textures13 DELETING ID: " + str(recID) + " >> " + str(e))

    conn.execute("VACUUM")
    conn.close()

    if counter > 0:
        newfileSize = os.path.getsize(dataBase)
        intTot = (oldfileSize - newfileSize) / 1048576.00000001
        strSaved = '[COLOR red]%0.2f[/COLOR]' % (intTot,)

        strMess = __addon__.getLocalizedString(30136)
        strMess2 = __addon__.getLocalizedString(30137)
        strMess3 = __addon__.getLocalizedString(30112)
        strEndMessage = strMess + " " + str(counter) + " " + strMess2 + " (" + strSaved + " " + strMess3 + ")\n"
    else:
        intTot = 0
        strEndMessage += (__addon__.getLocalizedString(30099) + "[COLOR blue: [/COLOR]")
        strEndMessage += __addon__.getLocalizedString(30152) + "\n"

    if iMode < 2:
        progress.close()

    return intCancel, intTot

########################################Textbox class########################################

def TextBoxes(heading, anounce):
    class TextBox():
        WINDOW = 10147
        CONTROL_LABEL = 1
        CONTROL_TEXTBOX = 5

        def __init__(self, *args, **kwargs):
            xbmc.executebuiltin("ActivateWindow(%d)" % (self.WINDOW,))
            self.win = xbmcgui.Window(self.WINDOW)
            xbmc.sleep(500)
            self.setControls()

        def setControls(self):
            self.win.getControl(self.CONTROL_LABEL).setLabel(heading)
            try:
                f = open(anounce)
                text = f.read()
            except Exception:
                text = anounce
            self.win.getControl(self.CONTROL_TEXTBOX).setText(text)
            return

    TextBox()

########################################Get extension########################################

def get_extension(filename):
    ext = os.path.splitext(filename)[1][1:].strip()
    return ext

########################################Get filename########################################

def get_filename(filename):
    name = os.path.splitext(filename)[0].strip()
    return name

########################################Delete Cache########################################

def DeleteFiles(cleanIt, iMode):
    global __addon__
    global arr
    global ignore_existing_thumbs
    global ignore_packages
    global strEndMessage
    global RockDebug

    __addon__.setSetting('lock', 'true')
    intCancel = 0
    intObjects = 0
    count = 0
    TotalfileSize = 0.0
    fileSize = 0.0
    intTot = 0
    grandTotal = 0

    ignore_existing_thumbs = bool(strtobool(str(__addon__.getSetting('ignore_existing_thumbs').title())))

    for j, entry in enumerate(arr):
        if entry[3] in cleanIt and not entry[4]:
            clear_cache_path = xbmc.translatePath(entry[1])
            if os.path.exists(clear_cache_path):
                for root, dirs, files in os.walk(clear_cache_path):
                    intObjects += len(files)

    strMess = __addon__.getLocalizedString(30011)
    strMess2 = __addon__.getLocalizedString(30012)

    if iMode == 1:
        progress = xbmcgui.DialogProgressBG()
        progress.create(strMess, strMess2)
    elif iMode == 0:
        progress = xbmcgui.DialogProgress()
        progress.create(strMess, strMess2)

    intObjects += 0.1

    for j, entry in enumerate(arr):
        if entry[3] in cleanIt and not entry[4]:
            clear_cache_path = xbmc.translatePath(entry[1])

            if os.path.exists(clear_cache_path):
                anigPath = os.path.join(clear_cache_path, "animatedgifs")
                arccPath = os.path.join(xbmc.translatePath("special://temp"), "archive_cache")

                if entry[3] == 'thumbnails':
                    dataBase = os.path.join(xbmc.translatePath("special://database/"), "Textures13.db")
                    conn = sqlite3.connect(dataBase)
                    c = conn.cursor()

                if entry[3] == 'packages' and ignore_packages > 0:
                    plist = getPackages()

                for root, dirs, files in os.walk(clear_cache_path):
                    if (root != anigPath and root != arccPath) or (root == anigPath):
                        for f in files:
                            strMess = __addon__.getLocalizedString(30013)
                            strMess2 = __addon__.getLocalizedString(30014)

                            percent = (count / intObjects) * 100

                            message1 = strMess + entry[0]
                            message2 = strMess2 + str(int(count)) + " / " + str(int(intObjects))

                            if iMode < 2:
                                progress.update(int(percent), unicode(message1), unicode(message2))

                            if iMode == 0:
                                try:
                                    if progress.iscanceled():
                                        intCancel = 1
                                        break
                                except Exception:
                                    pass

                            try:
                                fileSize = os.path.getsize(os.path.join(root, f))
                            except Exception:
                                fileSize = 0

                            if entry[3] == 'packages' and ignore_packages > 0:
                                if f in plist:
                                    try:
                                        os.unlink(os.path.join(root, f))
                                        TotalfileSize += fileSize
                                        if RockDebug:
                                            xbmc.log("RockClean >> DELETED >>" + f.encode('utf8'))
                                    except Exception as e:
                                        xbmc.log("RockClean >> CAN NOT DELETE FILE >>" + f.encode('utf8') + "<< ERROR: " + str(e))

                                    count += 1

                            elif entry[3] == 'thumbnails' and ignore_existing_thumbs:
                                thumbFolder = os.path.split(root)[1]
                                thumbPath = thumbFolder + "/" + f

                                sqlstr = "SELECT * FROM texture WHERE cachedurl=" + "'" + thumbPath + "'"
                                c.execute(sqlstr)
                                data = c.fetchone()

                                if not data:
                                    try:
                                        os.unlink(os.path.join(root, f))
                                        TotalfileSize += fileSize
                                        if RockDebug:
                                            xbmc.log("RockClean >> DELETED >>" + f.encode('utf8'))
                                    except Exception as e:
                                        xbmc.log("RockClean >> CAN NOT DELETE FILE >>" + f.encode('utf8') + "<< ERROR: " + str(e))

                                    count += 1

                            else:
                                try:
                                    os.unlink(os.path.join(root, f))
                                    TotalfileSize += fileSize
                                    if RockDebug:
                                        xbmc.log("RockClean >> DELETED >>" + f.encode('utf8'))
                                except Exception as e:
                                    xbmc.log("RockClean >> CAN NOT DELETE FILE >>" + f.encode('utf8') + "<< ERROR: " + str(e))

                                count += 1

                        if entry[2]:
                            for d in dirs:
                                if os.path.join(root, d) != anigPath and os.path.join(root, d) != arccPath:
                                    try:
                                        shutil.rmtree(os.path.join(root, d))
                                        if RockDebug:
                                            xbmc.log("RockClean >> DELETED >>" + d.encode('utf8'))
                                    except Exception as e:
                                        xbmc.log("RockClean >> CAN NOT DELETE FOLDER >>" + d.encode('utf8') + "<< ERROR: " + str(e))
                    else:
                        pass

                if entry[3] == 'thumbnails':
                    conn.close()

                if TotalfileSize > 0:
                    mess1 = __addon__.getLocalizedString(30113)
                    mess2 = __addon__.getLocalizedString(30112)
                    mess3 = " [COLOR red]%0.2f[/COLOR] " % ((TotalfileSize / (1048576.00000001)),)

                    mess = entry[3].title().encode('utf8') + " [COLOR blue](" + entry[0].encode('utf8') + "):[/COLOR] " + mess1 + mess3 + mess2
                    strEndMessage += (mess + "\n")

                    xbmc.log("RockClean >> CLEANING >> " + mess.encode('utf8'))
                    intTot = TotalfileSize / 1048576.00000001
                    grandTotal += TotalfileSize
                else:
                    strEndMessage += (entry[3].title().encode('utf8') + " [COLOR blue](" + entry[0].encode('utf8') + ") :[/COLOR] ")
                    strEndMessage += __addon__.getLocalizedString(30150) + "\n"

                TotalfileSize = 0.0

    if iMode < 2:
        progress.close()

    return intCancel, intTot

########################################Get All Packages########################################

def getPackages():
    global ignore_packages

    packAge = []

    clear_cache_path = xbmc.translatePath('special://home/addons/packages')
    if os.path.exists(clear_cache_path):
        for root, dirs, files in os.walk(clear_cache_path):
            for e, f in enumerate(files):
                name = os.path.splitext(f)[0]
                version = name.rsplit('-', 1)
                dt = os.path.getmtime(os.path.join(root, f))

                packAge.append([version[0], version[1], dt, f])

        uniquePackage = set()

        for e, item in enumerate(packAge):
            uniquePackage.add(packAge[e][0])

        deletePackages = []

        for item in uniquePackage:
            strVers = []
            for e, lst in enumerate(packAge):
                if packAge[e][0] == item:
                    strVers.append(packAge[e])

            strVers.sort(key=lambda date: packAge[e][2])
            strVers.reverse()

            for i, vv in enumerate(strVers):
                if i >= ignore_packages:
                    deletePackages.append(vv[3])

    return deletePackages

########################################Compact DBs########################################

def CompactDatabases(iMode):
    global __addon__
    global strEndMessage

    __addon__.setSetting('lock', 'true')
    intCancel = 0
    intObjects = 0
    counter = 0

    intTot = 0
    GreatTotal = 0

    strMess = __addon__.getLocalizedString(30016)
    strMess2 = __addon__.getLocalizedString(30012)

    if iMode == 1:
        progress = xbmcgui.DialogProgressBG()
        progress.create(strMess, strMess2)
    elif iMode == 0:
        progress = xbmcgui.DialogProgress()
        progress.create(strMess, strMess2)

    dbPath = xbmc.translatePath("special://database/")
    intObjects = 0

    if os.path.exists(dbPath):
        files = ([f for f in os.listdir(dbPath) if f.endswith('.db') and os.path.isfile(os.path.join(dbPath, f))])
        intObjects = len(files)
        intObjects += 0.1

        for f in files:
            strMess = __addon__.getLocalizedString(30017)
            strMess2 = __addon__.getLocalizedString(30018)

            percent = (counter / intObjects) * 100

            message1 = strMess + f
            message2 = strMess2 + str(int(counter)) + " / " + str(int(intObjects))

            if iMode < 2:
                progress.update(int(percent), unicode(message1), unicode(message2))

            if iMode == 0:
                try:
                    if progress.iscanceled():
                        intCancel = 1
                        break
                except Exception:
                    pass

            fileSizeBefore = os.path.getsize(os.path.join(dbPath, f))
            CompactDB(os.path.join(dbPath, f))
            fileSizeAfter = os.path.getsize(os.path.join(dbPath, f))

            xbmc.log("RockClean >> COMPACTED DATABASE >>" + f.encode('utf8'))

            if fileSizeAfter != fileSizeBefore:
                mess1 = __addon__.getLocalizedString(30110)
                mess2 = __addon__.getLocalizedString(30111)
                mess3 = " [COLOR red]%0.2f[/COLOR] " % (((fileSizeBefore - fileSizeAfter) / (1048576.00000001)),)
                mess4 = __addon__.getLocalizedString(30112)
                strEndMessage += mess1 + f.encode('utf8') + mess2 + mess3 + mess4 + "\n"

                intTot += (fileSizeBefore - fileSizeAfter) / 1048576.00000001
                GreatTotal += (fileSizeBefore - fileSizeAfter)
            counter += 1

    if iMode < 2:
        progress.close()

    if GreatTotal == 0:
        intTot = 0
        strEndMessage += __addon__.getLocalizedString(30151) + "\n"

    return intCancel, intTot

########################################Compact DB########################################

def CompactDB(SQLiteFile):
    conn = sqlite3.connect(SQLiteFile)
    conn.execute("VACUUM")
    conn.close()

########################################Get list of repositories########################################

def getLocalRepos():
    global RockDebug

    installedRepos = []
    repos = getJson("Addons.GetAddons", "type", "xbmc.addon.repository", "addons")
    for f in repos:
        installedRepos.append(f["addonid"])
        if RockDebug:
            xbmc.log("RockClean >> INSTALLED REPOS >>" + f["addonid"].encode('utf8'))

    count = len(installedRepos)

    return installedRepos, count

########################################Get list of installed addons########################################

def getLocalAddons():
    global RockDebug

    installedAddons = []
    addons = getJson("Addons.GetAddons", "type", "unknown", "addons")
    for f in addons:
        if f["type"] != "xbmc.addon.repository":
            installedAddons.append(f["addonid"])
            if RockDebug:
                xbmc.log("RockClean >> INSTALLED ADDONS >>" + f["addonid"].encode('utf8'))

    count = len(installedAddons)

    return installedAddons, count

########################################Get list of addon data folders########################################

def getLocalAddonDataFolders():
    addonData = []

    data_path = xbmc.translatePath('special://profile/addon_data/')

    for item in os.listdir(data_path):
        if os.path.isdir(os.path.join(data_path, item)):
            addonData.append(item)

    count = len(addonData)

    return addonData, count

########################################Delete data folders for nonexistant (uninstalled) addons########################################

def deleteAddonData(iMode):
    global __addon__
    global strEndMessage

    __addon__.setSetting('lock', 'true')
    intCancel = 0
    counter = 0
    TotalfileSize = 0
    deleted = 0

    strMess = __addon__.getLocalizedString(30117)
    strMess2 = __addon__.getLocalizedString(30012)

    if iMode == 1:
        progress = xbmcgui.DialogProgressBG()
        progress.create(strMess, strMess2)
    elif iMode == 0:
        progress = xbmcgui.DialogProgress()
        progress.create(strMess, strMess2)

    data_path = xbmc.translatePath('special://profile/addon_data/')

    installedAddons, countInstalledAddons = getLocalAddons()
    addonData, intObjects = getLocalAddonDataFolders()
    intObjects += 0.1

    for d in addonData:
        strMess = __addon__.getLocalizedString(30025)
        strMess2 = __addon__.getLocalizedString(30014)

        percent = (counter / intObjects) * 100

        message1 = strMess + str(d)
        message2 = strMess2 + str(int(deleted)) + " / " + str(int(intObjects))

        if iMode < 2:
            progress.update(int(percent), unicode(message1), unicode(message2))

        if iMode == 0:
            try:
                if progress.iscanceled():
                    intCancel = 1
                    break
            except Exception:
                pass

        if d not in installedAddons:
            fullName = os.path.join(data_path, d)
            TotalfileSize += getFolderSize(fullName)

            try:
                shutil.rmtree(fullName)
                xbmc.log("RockClean >> DELETING UNUSED ADDON DATA FOLDER >>" + fullName.encode('utf8'))
                deleted += 1
            except Exception as e:
                xbmc.log("RockClean >> ERROR DELETING UNUSED ADDON DATA FOLDER: " + str(e))

        counter += 1

    if TotalfileSize > 0:
        mess1 = __addon__.getLocalizedString(30113)
        mess2 = __addon__.getLocalizedString(30112)
        mess3 = " [COLOR red]%0.2f[/COLOR] " % ((TotalfileSize / (1048576.00000001)),)

        mess = __addon__.getLocalizedString(30090) + mess1 + mess3 + mess2
        strEndMessage += (mess + "\n")
    else:
        strEndMessage += (__addon__.getLocalizedString(30090) + ": ")
        strEndMessage += __addon__.getLocalizedString(30150) + "\n"

    if iMode < 2:
        progress.close()

    return intCancel, (TotalfileSize / 1048576.00000001)

########################################Get folder size########################################

def getFolderSize(folder):
    total_size = os.path.getsize(folder)

    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)

    return total_size

########################################Get Kodi data by json########################################

def getJson(method, param1, param2, retname):
    command = '''{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "%s",
    "params": {
        "%s": "%s"
        }
    }'''

    result = xbmc.executeJSONRPC(command % (method, param1, param2))
    py = json.loads(result)
    if 'result' in py and retname in py['result']:
        a = py['result'][retname]

        if RockDebug:
            xbmc.log("RockClean >> READ SYSTEM SETTING >> " + method + ":" + param1 + "."+ param2 + " >> " + str(a) )

        return a
    else:
        return ""

########################################Check Addons########################################

def ProcessAddons(iMode):
    global RockDebug
    global strEndMessage

    intCancel = 0
    intObjects = 0
    c = 0

    strMess = __addon__.getLocalizedString(30019)
    strMess2 = __addon__.getLocalizedString(30012)

    if iMode:
        progress = xbmcgui.DialogProgressBG()
    else:
        progress = xbmcgui.DialogProgress()

    progress.create(strMess, strMess2)

    repos, intObjects = getLocalRepos()
    AddonsInstalled, intObjAddons = getLocalAddons()

    intObjects += intObjAddons
    intObjects += 0.1

    strMess = __addon__.getLocalizedString(30025)
    strMess2 = __addon__.getLocalizedString(30026)

    AddonsInRepo = []

    for r in repos:
        if r == "repository.xbmc.org":
            repoxml = os.path.join(xbmc.translatePath("special://xbmc"), "addons", r, "addon.xml")
        else:
            repoxml = os.path.join(xbmc.translatePath("special://home"), "addons", r, "addon.xml")

        percent = (c / intObjects) * 100

        message1 = strMess + r
        message2 = strMess2 + str(int(c)) + " / " + str(int(intObjects))

        progress.update(int(percent), unicode(message1), unicode(message2))

        if not iMode:
            try:
                if progress.iscanceled():
                    intCancel = 1
                    break
            except Exception:
                pass

        AddonsInRepo += GetAddonsInRepo(repoxml, r)

        c += 1

    for a in AddonsInstalled:
        percent = (c / intObjects) * 100

        message1 = strMess + a
        message2 = strMess2 + str(int(c)) + " / " + str(int(intObjects))

        progress.update(int(percent), unicode(message1), unicode(message2))

        if not iMode:
            try:
                if progress.iscanceled():
                    intCancel = 1
                    break
            except Exception:
                pass

        if os.path.isdir(os.path.join(xbmc.translatePath("special://xbmc"), "addons", a)):
            continue

        if a in AddonsInRepo:
            xbmc.log("RockClean >> ADDON >> " + a.encode('utf8') + " >> FOUND")
        else:
            xbmc.log("RockClean >> ADDON >> " + a.encode('utf8') + " >> IS IN NO REPOSITORY")
            mess1 = __addon__.getLocalizedString(30122)             # IS IN NO REPOSITORY
            strEndMessage += a + " [B][COLOR red]" + mess1 + "[/B][/COLOR]\n"

        c += 1

    progress.close()

    return intCancel

########################################Check Repos########################################

def ProcessRepos(iMode):
    global RockDebug
    global strEndMessage

    intCancel = 0
    intObjects = 0
    c = 0

    strMess = __addon__.getLocalizedString(30019)
    strMess2 = __addon__.getLocalizedString(30012)

    if iMode:
        progress = xbmcgui.DialogProgressBG()
    else:
        progress = xbmcgui.DialogProgress()

    progress.create(strMess, strMess2)

    repos, intObjects = getLocalRepos()
    AddonsInstalled, intObjAddons = getLocalAddons()

    intObjects += 0.1

    for r in repos:
        if r == "repository.xbmc.org":
            repoxml = os.path.join(xbmc.translatePath("special://xbmc"), "addons", r, "addon.xml")
        else:
            repoxml = os.path.join(xbmc.translatePath("special://home"), "addons", r, "addon.xml")

        xbmc.log("RockClean >> PROCESSING REPO >>" + r.encode('utf8'))

        strMess = __addon__.getLocalizedString(30025)
        strMess2 = __addon__.getLocalizedString(30026)

        percent = (c / intObjects) * 100

        message1 = strMess + r
        message2 = strMess2 + str(int(c)) + " / " + str(int(intObjects))

        progress.update(int(percent), unicode(message1), unicode(message2))

        if not iMode:
            try:
                if progress.iscanceled():
                    intCancel = 1
                    break
            except Exception:
                pass

        AddonsInRepo = GetAddonsInRepo(repoxml, r)

        if len(AddonsInRepo) == 0:
            xbmc.log("RockClean >> REPO >> " + r + " >> " + repoxml.encode('utf8') + " >> EMPTY OR ERROR")
            mess1 = __addon__.getLocalizedString(30120)
            strEndMessage += r + " [B][COLOR red]" + mess1 + "[/B][/COLOR]\n"
        else:
            similar = []
            for tup in AddonsInstalled:
                if tup in AddonsInRepo:
                    similar.append(tup)

            if len(similar) == 0:
                xbmc.log("RockClean >> REPO >> " + r.encode('utf8') + " >> CONTAINS NO LOCAL ADDONS")
                mess1 = __addon__.getLocalizedString(30121)
                strEndMessage += r + " [B][COLOR red]" + mess1 + "[/B][/COLOR]\n"
            else:
                if RockDebug:
                    for i in similar:
                        xbmc.log("RockClean >> REPO >> " + r.encode('utf8') + " >> CONTAINS >>" + i.encode('utf8'))

        c += 1

    progress.close()

    return intCancel

########################################Get list of addons in repository########################################

def GetAddonsInRepo(netxml, repo):
    global RockDebug

    allAddonsInRepo = []

    if os.path.exists(netxml):
        if RockDebug:
            xbmc.log("RockClean >> LOCAL XML EXISTS >>" + netxml.encode('utf8'))

        repopath = getRepoPath(netxml)

        if not repopath and RockDebug:
            xbmc.log("RockClean >> INFO TAG NOT FOUND IN REPO >>" + netxml.encode('utf8'))

        for ri in repopath:
            id = getPathAddons(ri, repo)

            for addon in id:
                allAddonsInRepo.append(addon)
                if RockDebug:
                    xbmc.log("RockClean >> ADDON >>" + addon.encode('utf8'))

    else:
        if RockDebug:
            xbmc.log("RockClean >> LOCAL XML DOES NOT EXIST >>" + netxml.encode('utf8'))

    return allAddonsInRepo

########################################Get repository path(s) from xml########################################

def getRepoPath(xmlFile):
    global RockDebug

    XmlInfo = []

    xmldoc = minidom.parse(xmlFile)

    infoTag = xmldoc.getElementsByTagName("info")

    for r in infoTag:
        try:
            XmlInfo.append(r.childNodes[0].nodeValue.strip())
            if RockDebug:
                xbmc.log("RockClean >> REPO PATHS >>" + r.childNodes[0].nodeValue.encode('utf8'))
        except Exception as e:
            xbmc.log("RockClean >> ERROR REPO PATHS >>" + str(e).encode('utf-8'))

    return XmlInfo

########################################Get addons from xml########################################

def getPathAddons(xmlFile, repo):
    global RockDebug

    XmlInfo = []

    try:
        req = urllib2.Request(xmlFile)
        req.add_header('User-Agent', ' Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        httpdata = response.read()
        response.close()

    except Exception as e:
        xbmc.log("RockClean >> ERROR >>" + str(e).encode('utf-8'))
        return ""

    if get_extension(xmlFile) == "gz":
        gzFile = os.path.join(xbmc.translatePath('special://temp'), 'addon.gz')
        with open(gzFile, 'wb') as output:
            output.write(httpdata)

        f = gzip.GzipFile(gzFile, 'rb')
        httpdata = f.read()
        f.close()

    try:
        xmldoc = minidom.parseString(httpdata)
    except Exception as e:
        xbmc.log("RockClean >> ERROR PARSING REPO >> " + str(e).encode('utf-8'))
        return ""

    infoTag = xmldoc.getElementsByTagName("addon")

    for r in infoTag:
        addon = r.attributes["id"].value.strip()
        if addon != repo:
            XmlInfo.append(addon)
            if RockDebug:
                xbmc.log("RockClean >> REPO-ADDON-LIST >>" + addon)

    return XmlInfo

########################################Get settings########################################

def GetSettings():
    global RockDebug
    global RockBackgroundRun
    global RockConfirm
    global ignore_existing_thumbs
    global ignore_packages

    RockDebug = bool(strtobool(str(__addon__.getSetting('debug').title())))
    RockConfirm = bool(strtobool(str(__addon__.getSetting('confirm').title())))
    RockBackgroundRun = bool(strtobool(str(__addon__.getSetting('autoclean').title())))
    ignore_existing_thumbs = bool(strtobool(str(__addon__.getSetting('ignore_existing_thumbs').title())))

########################################Display results of cleaning########################################

def showResults():
    global __addon__
    global totalSizes

    totalSizes = CalcDeleted()
    fp = open(os.path.join(__addondir__, "shared.pkl"), "w")
    pickle.dump(totalSizes, fp)
    fp.close()

    if intCancel == 0:
        header = "[B][COLOR red]" + __addon__.getLocalizedString(30133) + "[/B][/COLOR]"
        TextBoxes(header, strEndMessage)
    elif intCancel == 1:
        strMess = __addon__.getLocalizedString(30030)
        xbmc.executebuiltin("XBMC.Notification(%s,%s,5000,%s)" % (__addonname__.encode('utf8'), strMess, __addon__.getAddonInfo('icon')))
    elif intCancel == 2:
        pass
    else:
        strMess = __addon__.getLocalizedString(30031)
        xbmc.executebuiltin("XBMC.Notification(%s,%s,2000,%s)" % (__addonname__.encode('utf8'), strMess, __addon__.getAddonInfo('icon')))

    __addon__.setSetting('lock', 'false')

    while True:
        xbmc.sleep(200)
        ActDialog = xbmcgui.getCurrentWindowDialogId()

        if ActDialog != 10147:
            break

    xbmc.sleep(100)
    xbmc.executebuiltin('Container.Refresh')
    xbmc.log("RockClean >> FINISHED")

########################################Add to menues - link########################################

def addLink(name, url, iconimage):
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({'thumb': iconimage})
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty( "Fanart_Image", fanart )
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz)
    return ok

########################################Add to menues - dir########################################

def addDir(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url.encode('utf8')) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name.encode('utf8'))
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({'thumb': iconimage})
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty( "Fanart_Image", fanart )
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

########################################Add to menues - item########################################

def addItem(name, url, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url.encode('utf8')) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name.encode('utf8'))
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({'thumb': iconimage})
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty( "Fanart_Image", fanart )
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
    return ok

########################################Parse choice########################################

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

########################################Main########################################

__addon__ = xbmcaddon.Addon(id='program.RockClean')
__addonwd__ = xbmc.translatePath(__addon__.getAddonInfo('path').decode("utf-8"))
__addondir__ = xbmc.translatePath(__addon__.getAddonInfo('profile').decode('utf8'))
__addonname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')

mediaPath = os.path.join(__addonwd__, 'media')

xbmc.log("RockClean >> STARTED VERSION %s" % (__version__))

ignore_existing_thumbs = False
ignore_packages = 0
RockDebug = False
RockBackgroundRun = False
RockConfirm = False

mess = ""
strEndMessage = ""
arr = []

GetSettings()

arr.append(['[COLOR blue]Cache[/COLOR]', 'special://home/cache', True, "cache", False])
if os.path.join(xbmc.translatePath('special://temp'), "") != os.path.join(xbmc.translatePath('special://home/cache'), ""):
    arr.append(['[COLOR blue]Clean All Tempoary Cache Files[/COLOR]', 'special://temp', True, "cache", False])
arr.append(['[COLOR blue]Clean Package Folder[/COLOR]', 'special://home/addons/packages', True, "packages", False])
arr.append(['[COLOR blue]Clean Thumbnails[/COLOR]', 'special://thumbnails', False, "thumbnails", False])

arr.append(['ADDONS (!)', '/dummy/dummy/dummy', False, "addons", False])

arr.append(['ATV', '/dummy/dummy/dummy', False, "atv", False])
if os.path.exists('/private/var/mobile/Library/Caches/AppleTV/Video/Other'):
    arr.append(['ATV', '/private/var/mobile/Library/Caches/AppleTV/Video/Other', True, "atv", False])
    arr.append(['ATV (LocalAndRental)', '/private/var/mobile/Library/Caches/AppleTV/Video/LocalAndRental', True, "atv", False])

actionToken = []
totalSizes = []

actionToken.append(["cache"])
actionToken.append(["packages"])
actionToken.append(["thumbnails"])
actionToken.append(["addons"])
actionToken.append(["custom"])
actionToken.append(["atv"])
actionToken.append(["cache", "packages", "thumbnails", "addons", "custom", "atv"])

actions = []

for act in actionToken:
    actionString = ""
    for a in act:
        actionString += a + ", "

    actions.append(__addon__.getLocalizedString(30020) + actionString[:-2])

arrMax = len(actions) + 10

actions.append(__addon__.getLocalizedString(30023))
actions.append(__addon__.getLocalizedString(30027))
actions.append(__addon__.getLocalizedString(30003))
actions.append(__addon__.getLocalizedString(30100))
actions.append(__addon__.getLocalizedString(30024))
actions.append(__addon__.getLocalizedString(30001))
actions.append(__addon__.getLocalizedString(30007))
actions.append(__addon__.getLocalizedString(30022))

strEndMessage = ""
strMess = __addon__.getLocalizedString(30021)
intCancel = 0

xbmc.log('RockClean SERVICE >> RUNNING APP...' + str(xbmcgui.Window(xbmcgui.getCurrentWindowId()).getProperty('RockClean')))

if __name__ == '__main__':
    if __addon__.getSetting('lock') == 'true':
        exit()

    params = get_params()
    url = None
    name = None
    mode = None

    try:
        url = urllib.unquote_plus(params["url"])
    except Exception:
        pass
    try:
        name = urllib.unquote_plus(params["name"])
    except Exception:
            pass
    try:
        mode = int(params["mode"])
    except Exception:
        pass

    if mode is None or url is None or len(url) < 1:
        totalSizes = CalcDeleted()
        fp = open(os.path.join(__addondir__, "shared.pkl"), "w")
        pickle.dump(totalSizes, fp)
        fp.close()
        mainMenu()

    elif mode == 1:
        fp = open(os.path.join(__addondir__, "shared.pkl"))
        totalSizes = pickle.load(fp)
        fp.close()
        CleanMenu()

    elif mode == 2:
        DatabasesMenu()

    elif mode == 3:
        forceUpdate()

    elif mode == 4:
        if RockConfirm:
            intCancel, intMbDel = DeleteFiles(actionToken[6], 0)
        else:
            dialog = xbmcgui.Dialog()

            if dialog.yesno(__addon__.getLocalizedString(30028), __addon__.getLocalizedString(30027)):
                intCancel, intMbDel = DeleteFiles(actionToken[6], 0)
            else:
                intCancel = 1

        if intCancel == 0:
            intCancel, intMbTxt = deleteAddonData(0)
        else:
            intCancel = 1

        if intCancel == 0:
            intCancel, intMbCom = CompactDatabases(0)
        else:
            intCancel = 1

        showResults()

    elif mode == 5:
        __addon__.openSettings()
        intCancel = 2
        xbmc.executebuiltin('Container.Refresh')

    elif mode == 10:
        mode -= 10
        WhatToClean = ""
        for j, entry in enumerate(arr):
            if entry[3] in actionToken[mode]:
                clear_cache_path = xbmc.translatePath(entry[1])
                if os.path.exists(clear_cache_path):
                    if entry[0][-1:] != ")":
                        WhatToClean += entry[0] + ", "

        WhatToClean = WhatToClean[:-2]

        if RockConfirm:
            intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30010), WhatToClean):
                intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
            else:
                intCancel = 1

        showResults()

    elif mode == 11:
        mode -= 10
        WhatToClean = ""
        for j, entry in enumerate(arr):
            if entry[3] in actionToken[mode]:
                clear_cache_path = xbmc.translatePath(entry[1])
                if os.path.exists(clear_cache_path):
                    if entry[0][-1:] != ")":
                        WhatToClean += entry[0] + ", "

        WhatToClean = WhatToClean[:-2]

        if RockConfirm:
            intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30010), WhatToClean):
                intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
            else:
                intCancel = 1

        showResults()

    elif mode == 12:
        mode -= 10
        WhatToClean = ""
        for j, entry in enumerate(arr):
            if entry[3] in actionToken[mode]:
                clear_cache_path = xbmc.translatePath(entry[1])
                if os.path.exists(clear_cache_path):
                    if entry[0][-1:] != ")":
                        WhatToClean += entry[0] + ", "

        WhatToClean = WhatToClean[:-2]

        if RockConfirm:
            intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30010), WhatToClean):
                intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
            else:
                intCancel = 1

        showResults()

    elif mode == 13:
        mode -= 10
        WhatToClean = ""
        for j, entry in enumerate(arr):
            if entry[3] in actionToken[mode]:
                clear_cache_path = xbmc.translatePath(entry[1])
                if os.path.exists(clear_cache_path):
                    if entry[0][-1:] != ")" and not entry[4]:
                        WhatToClean += entry[0] + ", "

        WhatToClean = WhatToClean[:-2]

        if RockConfirm:
            intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30010), WhatToClean):
                intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
            else:
                intCancel = 1

        showResults()

    elif mode == 14:
        if RockConfirm:
            intCancel, intMbTxt = deleteAddonData(0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30010), __addon__.getLocalizedString(30100)):
                intCancel, intMbTxt = deleteAddonData(0)
            else:
                intCancel = 1

        showResults()

    elif mode == 15:
        mode -= 11

        WhatToClean = ""
        for j, entry in enumerate(arr):
            if entry[3] in actionToken[mode]:
                clear_cache_path = xbmc.translatePath(entry[1])
                if os.path.exists(clear_cache_path):
                    if entry[0][-1:] != ")":
                        WhatToClean += entry[0] + ", "

        WhatToClean = WhatToClean[:-2]

        if RockConfirm:
            intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30010), WhatToClean):
                intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
            else:
                intCancel = 1

        showResults()

    elif mode == 16:
        mode -= 11

        WhatToClean = ""
        for j, entry in enumerate(arr):
            if entry[3] in actionToken[mode]:
                clear_cache_path = xbmc.translatePath(entry[1])
                if os.path.exists(clear_cache_path):
                    if entry[0][-1:] != ")":
                        WhatToClean += entry[0] + ", "

        WhatToClean = WhatToClean[:-2]

        if RockConfirm:
            intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30010), WhatToClean):
                intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
            else:
                intCancel = 1

        showResults()

    elif mode == 17:
        mode -= 11
        WhatToClean = ""
        for j, entry in enumerate(arr):
            if entry[3] in actionToken[mode]:
                clear_cache_path = xbmc.translatePath(entry[1])
                if os.path.exists(clear_cache_path):
                    if entry[0][-1:] != ")" and not entry[4]:
                        WhatToClean += entry[0] + ", "

        WhatToClean = WhatToClean + __addon__.getLocalizedString(30100)

        if RockConfirm:
            intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30010), WhatToClean):
                intCancel, intMbDel = DeleteFiles(actionToken[mode], 0)
            else:
                intCancel = 1

        if intCancel == 0:
            intCancel, intMbTxt = deleteAddonData(0)
        else:
            intCancel = 1

        showResults()

    elif mode == 20:
        if RockConfirm:
            intCancel, intMbTxt = CleanTextures(0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30010), __addon__.getLocalizedString(30002)):
                intCancel, intMbTxt = CleanTextures(0)
            else:
                intCancel = 1

        showResults()

    elif mode == 21:
        if RockConfirm:
            intCancel, intMbCom = CompactDatabases(0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30010), __addon__.getLocalizedString(30023)):
                intCancel, intMbCom = CompactDatabases(0)
            else:
                intCancel = 1

        showResults()

    elif mode == 30:
        if RockConfirm:
            intCancel = ProcessRepos(0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30028), __addon__.getLocalizedString(30024)):
                intCancel = ProcessRepos(0)
            else:
                intCancel = 1

        showResults()

    elif mode == 31:
        if RockConfirm:
            intCancel = ProcessAddons(0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30028), __addon__.getLocalizedString(30001)):
                intCancel = ProcessAddons(0)
            else:
                intCancel = 1

        showResults()

    elif mode == 32:
        if RockConfirm:
            intCancel = ProcessBrokenSources(0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30028), __addon__.getLocalizedString(30007)):
                intCancel = ProcessBrokenSources(0)
            else:
                intCancel = 1

        showResults()


    elif mode == 40:
        if RockConfirm:
            intCancel, intCnt = ProcessSpecial(0)
        else:
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__addon__.getLocalizedString(30028), __addon__.getLocalizedString(30164)):
                intCancel, intCnt = ProcessSpecial(0)
            else:
                intCancel = 1

        showResults()

    xbmc.log("RockClean >> FINISHED")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))