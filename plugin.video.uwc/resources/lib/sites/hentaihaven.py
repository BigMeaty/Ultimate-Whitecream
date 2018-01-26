'''
    Ultimate Whitecream
    Copyright (C) 2016 Whitecream

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
import base64

import xbmcplugin
from resources.lib import utils


headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Encoding': 'gzip',
       'Accept-Language': 'en-US,en;q=0.5'}


@utils.url_dispatcher.register('460')
def Main():
    utils.addDir('[COLOR hotpink]Categories[/COLOR]','http://hentaihaven.org/pick-your-poison/',463,'','')
    utils.addDir('[COLOR hotpink]A to Z[/COLOR]','http://hentaihaven.org/pick-your-series/',464,'','')
    utils.addDir('[COLOR hotpink]Uncensored[/COLOR]','http://hentaihaven.org/ajax.php?action=pukka_infinite_scroll&page_no=1&grid_params=infinite_scroll=on&infinite_page=2&infinite_more=true&current_page=taxonomy&front_page_cats=&inner_grid%5Buse_inner_grid%5D=on&inner_grid%5Btax%5D=post_tag&inner_grid%5Bterm_id%5D=53&inner_grid%5Bdate%5D=&search_query=&tdo_tag=uncensored&sort=date',461,'','')
    List('http://hentaihaven.org/ajax.php?action=pukka_infinite_scroll&page_no=1&grid_params=infinite_scroll=on')
    xbmcplugin.endOfDirectory(utils.addon_handle)


@utils.url_dispatcher.register('461', ['url'])
def List(url):
    try:
        listhtml = get_hh_html(url, '')
    except:
        return None
    listhtml = listhtml.replace('\\','')
    match1 = re.compile('<a\s+class="thumbnail-image" href="([^"]+)".*?data-src="([^"]+)"(.*?)<h3>[^>]+>([^<]+)<', re.DOTALL | re.IGNORECASE).findall(listhtml)
    for videopage, img, other, name in match1:
        name = utils.cleantext(name)
        if 'uncensored' in other:
            name = name + " [COLOR hotpink]Uncensored[/COLOR]"        
        utils.addDownLink(name, videopage, 462, img, '')
    try:
        page = re.compile('page_no=(\d+)', re.DOTALL | re.IGNORECASE).findall(url)[0]
        page = int(page)
        npage = page + 1
        maxpages = re.compile(r'max_num_pages":(\d+)', re.DOTALL | re.IGNORECASE).findall(listhtml)[0]
        if int(maxpages) > page:
            nextp = url.replace("no="+str(page),"no="+str(npage))
            utils.addDir('Next Page ('+str(npage)+')', nextp,461,'')
    except: pass
    xbmcplugin.endOfDirectory(utils.addon_handle)


@utils.url_dispatcher.register('462', ['url', 'name'], ['download'])
def Playvid(url, name, download=None):
    videopage = get_hh_html(url)
    if "<source" in videopage:
        videourl = re.compile('<source.*?src="([^"]+)"', re.DOTALL | re.IGNORECASE).findall(videopage)[0]
    else:
        videourl = re.compile('class="btn btn-1 btn-1e" href="([^"]+)" target="_blank"', re.DOTALL | re.IGNORECASE).findall(videopage)[0]
    if videourl:
        utils.playvid(videourl, name, download)
    else:
        utils.notify('Oh oh','Couldn\'t find a video')


@utils.url_dispatcher.register('463', ['url'])
def Categories(url):
    cathtml = get_hh_html(url, '')
    match = re.compile('/tag/([^/]+)/" cla[^>]+>([^<]+)<', re.DOTALL | re.IGNORECASE).findall(cathtml)
    for catpage, name in match:
        catpage = "http://hentaihaven.org/ajax.php?action=pukka_infinite_scroll&page_no=1&grid_params=infinite_scroll=on&infinite_page=2&infinite_more=true&current_page=taxonomy&front_page_cats=&inner_grid%5Buse_inner_grid%5D=on&inner_grid%5Btax%5D=post_tag&inner_grid%5Bterm_id%5D=53&inner_grid%5Bdate%5D=&search_query=&tdo_tag=" + catpage + "&sort=date" 
        utils.addDir(name, catpage, 461, '')    
    xbmcplugin.endOfDirectory(utils.addon_handle)


@utils.url_dispatcher.register('464', ['url'])
def A2Z(url):
    cathtml = get_hh_html(url, '')
    match = re.compile(r'class="cat_section"><a\s+href="([^"]+)"[^>]+>([^<]+)<.*?src="([^"]+)"(.*?)</div>', re.DOTALL | re.IGNORECASE).findall(cathtml)
    for catpage, name, img, other in match:
        if 'uncensored' in other:
            name = name + " [COLOR hotpink]Uncensored[/COLOR]"
        utils.addDir(name, catpage, 461, img)    
    xbmcplugin.endOfDirectory(utils.addon_handle)


def sucuri(html):
    self.cookie = None
    s = re.compile("S\s*=\s*'([^']+)").findall(html)[0]
    s = base64.b64decode(s)
    s = s.replace(' ', '')
    s = re.sub('String\.fromCharCode\(([^)]+)\)', r'chr(\1)', s)
    s = re.sub('\.slice\((\d+),(\d+)\)', r'[\1:\2]', s)
    s = re.sub('\.charAt\(([^)]+)\)', r'[\1]', s)
    s = re.sub('\.substr\((\d+),(\d+)\)', r'[\1:\1+\2]', s)
    s = re.sub(';location.reload\(\);', '', s)
    s = re.sub(r'\n', '', s)
    s = re.sub(r'document\.cookie', 'cookie', s)
    cookie = '' ; exec(s)
    self.cookie = re.compile('([^=]+)=(.*)').findall(cookie)[0]
    self.cookie = '%s=%s' % (self.cookie[0], self.cookie[1])
    return self.cookie

def get_hh_html(url, referer='', hdr=headers, NoCookie=None, data=None):
    html = utils.getHtml(url, referer, hdr, NoCookie, data)
    if 'sucuri_cloudproxy_js' in html:
        cookie = sucuri(html)
        headers.update({'Referer': url, 'Cookie': cookie})
        html = utils.getHtml(url, referer='', hdr=headers)
    return html
