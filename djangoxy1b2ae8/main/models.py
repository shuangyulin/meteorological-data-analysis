#coding:utf-8
from django.db import models

from .model import BaseModel

from datetime import datetime



class yonghu(BaseModel):
    __doc__ = u'''yonghu'''
    __tablename__ = 'yonghu'

    __loginUser__='yonghuming'


    __authTables__={}
    __authPeople__='是'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __loginUserColumn__='yonghuming'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='是'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=False, verbose_name=u'创建时间')
    yonghuming=models.CharField ( max_length=255,null=False,unique=True, verbose_name='用户名' )
    mima=models.CharField ( max_length=255,null=False, unique=False, verbose_name='密码' )
    xingming=models.CharField ( max_length=255,null=False, unique=False, verbose_name='姓名' )
    touxiang=models.TextField   (  null=True, unique=False, verbose_name='头像' )
    xingbie=models.CharField ( max_length=255, null=True, unique=False, verbose_name='性别' )
    nianling=models.IntegerField  (  null=True, unique=False, verbose_name='年龄' )
    youxiang=models.CharField ( max_length=255, null=True, unique=False, verbose_name='邮箱' )
    shouji=models.CharField ( max_length=255, null=True, unique=False, verbose_name='手机' )
    '''
    yonghuming=VARCHAR
    mima=VARCHAR
    xingming=VARCHAR
    touxiang=Text
    xingbie=VARCHAR
    nianling=Integer
    youxiang=VARCHAR
    shouji=VARCHAR
    '''
    class Meta:
        db_table = 'yonghu'
        verbose_name = verbose_name_plural = '用户'
class oceandata(BaseModel):
    __doc__ = u'''oceandata'''
    __tablename__ = 'oceandata'



    __authTables__={}
    __authPeople__='否'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='否'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=False, verbose_name=u'创建时间')
    date=models.DateField   (  null=True, unique=False, verbose_name='日期' )
    seasurfacetemperature=models.FloatField   (  null=True, unique=False, verbose_name='海面温度(℃)' )
    salinityofseawaterpsu=models.FloatField   (  null=True, unique=False, verbose_name='海水盐度(PSU)' )
    waveheight=models.FloatField   (  null=True, unique=False, verbose_name='海浪高度(米)' )
    wavecycle=models.FloatField   (  null=True, unique=False, verbose_name='海浪周期(秒)' )
    wavedirection=models.CharField ( max_length=255, null=True, unique=False, verbose_name='海浪方向' )
    windspeed=models.FloatField   (  null=True, unique=False, verbose_name='风速(米/秒)' )
    winddirection=models.CharField ( max_length=255, null=True, unique=False, verbose_name='风向' )
    airpressure=models.FloatField   (  null=True, unique=False, verbose_name='气压(百帕)' )
    humidity=models.FloatField   (  null=True, unique=False, verbose_name='湿度(%)' )
    precipitation=models.FloatField   (  null=True, unique=False, verbose_name='降水量(毫米)' )
    currentvelocityms=models.FloatField   (  null=True, unique=False, verbose_name='洋流速度(米/秒)' )
    currentdirection=models.CharField ( max_length=255, null=True, unique=False, verbose_name='洋流方向' )
    sealevelheight=models.FloatField   (  null=True, unique=False, verbose_name='海平面高度(米)' )
    depthofunderwater=models.FloatField   (  null=True, unique=False, verbose_name='海底地形深度(米)' )
    seawatertransparency=models.FloatField   (  null=True, unique=False, verbose_name='海水透明度(米)' )
    acidityandalkalinityofseawaterph=models.FloatField   (  null=True, unique=False, verbose_name='海水酸碱度(pH)' )
    dissolvedoxygeninseawater=models.FloatField   (  null=True, unique=False, verbose_name='海水溶解氧(毫升/升)' )
    '''
    date=Date
    seasurfacetemperature=Float
    salinityofseawaterpsu=Float
    waveheight=Float
    wavecycle=Float
    wavedirection=VARCHAR
    windspeed=Float
    winddirection=VARCHAR
    airpressure=Float
    humidity=Float
    precipitation=Float
    currentvelocityms=Float
    currentdirection=VARCHAR
    sealevelheight=Float
    depthofunderwater=Float
    seawatertransparency=Float
    acidityandalkalinityofseawaterph=Float
    dissolvedoxygeninseawater=Float
    '''
    class Meta:
        db_table = 'oceandata'
        verbose_name = verbose_name_plural = '海洋数据'
class oceandataforecast(BaseModel):
    __doc__ = u'''oceandataforecast'''
    __tablename__ = 'oceandataforecast'



    __authTables__={}
    __authPeople__='否'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='否'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=False, verbose_name=u'创建时间')
    date=models.CharField ( max_length=255, null=True, unique=False, verbose_name='日期' )
    waveheight=models.FloatField   (  null=True, unique=False, verbose_name='海浪高度(米)' )
    windspeed=models.FloatField   (  null=True, unique=False, verbose_name='风速(米/秒)' )
    airpressure=models.FloatField   (  null=True, unique=False, verbose_name='气压(百帕)' )
    precipitation=models.FloatField   (  null=True, unique=False, verbose_name='降水量(毫米)' )
    '''
    date=VARCHAR
    waveheight=Float
    windspeed=Float
    airpressure=Float
    precipitation=Float
    '''
    class Meta:
        db_table = 'oceandataforecast'
        verbose_name = verbose_name_plural = '预测信息'
