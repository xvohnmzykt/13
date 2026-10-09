import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SpiderNotify():
    @staticmethod
    def baidu_notify(urls):
        notify_url = getattr(settings, 'BAIDU_NOTIFY_URL', '')
        if not notify_url:
            # 未配置百度推送地址时静默跳过，避免每次保存都记录错误日志
            logger.debug('BAIDU_NOTIFY_URL is not configured, skip spider notify.')
            return
        try:
            data = '\n'.join(urls)
            result = requests.post(notify_url, data=data, timeout=10)
            logger.info(result.text)
        except Exception as e:
            logger.error(e)

    @staticmethod
    def notify(url):
        SpiderNotify.baidu_notify(url)
