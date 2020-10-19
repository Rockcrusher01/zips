import xbmc,xbmcaddon,xbmcgui,xbmcplugin,urllib,urllib2,os,re,sys,datetime,shutil,resolveurl,random
from resources.libs.common_addon import Addon
import base64
from resources.libs import dom_parser

addon_id        = 'plugin.video.AllSportzRecaps'
addon           = Addon(addon_id, sys.argv)
AddonTitle      = '[COLOR red]AllSportz Recaps[/COLOR]'
selfAddon       = xbmcaddon.Addon(id=addon_id)
fanart          = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
fanarts         = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
icon            = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
updatesicon     = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'resources/media/''updates.jpg'))
nextpage        = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'resources/media/''next.png'))
baseurl         = base64 . b64decode ( b'aHR0cHM6Ly93d3cuZHJvcGJveC5jb20vcy9vY3RnN2FyMDRucmFzY2ovQWxsU3BvcnR6JTIwUmVjYXBzLnhtbD9yYXc9dHJ1ZQ==' )
DATA_FOLDER     = xbmc.translatePath(os.path.join('special://profile/addon_data/' , addon_id))
dp              = xbmcgui.DialogProgress()
ytpl            = 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId='
ytpl2           = '&maxResults=50&key=AIzaSyAd-YEOqZz9nXVzGtn3KWzYLbLaajhqIDA'
ytplpg1         = 'https://www.googleapis.com/youtube/v3/playlistItems?pageToken='
ytplpg2         = '&part=snippet&playlistId='
ytplpg3         = '&maxResults=50&key=AIzaSyAd-YEOqZz9nXVzGtn3KWzYLbLaajhqIDA'
messagetext     = base64 . b64decode ( b'aHR0cHM6Ly93d3cuZHJvcGJveC5jb20vcy92bW94cmZpOXh6MTNjZnUvaW5mby54bWw/cmF3PXRydWU=') 
dialog          = xbmcgui.Dialog()
                                                               
def GetMenu():
     popup()
     url = baseurl
     addDir('[B][COLOR red]News & Updates[/COLOR][/B]',url,6,updatesicon,fanarts)
     link=open_url(baseurl)
     match= re.compile('<item>(.+?)</item>').findall(link)
     for item in match:
         try:
            if '<channel>' in item:
                    name=re.compile('<title>(.+?)</title>').findall(item)[0]
                    iconimage=re.compile('<thumbnail>(.+?)</thumbnail>').findall(item)[0]            
                    fanart=re.compile('<fanart>(.+?)</fanart>').findall(item)[0]
                    url=re.compile('<channel>(.+?)</channel>').findall(item)[0]
                    addDir(name,url,3,iconimage,fanart)
            elif '<playlist>' in item:
                    name=re.compile('<title>(.+?)</title>').findall(item)[0]
                    iconimage=re.compile('<thumbnail>(.+?)</thumbnail>').findall(item)[0]            
                    fanart=re.compile('<fanart>(.+?)</fanart>').findall(item)[0]
                    url=re.compile('<playlist>(.+?)</playlist>').findall(item)[0]
                    addDir(name,url,8,iconimage,fanart)       
            elif '<folder>'in item:
                            data=re.compile('<title>(.+?)</title>.+?folder>(.+?)</folder>.+?thumbnail>(.+?)</thumbnail>.+?fanart>(.+?)</fanart>').findall(item)
                            for name,url,iconimage,fanart in data:
                                    addDir(name,url,1,iconimage,fanart)
            else:
                            links=re.compile('<link>(.+?)</link>').findall(item)
                            if len(links)==1:
                                    data=re.compile('<title>(.+?)</title>.+?link>(.+?)</link>.+?thumbnail>(.+?)</thumbnail>.+?fanart>(.+?)</fanart>').findall(item)
                                    lcount=len(match)
                                    for name,url,iconimage,fanart in data:
                                            if 'youtube.com/playlist' in url:
                                                    addDir(name,url,2,iconimage,fanart)
                                            else:
                                                    addLink(name,url,2,iconimage,fanart)
                            elif len(links)>1:
                                    name=re.compile('<title>(.+?)</title>').findall(item)[0]
                                    iconimage=re.compile('<thumbnail>(.+?)</thumbnail>').findall(item)[0]
                                    fanart=re.compile('<fanart>(.+?)</fanart>').findall(item)[0]
                                    addLink(name,url2,iconimage,fanart)
         except:pass
         view(link)

def popup():
        message=open_url2(messagetext)
        if len(message)>1:
                path = xbmcaddon.Addon().getAddonInfo('path')
                infofile = os.path.join(os.path.join(path,''), 'info.txt')
                r = open(infofile)
                compfile = r.read()       
                if compfile == message:pass
                else:
                        showText('[B][I][COLOR red]AllSportz Recaps Version 1.0.7[/COLOR][/I][/B]', message)
                        text_file = open(infofile, "w")
                        text_file.write(message)
                        text_file.close()
                        
def GetContent(name,url,iconimage,fanart):
        url2=url
        link=open_url(url)

        match= re.compile('<item>(.+?)</item>').findall(link)
        for item in match:
            try:
                if '<channel>' in item:
                        name=re.compile('<title>(.+?)</title>').findall(item)[0]
                        iconimage=re.compile('<thumbnail>(.+?)</thumbnail>').findall(item)[0]            
                        fanart=re.compile('<fanart>(.+?)</fanart>').findall(item)[0]
                        url=re.compile('<channel>(.+?)</channel>').findall(item)[0]
                        addDir(name,url,3,iconimage,fanart)
                if '<image>' in item:
                        name=re.compile('<title>(.+?)</title>').findall(item)[0]
                        iconimage=re.compile('<thumbnail>(.+?)</thumbnail>').findall(item)[0]            
                        fanart=re.compile('<fanart>(.+?)</fanart>').findall(item)[0]
                        url=re.compile('<image>(.+?)</image>').findall(item)[0]
                        addDir(name,iconimage,iconimage,fanart)
                elif '<playlist>' in item:
                        name=re.compile('<title>(.+?)</title>').findall(item)[0]
                        iconimage=re.compile('<thumbnail>(.+?)</thumbnail>').findall(item)[0]            
                        fanart=re.compile('<fanart>(.+?)</fanart>').findall(item)[0]
                        url=re.compile('<playlist>(.+?)</playlist>').findall(item)[0]
                        addDir(name,url,8,iconimage,fanart)
    
                elif '<folder>'in item:
                                data=re.compile('<title>(.+?)</title>.+?folder>(.+?)</folder>.+?thumbnail>(.+?)</thumbnail>.+?fanart>(.+?)</fanart>').findall(item)
                                for name,url,iconimage,fanart in data:
                                        addDir(name,url,1,iconimage,fanart)
                else:
                                links=re.compile('<link>(.+?)</link>').findall(item)
                                if len(links)==1:
                                        data=re.compile('<title>(.+?)</title>.+?link>(.+?)</link>.+?thumbnail>(.+?)</thumbnail>.+?fanart>(.+?)</fanart>').findall(item)
                                        lcount=len(match)
                                        for name,url,iconimage,fanart in data:
                                                if 'youtube.com/playlist' in url:
                                                        addDir(name,url,2,iconimage,fanart)
                                                else:
                                                        addLink(name,url,2,iconimage,fanart)
                                elif len(links)>1:
                                        name=re.compile('<title>(.+?)</title>').findall(item)[0]
                                        iconimage=re.compile('<thumbnail>(.+?)</thumbnail>').findall(item)[0]
                                        fanart=re.compile('<fanart>(.+?)</fanart>').findall(item)[0]
                                        addLink(name,url2,iconimage,fanart)
            except:pass
            view(link)

def YOUTUBE_CHANNEL(url):

	CHANNEL = RUNNER + url
	link = open_url(CHANNEL)
	patron = "<video>(.*?)</video>"
	videos = re.findall(patron,link,re.DOTALL)

	items = []
	for video in videos:
		item = {}
		item["name"] = find_single_match(video,"<name>([^<]+)</name>")
		item["url"] = base64.b64decode(b"cGx1Z2luOi8vcGx1Z2luLnZpZGVvLnlvdXR1YmUvcGxheS8/dmlkZW9faWQ9") + find_single_match(video,"<id>([^<]+)</id>")
		item["author"] = find_single_match(video,"<author>([^<]+)</author>")
		item["iconimage"] = find_single_match(video,"<iconimage>([^<]+)</iconimage>")
		item["date"] = find_single_match(video,"<date>([^<]+)</date>")
		
		addLink('[COLOR red]' + item["name"] + ' - on ' + item["date"] + '[/COLOR]',item["url"],4,item["iconimage"],fanart)

def NEW():
        message=open_url2(messagetext)
        if len(message)>1:
                path = xbmcaddon.Addon().getAddonInfo('path')
                showText('[B][I][COLOR red]AllSportz Recaps Version 1.0.7[/COLOR][/I][/B]', message)
                quit()
        
def PLAYLINK(name,url,iconimage):
	
    dp.create(AddonTitle,"[COLORred]AllSportz Recaps[/COLOR]",'[COLOR red]OPENING LINK[/COLOR]','')   
    dp.update(0)
    
    if 'youtube.com/playlist' in url:
        searchterm = url.split('list=')[1]
        ytapi = ytpl + searchterm + ytpl2
        req = urllib2.Request(ytapi)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        link = link.replace('\r','').replace('\n','').replace('  ','')     
        match=re.compile('"title": "(.+?)".+?"videoId": "(.+?)"',re.DOTALL).findall(link)
        try:
            np=re.compile('"nextPageToken": "(.+?)"').findall(link)[0]
            ytapi = ytplpg1 + np + ytplpg2 + searchterm + ytplpg3
            addDir('Next Page >>',ytapi,2,nextpage,fanart)
        except:pass
        for name,ytid in match:
            url = 'https://www.youtube.com/watch?v='+ytid
            iconimage = 'https://i.ytimg.com/vi/'+ytid+'/hqdefault.jpg'
            if not 'Private video' in name:
                if not 'Deleted video' in name:
                    addLink(name,url,2,iconimage,fanart)

    if 'https://www.googleapis.com/youtube/v3' in url:
            searchterm = re.compile('playlistId=(.+?)&maxResults').findall(url)[0]
            req = urllib2.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0')
            response = urllib2.urlopen(req)
            link=response.read()
            response.close()
            link = link.replace('\r','').replace('\n','').replace('  ','')     
            match=re.compile('"title": "(.+?)".+?"videoId": "(.+?)"',re.DOTALL).findall(link)
            try:
                    np=re.compile('"nextPageToken": "(.+?)"').findall(link)[0]
                    ytapi = ytplpg1 + np + ytplpg2 + searchterm + ytplpg3
                    addDir('Next Page >>',ytapi,2,nextpage,fanart)
            except:pass
  
            for name,ytid in match:
                    url = 'https://www.youtube.com/watch?v='+ytid
                    iconimage = 'https://i.ytimg.com/vi/'+ytid+'/hqdefault.jpg'
                    if not 'Private video' in name:
                            if not 'Deleted video' in name:
                                    addLink(name,url,2,iconimage,fanart)
   
    if resolveurl.HostedMediaFile(url).valid_url(): stream_url = resolveurl.HostedMediaFile(url).resolve()
    else: stream_url=url
    liz = xbmcgui.ListItem(name,iconImage='DefaultVideo.png', thumbnailImage=iconimage)
    liz.setPath(stream_url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
                            
def PLAYVIDEO(url):

	xbmc.Player().play(url)

def open_url(url):
    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'klopp')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        link=link.replace('\n','').replace('\r','').replace('<fanart></fanart>','<fanart>x</fanart>').replace('<thumbnail></thumbnail>','<thumbnail>x</thumbnail>').replace('<utube>','<link>https://www.youtube.com/watch?v=').replace('</utube>','</link>')#.replace('></','>x</')
        print link
        return link
    except:quit()

def open_url2(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'klopp')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        print link
        return link
 
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]                    
        return param
	
def addDir(name,url,mode,iconimage,fanart,description=''):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+str(description)+"&fanart="+urllib.quote_plus(fanart)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name, 'plot': description } )
    liz.setProperty('fanart_image', fanart)
    if 'plugin://' in url:u=url
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addLink(name, url, mode, iconimage, fanart, description=''):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+str(description)+"&fanart="+urllib.quote_plus(fanart)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setProperty('fanart_image', fanart)
    liz.setProperty("IsPlayable","true")
    if 'plugin://' in url:u=url
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    return ok
    
def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)
    
def YOUTUBE_PLAYLIST(url):

    link = open_url(url)
    match = re.compile('yt-lockup-playlist yt-lockup-grid"(.+?)<div class="yt-lockup-meta">').findall(link)
    for links in match:
        url = re.compile ('<a href="(.+?)"').findall(links)[0]
        icon = re.compile ('data-thumb="(.+?)"').findall(links)[0].replace('&amp;', '&')
        title = re.compile ('<div class="yt-lockup-content">.+?title="(.+?)"').findall(links)[0]
        title = CLEANUP(title)
        if not 'http' in url:
            url1 = 'https://www.youtube.com/' + url
            addDir("[COLOR skyblue][B]" + title + "[/B][/COLOR]",url1,8,icon,fanart)
    SET_VIEW()

def YOUTUBE_PLAYLIST_PLAY(url):

    link = open_url(url)
    match = re.compile('<li class="yt-uix-scroller-scroll-unit(.+?)<span class="vertical-align">').findall(link)
    for links in match:
        title = re.compile ('video-title="(.+?)"',re.DOTALL).findall(links)[0]
        title = CLEANUP(title)
        icon = re.compile ('url="(.+?)"',re.DOTALL).findall(links)[0].replace('&amp;', '&')
        fanart = re.compile ('url="(.+?)"',re.DOTALL).findall(links)[0].replace('&amp;', '&')
        url = re.compile ('<a href="(.+?)"').findall(links)[0]
        if not 'http' in url:
            if not 'Deleted video' in title:
                url1 = 'https://www.youtube.com' + url
                addLink("[COLOR yellow][B]" + title + "[/B][/COLOR]",url1,2,icon,fanart)
                
def showText(heading, text):

    id = 10147
    xbmc.executebuiltin('ActivateWindow(%d)' % id)
    xbmc.sleep(500)
    win = xbmcgui.Window(id)
    retry = 50
    while (retry > 0):
        try:
            xbmc.sleep(6)
            retry -= 1
            win.getControl(1).setLabel(heading)
            win.getControl(5).setText(text)
            quit()
            return
        except: pass
        
def view(link):
        try:
                match= re.compile('<layouttype>(.+?)</layouttype>').findall(link)[0]
                if layout=='thumbnail': xbmc.executebuiltin('Container.SetViewMode(500)')              
                else:xbmc.executebuiltin('Container.SetViewMode(500)')  
        except:pass

params=get_params(); url=None; name=None; mode=None; site=None; iconimage=None
try: site=urllib.unquote_plus(params["site"])
except: pass
try: url=urllib.unquote_plus(params["url"])
except: pass
try: name=urllib.unquote_plus(params["name"])
except: pass
try: mode=int(params["mode"])
except: pass
try: iconimage=urllib.unquote_plus(params["iconimage"])
except: pass
try: fanart=urllib.unquote_plus(params["fanart"])
except: pass
 
if mode==None or url==None or len(url)<1: GetMenu()
elif mode==1:GetContent(name,url,iconimage,fanart)
elif mode==2:PLAYLINK(name,url,iconimage)
elif mode==3:YOUTUBE_CHANNEL(url)
elif mode==4:PLAYVIDEO(url)
elif mode==6:NEW()
elif mode==7:YOUTUBE_PLAYLIST(url)
elif mode==8:YOUTUBE_PLAYLIST_PLAY(url) #10
elif mode==9:YOUTUBE_CHANNEL(url) #11
elif mode==10:YOUTUBE_CHANNEL_PART2(url) #12
xbmcplugin.endOfDirectory(int(sys.argv[1]))
