from optpick import TorrentParser, TorrentInfo, OptPickConfig
from models import db, RSSHistory, TorDownload, TorDetail
from typing import Optional
import re
from flask import current_app
from loguru import logger


class OptimalPickManager:
    """RSS 择优下载管理器"""

    def __init__(self, config_path: str = "optconfig.json"):
        if not config_path:
            config_path = "optconfig.json"
        self.config = OptPickConfig(config_path)

        # 编译所有规则的正则表达式
        self.rules = [
            (rule["name"], re.compile(rule["pattern"]), rule.get("excludes", []))
            for rule in self.config.get_rules()
        ]

    def calculate_score(self, torrent_info: TorrentInfo) -> int:
        """计算种子版本得分"""
        return (
            self.config.get_group_score(torrent_info.group)
            + self.config.get_source_score(torrent_info.source)
            + self.config.get_resolution_score(torrent_info.resolution)
        )

    def getSameSeriesSeasonResolution(
        self, torrent_info: TorrentInfo
    ) -> Optional[TorDownload]:
        return (
            db.session.query(TorDownload)
            .join(TorDetail, TorDetail.id == TorDownload.tor_detail_id)
            .filter(
                (TorDetail.media_title == torrent_info.media_title)
                & (TorDetail.season == torrent_info.season)
                & (TorDetail.resolution == torrent_info.resolution)
            )
            .order_by(TorDownload.id.desc())
            .first()
        )
        # query = db.session.query(
        # TorDownload).join(
        #     TorDetail, TorDetail.id==TorDownload.tor_detail_id).all()

    def compareOptimalByGroup(self, groupNew, groupInDb):
        return self.config.get_group_score(groupNew) >= self.config.get_group_score(
            groupInDb
        )

    def should_download(self, dbrssitem: RSSHistory) -> bool:
        """判断是否应该择优"""
        with current_app.app_context():
            # TODO: 检查是否匹配任何规则
            matched = False
            matchstr = dbrssitem.title + ", " + dbrssitem.subtitle
            for name, pattern, excludes in self.rules:
                if pattern.match(matchstr):
                    matched = True
                    # 检查排除规则
                    if any(exclude in matchstr for exclude in excludes):
                        logger.info(f"Title matched but excluded: {matchstr}")
                        return False
                    break

            if not matched:  # 没有要求择优，默认下载
                return True

            # 解析种子信息
            torrent_info = TorrentParser.parse(dbrssitem.title)
            # 不在择优组列表中，不下载
            if not self.config.in_group_list(torrent_info.group):
                return False

            # 检查已存在的记录，后加的记录应当是具有更高的分
            # WARN: 匹配时要求 media_title，season, resolution 都一致
            existing_record = self.getSameSeriesSeasonResolution(torrent_info)
            if not existing_record:  # 没有下载过，则默认下载
                return True

            # 比较版本优先级
            return self.compareOptimalByGroup(
                torrent_info.group, existing_record.tor_detail.group
            )
