#处理命令执行及文件上传
import json
from audit import models
import subprocess
from django.conf import settings
from django.db.transaction import atomic
class Task():
    def __init__(self,request):
        self.request=request
        self.task_data=None
        self.errors=[]
    def is_valid(self):
        '验证数据是否有效'
        task_data=self.request.POST.get('task_data')
        if task_data:
            self.task_data=json.loads(task_data)
            if self.task_data.get('task_type')=='cmd':
                if self.task_data.get('cmd') and self.task_data.get("host_id_list"):
                    return True
                self.errors.append({'invalid_argument':'为空的命令或主机列表'})
            elif self.task_data.get('task_type')=='file_transfer':
                return True
            else:
                self.errors.append({'invalid_type':'命令类型不正确'})
        self.errors.append({'invalid_data': '请输入有效数据'})

    def run(self):
        '根据任务类型调用文件上传或命令执行'
        func=getattr(self,self.task_data.get('task_type'))   #基于反射，返回task_id，以便返回前端，让前端去获取任务执行的结果
        task_id=func()
        return task_id

    @atomic
    def cmd(self):
        '批量命令执行'
        task_obj=models.Task.objects.create(task_type=0,content=self.task_data.get('cmd'),
                                            account=self.request.user.account)   #新建一个task,存入到task表中，大任务
        #初始化TaskLog表,即初始化子任务表
        host_id_list=set(self.task_data.get('host_id_list'))
        tasklog_objs=[]

        for host_id in host_id_list:
            tasklog_objs.append(
                models.TaskLog(task=task_obj,
                               host_user_bind_id=int(host_id),
                               status=3)
            )
        models.TaskLog.objects.bulk_create(tasklog_objs,100)  #批量写入到表中，每次写100个
        #使用苏北process开启额外的进程去执行python脚本
        cmd='python %s %s'%(settings.TASK_PROCESS_PATH,task_obj.id)   #传入task_id
        massive_task=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        return task_obj.id    #返回大任务的id

    def file_transfer(self):
        '文件上传'
        task_obj = models.Task.objects.create(task_type=1, content=json.dumps(self.task_data),
                                              account=self.request.user.account)  # 新建一个task,存入到task表中，大任务
        # 初始化TaskLog表,即初始化子任务表
        host_id_list = set(self.task_data.get('host_id_list'))
        tasklog_objs = []

        for host_id in host_id_list:
            tasklog_objs.append(
                models.TaskLog(task=task_obj,
                               host_user_bind_id=int(host_id),
                               status=3)
            )
        models.TaskLog.objects.bulk_create(tasklog_objs, 100)  # 批量写入到表中，每次写100个
        # 使用苏北process开启额外的进程去执行python脚本
        cmd = 'python %s %s' % (settings.TASK_PROCESS_PATH, task_obj.id)  # 传入task_id
        massive_task = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        return task_obj.id  # 返回大任务的id