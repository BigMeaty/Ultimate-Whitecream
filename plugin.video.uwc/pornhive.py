import urllib, urllib2, re, cookielib, os.path, sys, socket
import xbmc, xbmcplugin, xbmcgui, xbmcaddon

import utils

from jsbeautifier import beautify

progress = utils.progress

def PHMain():
    utils.addDir('[COLOR yellow]Categories[/COLOR]','http://www.pornhive.tv/en/movies/all',73,'','')
    PHList('http://www.pornhive.tv/en/movies/all')
    xbmcplugin.endOfDirectory(utils.addon_handle)



def PHList(url):
    listhtml = utils.getHtml(url, '')
    match = re.compile('panel-img">.*?<a href="([^"]+)" title="([^"]+)".*?src="([^"]+)"', re.DOTALL | re.IGNORECASE).findall(listhtml)
    for videopage, name, img in match:
        utils.addDownLink(name, videopage, 72, img, '')
    try:
        nextp=re.compile('<a href="([^"]+)">Next', re.DOTALL | re.IGNORECASE).findall(listhtml)
        utils.addDir('Next Page', nextp[0],71,'')
    except: pass
    xbmcplugin.endOfDirectory(utils.addon_handle)
    
    
def PHCat(url):
    cathtml = utils.getHtml(url, '')
    match = re.compile('<ul class="dropdown-menu my-drop">(.*?)</ul>', re.DOTALL | re.IGNORECASE).findall(cathtml)
    match1 = re.compile('href="([^"]+)[^>]+>([^<]+)<', re.DOTALL | re.IGNORECASE).findall(match[0])
    for catpage, name in match1:
        utils.addDir(name, catpage, 71, '')
    xbmcplugin.endOfDirectory(utils.addon_handle)   


def PHVideo(url, name):
    progress.create('Play video', 'Searching videofile.')
    progress.update( 10, "", "Loading video page", "" )
    videopage = utils.getHtml(url, '')
    match = re.compile(r'<li id="link-([^"]+).*?xs-12">\s+Watch it on ([\w]+)', re.DOTALL | re.IGNORECASE).findall(videopage)
    if len(match) > 1:
        sites = []
        for videourl, site in match:
            sites.append(site)
        site = utils.dialog.select('Select video site', sites)
        sitename = match[site][1]
        siteurl = match[site][0]
    else:
        sitename = match[0][1]
        siteurl = match[0][0]
    outurl = "http://www.pornhive.tv/en/out/" + siteurl
    progress.update( 20, "", "Getting video page", "" )
    if sitename == "StreamCloud":
        progress.update( 30, "", "Getting StreamCloud", "" )
        playurl = getStreamCloud(outurl)
    elif sitename == "FlashX":
        progress.update( 30, "", "Getting FlashX", "" )
        playurl = getFlashX(outurl)
    progress.update( 90, "", "Playing video", "" )
    iconimage = xbmc.getInfoImage("ListItem.Thumb")
    listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    listitem.setInfo('video', {'Title': name, 'Genre': 'Porn'})
    xbmc.Player().play(playurl, listitem)
    
def getFlashX(url):
    phpage = utils.getHtml(url, '')
    progress.update( 50, "", "Opening FlashX page", "" )
    flashxurl = re.compile('<iframe src="([^"]+)"', re.DOTALL | re.IGNORECASE).findall(phpage)
    flashxsrc = utils.getHtml2(flashxurl[0])
    progress.update( 70, "", "Grabbing video file", "" )
    flashxjs = re.compile("<script type='text/javascript'>([^<]+)</sc", re.DOTALL | re.IGNORECASE).findall(flashxsrc)
    flashxujs = beautify(flashxjs[0])
    videourl = re.compile(r',.*file: "([^"]+)".*\}\],', re.DOTALL | re.IGNORECASE).findall(flashxujs)
    progress.update( 80, "", "Returning video file", "" )
    videourl = videourl[0]
    return videourl
    

def getStreamCloud(url):
    progress.update( 40, "", "Opening Streamcloud", "" )
    scpage = utils.getVideoLink(url, '')
    progress.update( 50, "", "Getting Streamcloud page", "" )
    schtml = utils.postHtml(scpage)
    form_values = {}
    match = re.compile('<input.*?name="(.*?)".*?value="(.*?)">', re.DOTALL | re.IGNORECASE).findall(schtml)
    for name, value in match:
        form_values[name] = value.replace("download1","download2")
    progress.update( 60, "", "Grabbing video file", "" )    
    newscpage = utils.postHtml(scpage, form_data=form_values)
    videourl = re.compile('file: "(.+?)",', re.DOTALL | re.IGNORECASE).findall(newscpage)
    progress.update( 80, "", "Returning video file", "" )  
    return videourl[0]