from django.test import TestCase

from teachingplatform.utils import *


class TeachingPlatformTest(TestCase):
    def setUp(self):
        pass

    def test_utils(self):
        md5 = get_sha256('test')
        self.assertIsNotNone(md5)
        c = CommonMarkdown.get_markdown('''
        # Title1

        ```python
        import os
        ```

        [url](https://teaching-platform.example.com/)

        [ddd](http://www.baidu.com)


        ''')
        self.assertIsNotNone(c)
        d = {
            'd': 'key1',
            'd2': 'key2'
        }
        data = parse_dict_to_url(d)
        self.assertIsNotNone(data)
