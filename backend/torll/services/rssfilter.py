import re
from utils import nomalizeSitename, tryint, genhash
from loguru import logger

class RssFilter:
    def __init__(self, filters):
        self.filters = filters
        self.match_filter = None
        self.tag = ""

    def matchFilter(self, filter, dbrssitem):
        """filter中条件满足返回 DL，不满足返回 reason"""
        if "title_regex" in filter:
            if not re.search(filter["title_regex"], dbrssitem.title, re.I):
                return "TITLE_REGEX"
        if "title_not_regex" in filter:
            if re.search(filter["title_not_regex"], dbrssitem.title, re.I):
                return "TITLE_NOT_REGEX"
        if "subtitle_regex" in filter:
            if not re.search(filter["subtitle_regex"], dbrssitem.subtitle, re.I):
                return "SUBTITLE_REGEX"
        if "subtitle_not_regex" in filter:
            if re.search(filter["subtitle_not_regex"], dbrssitem.subtitle, re.I):
                return "SUBTITLE_NOT_REGEX"
        if "no_hr" in filter:
            if re.search(r"h\d$", dbrssitem.subtitle):
                return "NO_HR"
        if "size_gb_min" in filter:
            size_gb = tryint(dbrssitem.size) / 10**9
            if size_gb < filter["size_gb_min"]:
                return "SIZE_MIN"
        if "size_gb_max" in filter:
            size_gb = tryint(dbrssitem.size) / 10**9
            if size_gb > filter["size_gb_max"]:
                return "SIZE_MAX"
        if "rsstags_regex" in filter:
            if not re.search(filter["rsstags_regex"], dbrssitem.rsstags, re.I):
                return "RSS_TAG_REGEX"
        if "rsstags_not_regex" in filter:
            if re.search(filter["rsstags_not_regex"], dbrssitem.rsstags, re.I):
                return "RSS_TAG_NOT_REGEX"
        if "rsscat_regex" in filter:
            if not re.search(filter["rsscat_regex"], dbrssitem.rsscatstr, re.I):
                return "RSS_CAT_REGEX"
        if "rsscat_not_regex" in filter:
            if re.search(filter["rsscat_not_regex"], dbrssitem.rsscatstr, re.I):
                return "RSS_CAT_NOT_REGEX"
        return "DL"


    def getFilterTag(self, filter):
        tag = ""
        if "tag" in filter:
            tag = filter["tag"]

        return tag
    
    def getMatchQbitName(self):
        if not self.match_filter:
            return None
        
        qbitname = ""
        if "qbitname" in self.match_filter:
            qbitname = self.match_filter["qbitname"]

        return qbitname

    def applyFilters(self, dbrssitem):
        reason = "DL"
        for filter in self.filters:
            try:
                reason = self.matchFilter(filter, dbrssitem)
                if reason == "DL":
                    self.match_filter = filter
                    self.tag = self.getFilterTag(filter)
                    return reason
                elif reason == "":
                    logger.debug(f"{self.name} {dbrssitem.title}")
                    return "(empty)"
            except:
                logger.error(f"filter 规则错误")
                return "规则写错"
        # 全部 filter条件都不满足
        return reason

    def applyDetailFilter(self, detail):
        if not self.match_filter:
            logger.error(f"匹配 filter 为空")
            return "匹配 filter 错误"
        reason = "DL"
        if "rate_min" in self.match_filter:
            # 如果 imdb/douban 没取到，且有 rate_min 要求，则有此限制
            if (
                detail.imdbval < self.match_filter["rate_min"]
                and detail.doubanval < self.match_filter["rate_min"]
            ):
                return "RATE_MIN"
        return reason
