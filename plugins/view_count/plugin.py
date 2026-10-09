from teachingplatform.plugin_manage.base_plugin import BasePlugin
from teachingplatform.plugin_manage import hooks


class ViewCountPlugin(BasePlugin):
    PLUGIN_NAME = '教学资源浏览次数统计'
    PLUGIN_DESCRIPTION = '统计教学资源的浏览次数'
    PLUGIN_VERSION = '0.1.0'
    PLUGIN_AUTHOR = '在线教学资源平台'

    def register_hooks(self):
        hooks.register('after_article_body_get', self.record_view)

    def record_view(self, article, *args, **kwargs):
        article.viewed()


plugin = ViewCountPlugin() 