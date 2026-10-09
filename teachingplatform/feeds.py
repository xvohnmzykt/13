from django.contrib.auth import get_user_model
from django.contrib.syndication.views import Feed
from django.utils import timezone
from django.utils.feedgenerator import Rss201rev2Feed

from blog.models import Article
from teachingplatform.utils import CommonMarkdown


class TeachingPlatformFeed(Feed):
    feed_type = Rss201rev2Feed

    description = '在线教学资源平台 —— 汇聚优质课程与教学资源'
    title = '在线教学资源平台'
    link = "/feed/"

    def author_name(self):
        return get_user_model().objects.first().nickname

    def author_link(self):
        return get_user_model().objects.first().get_absolute_url()

    def items(self):
        return Article.objects.filter(type='a', status='p').order_by('-pub_time')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return CommonMarkdown.get_markdown(item.body)

    def feed_copyright(self):
        now = timezone.now()
        return "Copyright© {year} 在线教学资源平台".format(year=now.year)

    def item_link(self, item):
        return item.get_absolute_url()

    def item_guid(self, item):
        return
