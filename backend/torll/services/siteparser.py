import lxml.html
import re
import siteconfig
import myconfig
import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "torcp2"))
from torcp.tmdbparser import TMDbNameParser
from datetime import datetime
from urllib.parse import urlparse
import requests as pyrequests
from http.cookies import SimpleCookie
from loguru import logger
from humanbytes import parseSizeStr
from models import db, TorrentCache, PtSite, SiteTorrent
from utils import tryint, tryFloat, nomalizeSitename, getfulllink, removePasskeyUrl


GENRE_IDS = {
    28: "动作",
    12: "冒险",
    16: "动画",
    35: "喜剧",
    80: "犯罪",
    99: "纪录",
    18: "剧情",
    10751: "家庭",
    14: "奇幻",
    36: "历史",
    27: "恐怖",
    10402: "音乐",
    9648: "悬疑",
    10749: "爱情",
    878: "科幻",
    10770: "电视电影",
    53: "惊悚",
    10752: "战争",
    37: "西部",
    10759: "动作冒险",
    10762: "儿童",
    10763: "新闻",
    10764: "真人秀",
    10765: "科幻奇幻",
    10766: "肥皂剧",
    10767: "脱口秀",
    10768: "战争政治",
}


def genreid2str(idlist):
    genrestr = ""
    if idlist:
        for x in idlist:
            xi = tryint(x)
            if xi in GENRE_IDS:
                genrestr += GENRE_IDS[xi] + " "
    return genrestr


def parseMediaSource(tortitle):
    if re.search(r"remux", tortitle, re.I):
        return "remux"
    if re.search(r"(web-?dl|web-?rip|hdtv|\bweb\b)", tortitle, re.I):
        return "webdl"
    if re.search(r"(encode|x265|x264)", tortitle, re.I):
        return "encode"
    if re.search(r"\b(blu-?ray|uhd|bdmv|BDRip)\b", tortitle, re.I):
        return "bluray"
    if re.search(r"\b(dvdr|dvdrip|NTSC|DVD|DVDISO)\b", tortitle, re.I):
        return "dvd"
    if re.search(r"(AVC.*DTS|MPEG.*AVC)", tortitle, re.I):
        return "bluray"
    # logger.info('unknow type: '+tortitle)
    return "other"


def subsubtitle(title, subtitle):
    title = re.sub(r" +", " ", title).strip()
    subtitle = re.sub(r" +", " ", subtitle).strip()
    if len(title) > len(subtitle):
        # if title.startswith(subtitle):
        #     return title.replace(subtitle, ''), subtitle
        # else:
        #     return title, subtitle
        return title, subtitle
    elif title == subtitle:
        s = re.sub(r"^[ -~‘’×]+", "", subtitle).strip()
        if len(title) - len(s) > 3:
            return title.replace(s, ""), s
        else:
            return title, subtitle
    else:
        return title, subtitle.replace(title, "")


def striptitle(titlestr):
    s = re.sub(r"\[?限时禁转\]?", "", titlestr)
    s = re.sub(r"\[\W*\]$", "", s)
    return s


def striptag(titlestr):
    s = titlestr.replace("\n", "").strip()
    # s = re.sub(r'\[?(国语|中字|官方|禁转|原创)\]?', '', s)
    s = re.sub(r"剩余时间.*?\d分钟", "", s)
    s = re.sub(r"\[?Checked by \w+\]?", "", s)
    s = re.sub(r"\[\W*\]$", "", s)  # frds
    return s


def sitecat2tmdbcat(sitecat):
    m = re.search(r"TV|Series", sitecat)
    return "tv" if m else "movie"


def getSiteName(url):
    hostnameList = urlparse(url).netloc.split(".")
    if len(hostnameList) == 2:
        sitename = hostnameList[0]
    elif len(hostnameList) == 3:
        sitename = hostnameList[1]
    else:
        sitename = ""
    return sitename


def getAbbrevSiteName(url):
    sitename = getSiteName(url)
    return nomalizeSitename(sitename)


def strip_scheme_domain(url):
    parsed = urlparse(url)
    scheme_domain = f"{parsed.scheme}://{parsed.netloc}/"
    return parsed.geturl().replace(scheme_domain, "", 1)


def requestSitePage(pageUrl, pageCookie):
    logger.info(f"请求页面: {pageUrl}")
    cookie = SimpleCookie()
    cookie.load(pageCookie)
    cookies = {k: v.value for k, v in cookie.items()}
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78",
        "Content-Type": "text/html; charset=UTF-8",
    }

    try:
        r = pyrequests.get(pageUrl, headers=headers, cookies=cookies, timeout=15)
        # print(r.encoding, r.apparent_encoding)
        # utf-8 Windows-1254
        # 'ISO-8859-1' utf-8
        r.encoding = "utf-8"
        # r.encoding = r.apparent_encoding
    except:
        logger.warning(f"请求页面失败: {pageUrl}")
        return None
    return r


def cutExtitle(subtitle):
    m = re.search(r"Season\s*\d+|第(\w+)季|第(\w+)集", subtitle, re.I)
    if m:
        subtitle = subtitle[: m.span(0)[0]]

    if m := re.search(r"^\[\w+\]", subtitle, re.I):
        subtitle = subtitle[m.span(0)[1] :].strip()
    return subtitle


def fillDetailWithSiteDetailPage(detail, sitename, detailLink, cookie):
    if cookie:
        r = requestSitePage(detailLink, cookie)
        if r:
            doc = r.text
            tordetail = parseDetailInfo(detail, sitename, doc)
            return tordetail
        logger.error(f"取站点页面出错：{detailLink}")
    return None


def parseDetailInfo(tordetail, sitename, doc):
    if m := re.search(r"www\.imdb\.com\/title\/(tt\d+)", doc, flags=re.A):
        tordetail.imdbstr = m[1]

    if m := re.search(r"douban\.com\/subject\/(\d+)", doc, flags=re.A):
        tordetail.doubanid = m[1]
    cursite = siteconfig.getSiteConfig(sitename)
    if cursite:
        parser = lxml.html.HTMLParser(recover=True, encoding="utf-8")
        htmltree = lxml.html.fromstring(doc, parser=parser)
        # ele = xpathGetElement(htmltree, cursite, 'detailTitle')
        # tordetail.media_title = ele if ele else ''

        ele = xpathGetElement(htmltree, cursite, "detailSubtitle")
        tordetail.subtitle = ele[0] if ele else ""

        slnum = xpathGetElement(htmltree, cursite, "detailSeeders")
        if m := re.search(r"(\d+)个做种者[^\d]+(\d+)个下载者", slnum):
            tordetail.seednum = m[1]
            tordetail.downnum = m[2]

        basicinfo = xpathGetElement(htmltree, cursite, "detailBasicInfo")
        # basicinfo = ''.join(basicinfolist)
        if m := re.search(r"\b大小[^\d]+([\d\.]+\s*[KMGT]B)", basicinfo):
            tordetail.sizestr = m[1]
        # TODO: 各站可以自己定义了 综艺，音乐等分类
        # if m := re.search(r'\b类型:\s*(\w+)', basicinfo):
        #     tordetail.tmdbtype = sitecat2tmdbcat(m[1])
        # if m := re.search(r'\b媒介:\s*([\w\-() ]+)', basicinfo):
        #     tordetail.mediasource = m[1]
        # if m := re.search(r'\b编码:\s*([\w\-\.()]+)', basicinfo):
        #     tordetail.videocodec = m[1]
        # if m := re.search(r'\b音频编码:\s*([\w\-.]+)', basicinfo):
        #     tordetail.audiocodec = m[1]
        # if m := re.search(r'\b分辨率:\s*(\w+)', basicinfo):
        #     tordetail.resolution = m[1]
        # if m := re.search(r'\b制作组:\s*(\w+)', basicinfo):
        #     tordetail.group = m[1]
        # TODO: 页面中的 季: 4   集: 10 不准
        # if m := re.search(r'季:\s*(\d+)\s+集:\s*(\d+)', basicinfo):
        #     tordetail.season = m[1]
        #     tordetail.episode = m[2]
    else:
        logger.warning(f"解析详情页但 site {sitename} 没配置")

    if m := re.search(r"(产\s*地|国家/地区|制\s*片)\s+(\w+)\b", doc):
        tordetail.area = m[2]
    if mtitle := re.search(r"片\s*名\s+([^\<\r\n]+)", doc):
        tordetail.extitle = mtitle[1]
    if m := re.search(r"译\s*名\s+([^/\r\n\<]+)$", doc):
        tordetail.title_translation = m[1]
    # 无片名，有译名时，覆盖原来名字解析出的 extitle
    if tordetail.title_translation and not mtitle:
        tordetail.extitle = tordetail.title_translation

    tordetail.extitle = cutExtitle(tordetail.extitle)

    if m := re.search(r"年\s*代\s+(\d+)", doc):
        tordetail.year_int = tryint(m[1])
    if m := re.search(r"集\s*数\s+(\d+)", doc):
        tordetail.epnum = m[1]
    if m := re.search(r"上映日期\s+([^</]+)", doc):
        tordetail.pubdate = m[1]
        if tordetail.year_int and (tordetail.year_int < 1900):
            if m1 := re.search(r"(\d{4})-\d{2}"):
                tordetail.year_int = tryint(m1[1])

    tordetail.imdbval, tordetail.doubanval = parseInfoPageIMDbval(doc)
    logger.info(
        f"取得 IMDb {tordetail.imdbstr}, 辅助片名: {tordetail.extitle}, 地区: {tordetail.area}, "
        + f"imdb分: {tordetail.imdbval}, douban分: {tordetail.doubanval}, "
        + f"年代: {tordetail.year_int}, 作种人数: {tordetail.seednum}"
    )

    return tordetail


# xpath method
def xpathGetElement(row, siteJson, key):
    if not siteJson:
        return ""
    if key not in siteJson:
        # 如果site中没有配置 key 项，在 nexusphp 配置中找
        siteJson = siteconfig.getSiteConfig("nexusphp")
        if key not in siteJson:
            return ""
    eleJson = siteJson[key]
    if not isinstance(eleJson, str):
        elestring = row.xpath(eleJson["path"])
        if elestring and "method" in eleJson:
            if eleJson["method"] == "re_imdb":
                m = re.search(r"title/(tt\d+)", elestring, re.I)
                return m[1] if m else ""
            elif eleJson["method"] == "re_douban":
                m = re.search(r"subject/(\d+)", elestring, re.I)
                return m[1] if m else ""
            elif eleJson["method"] == "ssd_imdb":
                m = re.search(r"search=(\d+)&search_area=4", elestring, re.I)
                return m[1] if m else ""
            elif eleJson["method"] == "ssd_douban":
                m = re.search(r"search=(\d+)&search_area=5", elestring, re.I)
                return m[1] if m else ""
            elif eleJson["method"] == "ttg_seednum":
                m = re.search(r"(\d+)\s*/\s*\d+", elestring, re.I)
                return m[1] if m else ""
            elif eleJson["method"] == "ttg_downum":
                m = re.search(r"\d+\s*/\s*(\d+)", elestring, re.I)
                return m[1] if m else ""

        return ""
    else:
        if not eleJson.strip():
            return ""
        return row.xpath(eleJson)


def matchIMDbid(str):
    return True if re.match(r"tt\d+", str.strip(), re.I) else False


def xpathSearchPtSites(sitehost, siteCookie, seachWord):
    sitehost = nomalizeSitename(sitehost)
    cursite = siteconfig.getSiteConfig(sitehost)
    if not cursite:
        logger.error(f"搜索出错: {sitehost} 未配置")
        return -1  # site not configured

    if matchIMDbid(seachWord):
        pturl = cursite["baseurl"] + cursite["searchIMDburl"] + seachWord
    else:
        pturl = cursite["baseurl"] + cursite["searchurl"] + seachWord

    r = requestSitePage(pturl, siteCookie)
    if not r:
        logger.error(f"搜索，站点页面访问出错 {pturl} ")
        return -1  # page not fetched
    doc = r.content
    parser = lxml.html.HTMLParser(recover=True, encoding="utf-8")
    htmltree = lxml.html.fromstring(doc, parser=parser)
    torlist = htmltree.xpath(cursite["torlist"])
    count = 0
    for row in reversed(torlist):
        # title = xpathGetElement(row, cursite, "tortitle")
        infolink = xpathGetElement(row, cursite, "infolink")
        if not infolink:
            continue

        infolink = getfulllink(sitehost, infolink)

        dbitem = TorrentCache()
        dbitem.site = sitehost
        dbitem.infolink = infolink
        fillDbitemWithXPathParser(dbitem, row, cursite)
        fillDbitemWithTMDbParser(dbitem)
        dbitem.searchword = seachWord

        count += 1
        db.session.add(dbitem)
        db.session.commit()
    logger.info(f"搜索 {sitehost}: {seachWord}, 得 {count} 个结果")
    return count


def parseInfoPageIMDbval(doc):
    imdbval = 0
    m1 = re.search(r"IMDb.*?([0-9.]+)\s*/\s*10", doc, flags=re.I)
    if m1:
        imdbval = tryFloat(m1[1])
    doubanval = 0
    m2 = re.search(r"豆瓣.*?([0-9.]+)/10", doc, flags=re.I)
    if m2:
        doubanval = tryFloat(m2[1])
    if imdbval < 1 and doubanval < 1:
        ratelist = [
            x[1]
            for x in re.finditer(
                r"Rating:.*?([0-9.]+)\s*/\s*10\s*from", doc, flags=re.I
            )
        ]
        if len(ratelist) >= 2:
            doubanval = tryFloat(ratelist[0])
            imdbval = tryFloat(ratelist[1])
        elif len(ratelist) == 1:
            # TODO: 不分辨douban/imdb了
            doubanval = tryFloat(ratelist[0])
            imdbval = doubanval
            # rate1 = re.search(r'Rating:.*?([0-9.]+)\s*/\s*10\s*from', doc, flags=re.A)
            # if rate1:
            #     imdbval = tryFloat(rate1[1])
        # print("   >> IMDb: %s, douban: %s" % (imdbval, doubanval))
    return imdbval, doubanval


def fillDbitemWithTMDbParser(dbitem):
    p = TMDbNameParser(myconfig.CONFIG.torcpdb_url, myconfig.CONFIG.torcpdb_apikey)
    p.parse(
        torname=dbitem.tortitle,
        useTMDb=True,
        hasIMDbId=dbitem.imdbstr,
        infolink=getfulllink(dbitem.site, dbitem.infolink),
    )
    dbitem.genrestr = genreid2str(p.genre_ids)
    dbitem.tmdbtitle, dbitem.tmdbcat, dbitem.tmdbid, dbitem.tmdbposter = (
        p.title,
        p.tmdbcat,
        p.tmdbid,
        p.poster_path,
    )
    dbitem.tmdbyear = p.year
    dbitem.mediasource, dbitem.videocodec, dbitem.audiocodec = (
        p.mediaSource,
        p.videoCodec,
        p.audioCodec,
    )
    dbitem.imdbstr = p.imdbid
    dbitem.imdbval = p.imdbval


def fillDbitemWithXPathParser(dbitem, row, cursite):
    title = xpathGetElement(row, cursite, "tortitle")
    dbitem.mediasource = parseMediaSource(title)
    # dbitem.infolink = xpathGetElement(row, cursite, "infolink")
    # dbitem.infolink = getfulllink(dbitem.site, dbitem.infolink)
    dbitem.downlink = xpathGetElement(row, cursite, "downlink")
    if not dbitem.downlink and dbitem.infolink:
        dbitem.downlink = dbitem.infolink.replace("details.php", "download.php")
    subtitle = str(xpathGetElement(row, cursite, "subtitle"))
    if subtitle:
        title, subtitle = subsubtitle(title, subtitle)
        dbitem.subtitle = striptag(subtitle)
    dbitem.tortitle = striptitle(title)

    dbitem.tagzz = True if xpathGetElement(row, cursite, "tagzz") else False
    dbitem.taggy = True if xpathGetElement(row, cursite, "taggy") else False
    dbitem.tagfree = True if xpathGetElement(row, cursite, "tagfree") else False
    dbitem.tag2xfree = True if xpathGetElement(row, cursite, "tag2xfree") else False
    dbitem.doubanval = tryFloat(xpathGetElement(row, cursite, "doubanval"))
    dbitem.imdbval = tryFloat(xpathGetElement(row, cursite, "imdbval"))
    dbitem.imdbstr = xpathGetElement(row, cursite, "imdbstr")
    if dbitem.imdbstr and not dbitem.imdbstr.startswith("tt"):
        dbitem.imdbstr = "tt" + dbitem.imdbstr.zfill(7)
    dbitem.doubanid = xpathGetElement(row, cursite, "doubanid")
    dbitem.seednum = tryint(xpathGetElement(row, cursite, "seednum"))
    dbitem.downnum = tryint(xpathGetElement(row, cursite, "downnum"))
    dbitem.torsizestr = str(xpathGetElement(row, cursite, "torsize")).strip()
    dbitem.torsizeint = parseSizeStr(dbitem.torsizestr)
    tordatestr = xpathGetElement(row, cursite, "tordate")
    try:
        dbitem.tordate = datetime.strptime(tordatestr, "%Y-%m-%d %H:%M:%S")
    except:
        logger.warning(f"日期解析出错：{tordatestr}, {dbitem.infolink}")
        dbitem.tordate = datetime.now()


UPDATE_STATUS_IDLE = 0
UPDATE_STATUS_BUSY = 1


def siteUpdateBegin(sitename: str):
    dbsite = PtSite.query.filter(PtSite.site == sitename).first()
    dbsite.updateing = UPDATE_STATUS_BUSY
    db.session.commit()


def siteUpdateEnd(sitename: str):

    dbsite = PtSite.query.filter(PtSite.site == sitename).first()
    dbsite.updateing = UPDATE_STATUS_IDLE
    db.session.commit()


def getSiteTorrent(sitename, sitecookie, siteurl=None):
    sitename = nomalizeSitename(sitename)
    cursite = siteconfig.getSiteConfig(sitename)
    if not cursite:
        logger.info(f"site {sitename} not configured")
        return -1  # site not configured

    if not siteurl:
        if "newtorrent" in cursite:
            siteurl = cursite["baseurl"] + cursite["newtorrent"]
    if not siteurl.startswith("http"):
        siteurl = cursite["baseurl"] + siteurl
    logger.info(f"站新 {sitename}: {siteurl}")
    siteUpdateBegin(sitename)
    # if not siteurl:
    #     logger.warning("no newtorlink configured.")
    #     return -2
    logger.info(f"Loading new torrents: {sitename} - {siteurl}")
    r = requestSitePage(siteurl, sitecookie)
    if not r:
        logger.warning("Fail to fetch: " + siteurl)
        return -3  # page not fetched
    doc = r.content
    parser = lxml.html.HTMLParser(recover=True, encoding="utf-8")
    htmltree = lxml.html.fromstring(doc, parser=parser)
    torlist = htmltree.xpath(cursite["torlist"])
    count = 0
    logger.info(f"站新 种子列表: {len(torlist)}")
    for row in reversed(torlist):
        # title = xpathGetElement(row, cursite, "tortitle")
        infolink = xpathGetElement(row, cursite, "infolink")
        if not infolink:
            continue

        infolink = getfulllink(sitename, infolink)
        exists = db.session.query(
            SiteTorrent.query.filter(db.and_(
                        SiteTorrent.infolink == infolink, SiteTorrent.site == sitename
                    )).exists()).scalar()

        if exists:
            continue

        dbitem = SiteTorrent()
        dbitem.site = sitename
        dbitem.infolink = infolink
        fillDbitemWithXPathParser(dbitem, row, cursite)
        logger.info(f"{dbitem.tortitle}, {dbitem.tordate}")
        fillDbitemWithTMDbParser(dbitem)

        count += 1
        db.session.add(dbitem)
        db.session.commit()
    siteUpdateEnd(sitename)
    logger.info(f"站新完成 {sitename} : {count} ")
    return count
