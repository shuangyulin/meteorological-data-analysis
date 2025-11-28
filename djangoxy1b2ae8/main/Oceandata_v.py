#coding:utf-8
import base64, copy, logging, os, sys, time, xlrd, json, datetime, configparser
from django.http import JsonResponse
from django.apps import apps
import numbers
from django.db.models.aggregates import Count,Sum
from django.db.models import Case, When, IntegerField, F
from django.forms import model_to_dict
import requests
from util.CustomJSONEncoder import CustomJsonEncoder
from .models import oceandata
from util.codes import *
from util.auth import Auth
from util.common import Common
import util.message as mes
from django.db import connection
import random
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.db.models import Q
from util.baidubce_api import BaiDuBce
from .config_model import config


def oceandata_register(request):
    if request.method in ["POST", "GET"]:
        msg = {'code': normal_code, "msg": mes.normal_code}
        req_dict = request.session.get("req_dict")


        error = oceandata.createbyreq(oceandata, oceandata, req_dict)
        if error is Exception or (type(error) is str and "Exception" in error):
            msg['code'] = crud_error_code
            msg['msg'] = "用户已存在,请勿重复注册!"
        else:
            msg['data'] = error
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def oceandata_login(request):
    if request.method in ["POST", "GET"]:
        msg = {'code': normal_code, "msg": mes.normal_code}
        req_dict = request.session.get("req_dict")
        datas = oceandata.getbyparams(oceandata, oceandata, req_dict)
        if not datas:
            msg['code'] = password_error_code
            msg['msg'] = mes.password_error_code
            return JsonResponse(msg, encoder=CustomJsonEncoder)

        try:
            __sfsh__= oceandata.__sfsh__
        except:
            __sfsh__=None

        if  __sfsh__=='是':
            if datas[0].get('sfsh')!='是':
                msg['code']=other_code
                msg['msg'] = "账号已锁定，请联系管理员审核!"
                return JsonResponse(msg, encoder=CustomJsonEncoder)
                
        req_dict['id'] = datas[0].get('id')


        return Auth.authenticate(Auth, oceandata, req_dict)


def oceandata_logout(request):
    if request.method in ["POST", "GET"]:
        msg = {
            "msg": "登出成功",
            "code": 0
        }

        return JsonResponse(msg, encoder=CustomJsonEncoder)


def oceandata_resetPass(request):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code}

        req_dict = request.session.get("req_dict")

        columns=  oceandata.getallcolumn( oceandata, oceandata)

        try:
            __loginUserColumn__= oceandata.__loginUserColumn__
        except:
            __loginUserColumn__=None
        username=req_dict.get(list(req_dict.keys())[0])
        if __loginUserColumn__:
            username_str=__loginUserColumn__
        else:
            username_str=username
        if 'mima' in columns:
            password_str='mima'
        else:
            password_str='password'

        init_pwd = '123456'
        recordsParam = {}
        recordsParam[username_str] = req_dict.get("username")
        records=oceandata.getbyparams(oceandata, oceandata, recordsParam)
        if len(records)<1:
            msg['code'] = 400
            msg['msg'] = '用户不存在'
            return JsonResponse(msg, encoder=CustomJsonEncoder)

        eval('''oceandata.objects.filter({}='{}').update({}='{}')'''.format(username_str,username,password_str,init_pwd))
        
        return JsonResponse(msg, encoder=CustomJsonEncoder)



def oceandata_session(request):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code,"msg": mes.normal_code, "data": {}}

        req_dict={"id":request.session.get('params').get("id")}
        msg['data']  = oceandata.getbyparams(oceandata, oceandata, req_dict)[0]

        return JsonResponse(msg, encoder=CustomJsonEncoder)


def oceandata_default(request):

    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code,"msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        req_dict.update({"isdefault":"是"})
        data=oceandata.getbyparams(oceandata, oceandata, req_dict)
        if len(data)>0:
            msg['data']  = data[0]
        else:
            msg['data']  = {}
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def oceandata_page(request):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = request.session.get("req_dict")

        global oceandata
        #当前登录用户信息
        tablename = request.session.get("tablename")

        msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], \
        msg['data']['pageSize']  =oceandata.page(oceandata, oceandata, req_dict, request)
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def oceandata_autoSort(request):
    '''
    ．智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
主要信息列表（如商品列表，新闻列表）中使用，显示最近点击的或最新添加的5条记录就行
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = request.session.get("req_dict")
        if "clicknum"  in oceandata.getallcolumn(oceandata,oceandata):
            req_dict['sort']='clicknum'
        elif "browseduration"  in oceandata.getallcolumn(oceandata,oceandata):
            req_dict['sort']='browseduration'
        else:
            req_dict['sort']='clicktime'
        req_dict['order']='desc'
        msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], \
        msg['data']['pageSize']  = oceandata.page(oceandata,oceandata, req_dict)

        return JsonResponse(msg, encoder=CustomJsonEncoder)

#分类列表
def oceandata_lists(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":[]}
        msg['data'],_,_,_,_  = oceandata.page(oceandata, oceandata, {})
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def oceandata_query(request):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        try:
            query_result = oceandata.objects.filter(**request.session.get("req_dict")).values()
            msg['data'] = query_result[0]
        except Exception as e:

            msg['code'] = crud_error_code
            msg['msg'] = f"发生错误：{e}"
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def oceandata_list(request):
    '''
    前台分页
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code,  "data":{"currPage":1,"totalPage":1,"total":1,"pageSize":10,"list":[]}}
        req_dict = request.session.get("req_dict")
        #获取全部列名
        columns=  oceandata.getallcolumn( oceandata, oceandata)
        if "vipread" in req_dict and "vipread" not in columns:
          del req_dict["vipread"]
        #表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
        try:
            __foreEndList__=oceandata.__foreEndList__
        except:
            __foreEndList__=None
        try:
            __foreEndListAuth__=oceandata.__foreEndListAuth__
        except:
            __foreEndListAuth__=None

        #authSeparate
        try:
            __authSeparate__=oceandata.__authSeparate__
        except:
            __authSeparate__=None

        if __foreEndListAuth__ =="是" and __authSeparate__=="是":
            tablename=request.session.get("tablename")
            if tablename!="users" and request.session.get("params") is not None:
                req_dict['userid']=request.session.get("params").get("id")

        tablename = request.session.get("tablename")
        if tablename == "users" and req_dict.get("userid") != None:#判断是否存在userid列名
            del req_dict["userid"]
        else:
            __isAdmin__ = None

            allModels = apps.get_app_config('main').get_models()
            for m in allModels:
                if m.__tablename__==tablename:

                    try:
                        __isAdmin__ = m.__isAdmin__
                    except:
                        __isAdmin__ = None
                    break

            if __isAdmin__ == "是":
                if req_dict.get("userid"):
                    # del req_dict["userid"]
                    pass
            else:
                #非管理员权限的表,判断当前表字段名是否有userid
                if "userid" in columns:
                    try:
                        pass
                    except:
                        pass
        #当列属性authTable有值(某个用户表)[该列的列名必须和该用户表的登陆字段名一致]，则对应的表有个隐藏属性authTable为”是”，那么该用户查看该表信息时，只能查看自己的
        try:
            __authTables__=oceandata.__authTables__
        except:
            __authTables__=None

        if __authTables__!=None and  __authTables__!={} and __foreEndListAuth__=="是":
            for authColumn,authTable in __authTables__.items():
                if authTable==tablename:
                    try:
                        del req_dict['userid']
                    except:
                        pass
                    params = request.session.get("params")
                    req_dict[authColumn]=params.get(authColumn)
                    username=params.get(authColumn)
                    break
        
        if oceandata.__tablename__[:7]=="discuss":
            try:
                del req_dict['userid']
            except:
                pass


        q = Q()
        msg['data']['list'], msg['data']['currPage'], msg['data']['totalPage'], msg['data']['total'], \
        msg['data']['pageSize']  = oceandata.page(oceandata, oceandata, req_dict, request, q)
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def oceandata_save(request):
    '''
    后台新增
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        if 'clicktime' in req_dict.keys():
            del req_dict['clicktime']
        tablename=request.session.get("tablename")
        __isAdmin__ = None
        allModels = apps.get_app_config('main').get_models()
        for m in allModels:
            if m.__tablename__==tablename:

                try:
                    __isAdmin__ = m.__isAdmin__
                except:
                    __isAdmin__ = None
                break

        #获取全部列名
        columns=  oceandata.getallcolumn( oceandata, oceandata)
        if tablename!='users' and req_dict.get("userid")==None and 'userid' in columns  and __isAdmin__!='是':
            params=request.session.get("params")
            req_dict['userid']=params.get('id')


        if 'addtime' in req_dict.keys():
            del req_dict['addtime']

        idOrErr= oceandata.createbyreq(oceandata,oceandata, req_dict)
        if idOrErr is Exception:
            msg['code'] = crud_error_code
            msg['msg'] = idOrErr
        else:
            msg['data'] = idOrErr

        return JsonResponse(msg, encoder=CustomJsonEncoder)

def oceandata_add(request):
    '''
    前台新增
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        tablename=request.session.get("tablename")

        #获取全部列名
        columns=  oceandata.getallcolumn( oceandata, oceandata)
        try:
            __authSeparate__=oceandata.__authSeparate__
        except:
            __authSeparate__=None

        if __authSeparate__=="是":
            tablename=request.session.get("tablename")
            if tablename!="users" and 'userid' in columns:
                try:
                    req_dict['userid']=request.session.get("params").get("id")
                except:
                    pass

        try:
            __foreEndListAuth__=oceandata.__foreEndListAuth__
        except:
            __foreEndListAuth__=None

        if __foreEndListAuth__ and __foreEndListAuth__!="否":
            tablename=request.session.get("tablename")
            if tablename!="users":
                req_dict['userid']=request.session.get("params").get("id")


        if 'addtime' in req_dict.keys():
            del req_dict['addtime']
        error= oceandata.createbyreq(oceandata,oceandata, req_dict)
        if error is Exception:
            msg['code'] = crud_error_code
            msg['msg'] = error
        else:
            msg['data'] = error
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def oceandata_thumbsup(request,id_):
    '''
     点赞：表属性thumbsUp[是/否]，刷表新增thumbsupnum赞和crazilynum踩字段，
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        id_=int(id_)
        type_=int(req_dict.get("type",0))
        rets=oceandata.getbyid(oceandata,oceandata,id_)

        update_dict={
        "id":id_,
        }
        if type_==1:#赞
            update_dict["thumbsupnum"]=int(rets[0].get('thumbsupnum'))+1
        elif type_==2:#踩
            update_dict["crazilynum"]=int(rets[0].get('crazilynum'))+1
        error = oceandata.updatebyparams(oceandata,oceandata, update_dict)
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error
        return JsonResponse(msg, encoder=CustomJsonEncoder)


def oceandata_info(request,id_):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}

        data = oceandata.getbyid(oceandata,oceandata, int(id_))
        if len(data)>0:
            msg['data']=data[0]
            if msg['data'].__contains__("reversetime"):
                if isinstance(msg['data']['reversetime'], datetime.datetime):
                    msg['data']['reversetime'] = msg['data']['reversetime'].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    if msg['data']['reversetime'] != None:
                        reversetime = datetime.datetime.strptime(msg['data']['reversetime'], '%Y-%m-%d %H:%M:%S')
                        msg['data']['reversetime'] = reversetime.strftime("%Y-%m-%d %H:%M:%S")

        #浏览点击次数
        try:
            __browseClick__= oceandata.__browseClick__
        except:
            __browseClick__=None

        if __browseClick__=="是"  and  "clicknum"  in oceandata.getallcolumn(oceandata,oceandata):
            try:
                clicknum=int(data[0].get("clicknum",0))+1
            except:
                clicknum=0+1
            click_dict={"id":int(id_),"clicknum":clicknum,"clicktime":datetime.datetime.now()}
            ret=oceandata.updatebyparams(oceandata,oceandata,click_dict)
            if ret!=None:
                msg['code'] = crud_error_code
                msg['msg'] = ret
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def oceandata_detail(request,id_):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}

        data =oceandata.getbyid(oceandata,oceandata, int(id_))
        if len(data)>0:
            msg['data']=data[0]
            if msg['data'].__contains__("reversetime"):
                if isinstance(msg['data']['reversetime'], datetime.datetime):
                    msg['data']['reversetime'] = msg['data']['reversetime'].strftime("%Y-%m-%d %H:%M:%S")
                else:
                    if msg['data']['reversetime'] != None:
                        reversetime = datetime.datetime.strptime(msg['data']['reversetime'], '%Y-%m-%d %H:%M:%S')
                        msg['data']['reversetime'] = reversetime.strftime("%Y-%m-%d %H:%M:%S")

        #浏览点击次数
        try:
            __browseClick__= oceandata.__browseClick__
        except:
            __browseClick__=None

        if __browseClick__=="是"   and  "clicknum"  in oceandata.getallcolumn(oceandata,oceandata):
            try:
                clicknum=int(data[0].get("clicknum",0))+1
            except:
                clicknum=0+1
            click_dict={"id":int(id_),"clicknum":clicknum,"clicktime":datetime.datetime.now()}

            ret=oceandata.updatebyparams(oceandata,oceandata,click_dict)
            if ret!=None:
                msg['code'] = crud_error_code
                msg['msg'] = ret
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def oceandata_update(request):
    '''
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")
        if 'clicktime' in req_dict.keys() and req_dict['clicktime']=="None":
            del req_dict['clicktime']
        if req_dict.get("mima") and "mima" not in oceandata.getallcolumn(oceandata,oceandata) :
            del req_dict["mima"]
        if req_dict.get("password") and "password" not in oceandata.getallcolumn(oceandata,oceandata) :
            del req_dict["password"]
        try:
            del req_dict["clicknum"]
        except:
            pass


        error = oceandata.updatebyparams(oceandata, oceandata, req_dict)
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error

        return JsonResponse(msg)


def oceandata_delete(request):
    '''
    批量删除
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code, "data": {}}
        req_dict = request.session.get("req_dict")

        error=oceandata.deletes(oceandata,
            oceandata,
             req_dict.get("ids")
        )
        if error!=None:
            msg['code'] = crud_error_code
            msg['msg'] = error
        return JsonResponse(msg)


def oceandata_vote(request,id_):
    '''
    浏览点击次数（表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1）
统计商品或新闻的点击次数；提供新闻的投票功能
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": mes.normal_code}


        data= oceandata.getbyid(oceandata, oceandata, int(id_))
        for i in data:
            votenum=i.get('votenum')
            if votenum!=None:
                params={"id":int(id_),"votenum":votenum+1}
                error=oceandata.updatebyparams(oceandata,oceandata,params)
                if error!=None:
                    msg['code'] = crud_error_code
                    msg['msg'] = error
        return JsonResponse(msg)

def oceandata_importExcel(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}

        excel_file = request.FILES.get("file", "")
        if excel_file.size > 100 * 1024 * 1024:  # 限制为 100MB
            msg['code'] = 400
            msg["msg"] = '文件大小不能超过100MB'
            return JsonResponse(msg)

        file_type = excel_file.name.split('.')[1]
        
        if file_type in ['xlsx', 'xls']:
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())
            table = data.sheets()[0]
            rows = table.nrows
            
            try:
                for row in range(1, rows):
                    row_values = table.row_values(row)
                    req_dict = {}
                    if str(row_values[0]) != '':
                        try:
                            date_tuple = xlrd.xldate_as_tuple(row_values[0], 0)
                            date_str = '-'.join([str(i) for i in date_tuple[:-3]])
                            req_dict['date'] = datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
                        except:
                            req_dict['date'] = row_values[0]
                    else:
                        req_dict['date'] = None
                    if str(row_values[1]) != '':
                        req_dict['seasurfacetemperature'] = float(row_values[1])
                    else:
                        req_dict['seasurfacetemperature'] = None
                    if str(row_values[2]) != '':
                        req_dict['salinityofseawaterpsu'] = float(row_values[2])
                    else:
                        req_dict['salinityofseawaterpsu'] = None
                    if str(row_values[3]) != '':
                        req_dict['waveheight'] = float(row_values[3])
                    else:
                        req_dict['waveheight'] = None
                    if str(row_values[4]) != '':
                        req_dict['wavecycle'] = float(row_values[4])
                    else:
                        req_dict['wavecycle'] = None
                    if '.0' in str(row_values[5]):
                        req_dict['wavedirection'] = str(row_values[5]).split('.')[0]
                    elif str(row_values[5]) != '':
                        req_dict['wavedirection'] = row_values[5]
                    else:
                        req_dict['wavedirection'] = None
                    if str(row_values[6]) != '':
                        req_dict['windspeed'] = float(row_values[6])
                    else:
                        req_dict['windspeed'] = None
                    if '.0' in str(row_values[7]):
                        req_dict['winddirection'] = str(row_values[7]).split('.')[0]
                    elif str(row_values[7]) != '':
                        req_dict['winddirection'] = row_values[7]
                    else:
                        req_dict['winddirection'] = None
                    if str(row_values[8]) != '':
                        req_dict['airpressure'] = float(row_values[8])
                    else:
                        req_dict['airpressure'] = None
                    if str(row_values[9]) != '':
                        req_dict['humidity'] = float(row_values[9])
                    else:
                        req_dict['humidity'] = None
                    if str(row_values[10]) != '':
                        req_dict['precipitation'] = float(row_values[10])
                    else:
                        req_dict['precipitation'] = None
                    if str(row_values[11]) != '':
                        req_dict['currentvelocityms'] = float(row_values[11])
                    else:
                        req_dict['currentvelocityms'] = None
                    if '.0' in str(row_values[12]):
                        req_dict['currentdirection'] = str(row_values[12]).split('.')[0]
                    elif str(row_values[12]) != '':
                        req_dict['currentdirection'] = row_values[12]
                    else:
                        req_dict['currentdirection'] = None
                    if str(row_values[13]) != '':
                        req_dict['sealevelheight'] = float(row_values[13])
                    else:
                        req_dict['sealevelheight'] = None
                    if str(row_values[14]) != '':
                        req_dict['depthofunderwater'] = float(row_values[14])
                    else:
                        req_dict['depthofunderwater'] = None
                    if str(row_values[15]) != '':
                        req_dict['seawatertransparency'] = float(row_values[15])
                    else:
                        req_dict['seawatertransparency'] = None
                    if str(row_values[16]) != '':
                        req_dict['acidityandalkalinityofseawaterph'] = float(row_values[16])
                    else:
                        req_dict['acidityandalkalinityofseawaterph'] = None
                    if str(row_values[17]) != '':
                        req_dict['dissolvedoxygeninseawater'] = float(row_values[17])
                    else:
                        req_dict['dissolvedoxygeninseawater'] = None
                    oceandata.createbyreq(oceandata, oceandata, req_dict)
                    
            except:
                pass
                
        else:
            msg = {
                "msg": "文件类型错误",
                "code": 500
            }
                
        return JsonResponse(msg)

def oceandata_autoSort2(request):
    return JsonResponse({"code": 0, "msg": '',  "data":{}})



def oceandata_count(request):
    '''
    总数接口
    '''
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}
        req_dict = request.session.get("req_dict")
        where = ' where 1 = 1 '
        for key in req_dict:
            if req_dict[key] != None:
                where = where + " and key like '{0}'".format(req_dict[key])
        
        sql = "SELECT count(*) AS count FROM oceandata {0}".format(where)
        count = 0
        cursor = connection.cursor()
        cursor.execute(sql)
        desc = cursor.description
        data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()] 
        for online_dict in data_dict:
            count = online_dict['count']
        msg['data'] = count

        return JsonResponse(msg, encoder=CustomJsonEncoder)

# （按值统计）时间统计类型
def oceandata_value(request, xColumnName, yColumnName, timeStatType):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}
        #获取hadoop分析后的数据文件
        date_type = ""
        if timeStatType == '日':
            date_type = "date"
        if timeStatType == '月':
            date_type = "month"
        if timeStatType == '季':
            date_type = "quarter"
        if timeStatType == '年':
            date_type = "year"
        json_filename = f'oceandata_value{xColumnName}{yColumnName}{date_type}.json'

        if os.path.exists(json_filename) == True:
            with open(json_filename, encoding='utf-8') as f:
                msg['data'] = json.load(f)
        else:
            where = ' where 1 = 1 '
            sql = ''
            if timeStatType == '日':
                sql = "SELECT DATE_FORMAT({0}, '%Y-%m-%d') {0}, ROUND(sum({1}),2) total FROM oceandata {2} GROUP BY DATE_FORMAT({0}, '%Y-%m-%d')".format(xColumnName, yColumnName, where, '%Y-%m-%d')

            if timeStatType == '月':
                sql = "SELECT DATE_FORMAT({0}, '%Y-%m') {0}, ROUND(sum({1}),2) total FROM oceandata {2} GROUP BY DATE_FORMAT({0}, '%Y-%m')".format(xColumnName, yColumnName, where, '%Y-%m')

            if timeStatType == '季':
                sql = "SELECT CONCAT(YEAR(MIN({0})), '-Q', QUARTER(MIN({0}))) AS {0}, SUM({1}) AS total FROM orders {2} GROUP BY YEAR({0}), QUARTER({0})".format(xColumnName, yColumnName, where)

            if timeStatType == '年':
                sql = "SELECT DATE_FORMAT({0}, '%Y') {0}, ROUND(sum({1}),2) total FROM oceandata {2} GROUP BY DATE_FORMAT({0}, '%Y')".format(xColumnName, yColumnName, where, '%Y')
            L = []
            cursor = connection.cursor()
            cursor.execute(sql)
            desc = cursor.description
            data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
            for online_dict in data_dict:
                for key in online_dict:
                    if 'datetime.datetime' in str(type(online_dict[key])):
                        online_dict[key] = online_dict[key].strftime(
                            "%Y-%m-%d %H:%M:%S")
                    else:
                        pass
                L.append(online_dict)
            msg['data'] = L
        req_dict = request.session.get("req_dict")
        if "order" in req_dict:
            order = req_dict["order"]
            if order == "desc":
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'],reverse=True)
            else:
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'])

        if "limit" in req_dict and int(req_dict["limit"]) < len(L):
            msg['data'] = msg['data'][:int(req_dict["limit"])]
        return JsonResponse(msg, encoder=CustomJsonEncoder)

# 按值统计
def oceandata_o_value(request, xColumnName, yColumnName):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}
        #获取hadoop分析后的数据文件
        json_filename = f'oceandata_value{xColumnName}{yColumnName}.json'

        if os.path.exists(json_filename) == True:
            with open(json_filename, encoding='utf-8') as f:
                msg['data'] = json.load(f)
        else:
            where = ' where 1 = 1 '
            sql = "SELECT {0}, ROUND(sum({1}),2) AS total FROM oceandata {2} GROUP BY {0}".format(xColumnName, yColumnName, where)
            L = []
            cursor = connection.cursor()
            cursor.execute(sql)
            desc = cursor.description
            data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
            for online_dict in data_dict:
                for key in online_dict:
                    if 'datetime.datetime' in str(type(online_dict[key])):
                        online_dict[key] = online_dict[key].strftime(
                            "%Y-%m-%d %H:%M:%S")
                    else:
                        pass
                L.append(online_dict)
            msg['data'] = L
        req_dict = request.session.get("req_dict")
        if "order" in req_dict:
            order = req_dict["order"]
            if order == "desc":
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'],reverse=True)
            else:
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'])

        if "limit" in req_dict and int(req_dict["limit"]) < len(L):
            msg['data'] = msg['data'][:int(req_dict["limit"])]
        return JsonResponse(msg, encoder=CustomJsonEncoder)

# （按值统计）时间统计类型(多)
def oceandata_valueMul(request, xColumnName, timeStatType):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": []}

        req_dict = request.session.get("req_dict")

        #获取hadoop分析后的数据文件
        date_type = ""
        if timeStatType == '日':
            date_type = "date"
        if timeStatType == '月':
            date_type = "month"
        if timeStatType == '季':
            date_type = "quarter"
        if timeStatType == '年':
            date_type = "year"
        #获取hadoop分析后的数据文件
        json_filename = f'oceandata_value{xColumnName}｛yColumnNameMul.replace(",","")｝{date_type}.json'

        if os.path.exists(json_filename) == True:
            with open(json_filename, encoding='utf-8') as f:
                msg['data'] = json.load(f)
        else:
            where = ' where 1 = 1 '
            for item in req_dict['yColumnNameMul'].split(','):
                sql = ''
                if timeStatType == '日':
                    sql = "SELECT DATE_FORMAT({0}, '%Y-%m-%d') {0}, ROUND(sum({1}),2) total FROM oceandata {2} GROUP BY DATE_FORMAT({0}, '%Y-%m-%d') LIMIT 10".format(xColumnName, item, where, '%Y-%m-%d')

                if timeStatType == '月':
                    sql = "SELECT DATE_FORMAT({0}, '%Y-%m') {0}, ROUND(sum({1}),2) total FROM oceandata {2} GROUP BY DATE_FORMAT({0}, '%Y-%m') LIMIT 10".format(xColumnName, item, where, '%Y-%m')

                if timeStatType == '季':
                    sql = "SELECT CONCAT(YEAR(MIN({0})), '-Q', QUARTER(MIN({0}))) {0}, sum({1}) total FROM oceandata {2} GROUP BY YEAR({0}), QUARTER({0}) LIMIT 10".format(xColumnName, item, where)

                if timeStatType == '年':
                    sql = "SELECT DATE_FORMAT({0}, '%Y') {0}, ROUND(sum({1}),2) total FROM oceandata {2} GROUP BY DATE_FORMAT({0}, '%Y') LIMIT 10".format(xColumnName, item, where, '%Y')

                L = []
                cursor = connection.cursor()
                cursor.execute(sql)
                desc = cursor.description
                data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
                for online_dict in data_dict:
                    for key in online_dict:
                        if 'datetime.datetime' in str(type(online_dict[key])):
                            online_dict[key] = online_dict[key].strftime(
                                "%Y-%m-%d %H:%M:%S")
                        else:
                            pass
                    L.append(online_dict)
                msg['data'].append(L)
        return JsonResponse(msg, encoder=CustomJsonEncoder)

# （按值统计(多)）
def oceandata_o_valueMul(request, xColumnName):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": []}

        req_dict = request.session.get("req_dict")
        #获取hadoop分析后的数据文件
        json_filename = f'oceandata_value{xColumnName}｛yColumnNameMul.replace(",","")｝.json'

        if os.path.exists(json_filename) == True:
            with open(json_filename, encoding='utf-8') as f:
                msg['data'] = json.load(f)
        else:
            where = ' where 1 = 1 '
            for item in req_dict['yColumnNameMul'].split(','):
                sql = "SELECT {0}, ROUND(sum({1}),2) AS total FROM oceandata {2} GROUP BY {0} LIMIT 10".format(xColumnName, item, where)
                L = []
                cursor = connection.cursor()
                cursor.execute(sql)
                desc = cursor.description
                data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
                for online_dict in data_dict:
                    for key in online_dict:
                        if 'datetime.datetime' in str(type(online_dict[key])):
                            online_dict[key] = online_dict[key].strftime(
                                "%Y-%m-%d %H:%M:%S")
                        else:
                            pass
                    L.append(online_dict)
                msg['data'].append(L)
        return JsonResponse(msg, encoder=CustomJsonEncoder)

def oceandata_group(request, columnName):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "成功", "data": {}}

        #获取hadoop分析后的数据文件
        json_filename = f'oceandata_group{columnName}.json'

        if os.path.exists(json_filename) == True:
            with open(json_filename, encoding='utf-8') as f:
                msg['data'] = json.load(f)
        else:
            where = ' where 1 = 1 '
            sql = "SELECT COUNT(*) AS total, " + columnName + " FROM oceandata " + where + " GROUP BY " + columnName
            L = []
            cursor = connection.cursor()
            cursor.execute(sql)
            desc = cursor.description
            data_dict = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
            for online_dict in data_dict:
                for key in online_dict:
                    if 'datetime.datetime' in str(type(online_dict[key])):
                        online_dict[key] = online_dict[key].strftime("%Y-%m-%d")
                    else:
                        pass
                L.append(online_dict)
            msg['data'] = L
        req_dict = request.session.get("req_dict")
        if "order" in req_dict:
            order = req_dict["order"]
            if order == "desc":
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'],reverse=True)
            else:
                msg['data'] = sorted((x for x in msg['data'] if x['total'] is not None),key=lambda x: x['total'])

        if "limit" in req_dict and int(req_dict["limit"]) < len(L):
            msg['data'] = msg['data'][:int(req_dict["limit"])]
        return JsonResponse(msg, encoder=CustomJsonEncoder)









