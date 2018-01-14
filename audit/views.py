from django.shortcuts import render,HttpResponse,redirect
from audit import models
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import json
import string,random
import datetime
from audit import task_handler
from django.conf import settings
import os
from django.views.decorators.csrf import csrf_exempt
# Create your views here.



def auth_login(request):
    if request.method=="GET":
        return render(request,'login.html')
    else:
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(username=username,password=password)
        if user:
            login(request,user)
            return redirect(request.GET.get('next') or '/')
        else:
            error='用户名或密码错误'
            return render(request,'login.html',{'error':error})

@login_required
def auth_logout(request):
    logout(request)
    return redirect('/login/')


@login_required
def index(request):
    # host_group_list=request.user.account.host_group.all()
    # host_list=request.user.account.host_user_bind.all()
    # print(host_group_list,host_list)
    return render(request,'host_list.html')

@login_required
def get_host_list(request):
    gid=request.GET.get('gid')
    if gid=='-1':
        host_list=models.HostUserBind.objects.filter(account=request.user.account).all()
    else:
        host_group_obj=request.user.account.host_group.get(id=gid)
        host_list=host_group_obj.host_user_binds.all()
    data=json.dumps(list(host_list.values('host__hostname','host__addr','host__idc__name','host__port','host_user__username','host_id')))
    return HttpResponse(data)

@login_required
def generate_token(request):
    '前端向后台付出ajax请求，依据hostid，产生一个随机字符串，并记录到数据库中，每次请求进来，删掉五分钟前生成的随机字符串'
    seconds=8*60*60+300
    time_obj = datetime.datetime.now() - datetime.timedelta(seconds=seconds)  # 5mins ago
    models.Token.objects.filter(date__lt=time_obj).delete()   #删掉时间超过5分钟的数据
    host_id=request.POST.get('host_id')
    token_obj=models.Token.objects.filter(host_user_bind__host_id=host_id,date__gt=time_obj).first()
    if token_obj:
        token_data=token_obj.val
    else:
        val= ''.join(random.sample(string.ascii_lowercase + string.digits, 8))
        host_user_bind_obj=models.HostUserBind.objects.filter(host_id=host_id).first()
        models.Token.objects.create(host_user_bind=host_user_bind_obj,account=request.user.account,val=val)
        token_data=val
    return HttpResponse(token_data)

@login_required
def massive_cmd(reuqest):
    '向前端返回页面'
    return render(reuqest,'massive_cmd.html')

@login_required
def massive_process(request):
    '批量命令执行及文件上传'
    task_obj=task_handler.Task(request)
    if task_obj.is_valid():
        task_id=task_obj.run()
        print('task_id',task_id)
        return HttpResponse(json.dumps({'task_id':task_id}))
    return HttpResponse(json.dumps(task_obj.errors))

@login_required
def massive_files(request):
    '向前端返回文件传输页面,同时返回一个随机字符串到前端'
    random_str = ''.join(random.sample(string.ascii_lowercase + string.digits, 8))
    return render(request,'massive_files.html',locals())   #locals()将当前局部变量返回到前端

@login_required
def massive_process_result(request):
    '前端获取批量执行命令的结果'
    task_id=request.GET.get('task_id')
    task_log_objs=models.TaskLog.objects.filter(task_id=int(task_id)).values('result','status',
                                                                             'host_user_bind__host__hostname',
                                                                             'host_user_bind__host__addr').all()
    return_data=list(task_log_objs)
    return HttpResponse(json.dumps(return_data))

@login_required
@csrf_exempt
def file_receive(request):
    '接收文件，命名格式uploads/user_id/random_str/file_name'
    #将random_str传到大的任务内容里，再由批量处理脚本去执行
    file_path='%s/%s/%s'%(settings.FILE_UPLOAD_PATH,request.user.account.id,request.GET.get('random_str'))
    if not os.path.exists(file_path):
        os.makedirs(file_path,exist_ok=True)
    file_obj=request.FILES.get('file')    #获取文件对象
    f=open(os.path.join(file_path,file_obj.name),'wb')
    for chunk in file_obj.chunks():
        f.write(chunk)
    f.close()
    return HttpResponse(json.dumps({'status':0}))

import zipfile
from wsgiref.util import FileWrapper

def send_zipfile(request,task_id,file_path):
    """
    Create a ZIP file on disk and transmit it in chunks of 8KB,
    without loading the whole file into memory. A similar approach can
    be used for large dynamic PDF files.
    """
    zip_file_name = 'task_id_%s_files' % task_id
    archive = zipfile.ZipFile(zip_file_name , 'w', zipfile.ZIP_DEFLATED)
    file_list = os.listdir(file_path)
    for filename in file_list:
        archive.write('%s/%s' %(file_path,filename),arcname=filename)
    archive.close()


    wrapper = FileWrapper(open(zip_file_name,'rb'))
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % zip_file_name
    response['Content-Length'] = os.path.getsize(zip_file_name)
    #temp.seek(0)
    return response

@login_required
def tansfer_file_to_user(request):
    task_id=request.GET.get('task_id')
    file_path=os.path.join(settings.FILE_DOWNLOAD_PATH,task_id)
    response=send_zipfile(request,task_id,file_path)
    return response