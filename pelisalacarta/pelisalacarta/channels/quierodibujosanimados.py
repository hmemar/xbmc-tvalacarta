# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para quierodibujosanimados
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

DEBUG = config.get_setting("debug")

__category__ = "A"
__type__ = "generic"
__title__ = "Quiero dibujos animados"
__channel__ = "quierodibujosanimados"
__language__ = "ES"
__creationdate__ = "20121112"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[quierodibujosanimados.py] mainlist")
    item.url="http://www.quierodibujosanimados.com/"
    return series(item)

def series(item):
    logger.info("[quierodibujosanimados.py] series")
    itemlist = []
    
    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data,'<h4 style="margin-top:10px;">Dibujos</h4>(.*?)<h4')
    
    patron = '<a target="_top" title="([^"]+)" href="(/cat[^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)    

    for scrapedtitle,scrapedurl in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="episodios" , title=title , url=url, thumbnail=thumbnail, plot=plot, fanart="http://pelisalacarta.mimediacenter.info/fanart/quierodibujosanimados.jpg", viewmode="movie_with_plot"))        

    return itemlist

def episodios(item):
    logger.info("[quierodibujosanimados.py] episodios")

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    '''
    <h2><a   target="_self"     title="Agallas en: Todos quieren dirigir" href="/Agallas-en-Todos-quieren-dirigir/912" class="">Agallas en: Todos quieren dirigir</a></h2>
    <div class="titulo_inf">
    <a title="Agallas El perro cobarde" href="/cat/agallas-el-perro-cobarde/16" class="">Agallas El perro cobarde</a>					<div class="estrellas">			<style> 
    #stars_912 {
    background-image:url(/ico/estrellas16.png);
    background-repeat: no-repeat;
    background-position: -96px 0px;
    height:16px;
    width:80px;
    display:block;
    }
    #stars_912 span { width:8px; height:16px; display:block; float:left; }
    </style>		
    <div id="stars_912"></div>
    </div>
    </div>
    <div class="texto">
    
    <div id="foto"><a target="_self" title="Agallas en: Todos quieren dirigir" href="/Agallas-en-Todos-quieren-dirigir/912" class=""><img src="/i/thm-Todos-quieren-dirigir.jpg" /></a></div>
    
    <span class=""><p>&nbsp;En la casa de Muriel y Justo, una noche reciben una visita muy tenebrosa, Bentun Tarantela, un director de cine independiente....Muriel queda impresionada y le invita a entrar en la casa. Este director quiere hacer una pel&iacute;cula en la casa...Coraje se asusta much&iacute;simo, &iquest;Por qu&eacute;?...Cap&iacute;tulo titulado <strong>&quot;Todos quieren dirigir&quot;.</strong></p></span>					<div class="leer_mas">
    <a href="/Agallas-en-Todos-quieren-dirigir/912" class="">Ver dibujos animados</a>					</div>
    </div>
    '''
    patron  = '<h2><a[^<]+</a></h2>[^<]+'
    patron += '<div class="titulo_inf">[^<]+'
    patron += '<a[^<]+</a[^<]+<div class="estrellas"[^<]+<style[^<]+</style[^<]+'
    patron += '<div id="stars[^<]+</div>[^<]+'
    patron += '</div>[^<]+'
    patron += '</div>[^<]+'
    patron += '<div class="texto">[^<]+'
    patron += '<div id="foto"><a target="_self" title="([^"]+)" href="([^"]+)"[^<]+<img src="([^"]+)"[^<]+</a></div>[^<]+'
    patron += '<span class="">(.*?)</span>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    itemlist = []
    
    for scrapedtitle,scrapedurl,scrapedthumbnail,scrapedplot in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapertools.htmlclean(scrapedplot)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, viewmode="movie_with_plot", fanart="http://pelisalacarta.mimediacenter.info/fanart/quierodibujosanimados.jpg"))

    try:
        siguiente = scrapertools.get_match(data,"<a href='([^']+)'>Siguientes >")
        scrapedurl = urlparse.urljoin(item.url,siguiente)
        scrapedtitle = ">> Pagina Siguiente"
        scrapedthumbnail = ""
        scrapedplot = ""

        itemlist.append( Item(channel=__channel__, action="episodios", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True, fanart="http://pelisalacarta.mimediacenter.info/fanart/quierodibujosanimados.jpg") )
    except:
        pass
    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # mainlist
    mainlist_items = mainlist(Item())
    
    # Comprueba que todas las opciones tengan algo (excepto el buscador)
    for mainlist_item in mainlist_items:
        if mainlist_item.action!="search":
            exec "itemlist = "+mainlist_item.action+"(mainlist_item)"
            if len(itemlist)==0:
                mirrors = findvideos(item=itemlist[0])
                if len(mirrors)>0:
                    return True

    return False