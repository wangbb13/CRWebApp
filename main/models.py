from django.db import models


class ReturnApplyInfo(models.Model):
    draw_yard_code = models.CharField(u'提取堆场代码', max_length=6, null=True)
    container_quantity = models.IntegerField(u'总箱数')
    draw_datetime = models.DateTimeField(u'提取时间')


class YardInfo(models.Model):
    code = models.CharField(u'堆场代码', max_length=6, null=True)
    abbr = models.CharField(u'堆场简称', max_length=100, null=True)
    name = models.CharField(u'堆场全称', max_length=100, null=True)
    en = models.CharField(u'堆场英文名称', max_length=200, null=True)
    country_id = models.IntegerField(u'堆场所在国家ID')
    country = models.CharField(u'堆场所在国家', max_length=80, null=True)
    city_id = models.CharField(u'堆场所在城市ID', max_length=10, null=True)
    city = models.CharField(u'堆场所在城市', max_length=60, null=True)
