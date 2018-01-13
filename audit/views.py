from django.shortcuts import render,HttpResponse,redirect
from audit import models
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import json
import string,random
import datetime
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



