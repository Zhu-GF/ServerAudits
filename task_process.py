#批量执行子任务
import paramiko
import sys
import os
import multiprocessing
import json
def cmd_run(tasklog_id,cmd):
    import django
    django.setup()
    from audit import models
    tasklog_obj = models.TaskLog.objects.filter(id=tasklog_id).first()
    try:
        # 建立一个sshclient对象
        ssh = paramiko.SSHClient()
        # 允许将信任的主机自动加入到host_allow 列表，此方法必须放在connect方法的前面
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 调用connect方法连接服务器
        ssh.connect(hostname=tasklog_obj.host_user_bind.host.addr, port=tasklog_obj.host_user_bind.host.port,
                    username=tasklog_obj.host_user_bind.host_user.username,
                    password=tasklog_obj.host_user_bind.host_user.password,
                    timeout=600)
        # 执行命令
        stdin, stdout, stderr = ssh.exec_command(cmd)
        # 结果放到stdout中，如果有错误将放到stderr中
        # print(stdout.read().decode())
        result=stdout.read()+stderr.read()
        # 关闭连接
        ssh.close()
        tasklog_obj.result=result or 'cmd no result back'
        tasklog_obj.status=0
        tasklog_obj.save()
    except Exception as e:
        print(e)
        tasklog_obj.status = 1
        tasklog_obj.result = str(e)
        tasklog_obj.save()

def file_transfer(tasklog_id,task_data):
    import django
    django.setup()
    from audit import models
    from django.conf import settings
    tasklog_obj = models.TaskLog.objects.filter(id=tasklog_id).first()
    print(tasklog_obj.task_id,'task')
    try:
        # 上传文件 1.建立连接
        t = paramiko.Transport((tasklog_obj.host_user_bind.host.addr,tasklog_obj.host_user_bind.host.port))
        t.connect(username=tasklog_obj.host_user_bind.host_user.username,password=tasklog_obj.host_user_bind.host_user.password)
        sftp = paramiko.SFTPClient.from_transport(t)
        task_datas=json.loads(task_data)
        remote_path=task_datas.get('remote_path')
        random_str=task_datas.get('random_str')
        if task_datas.get('transfer_types')=='upload_files':   #上传文件
            local_path=os.path.join(settings.FILE_UPLOAD_PATH,str(tasklog_obj.task.account.id),random_str)
            #local_path='%s/%s/%s'%(settings.FILE_UPLOAD_PATH,tasklog_obj.task.account.id,random_str)
            print(local_path)
            print(remote_path,'远程文件路径')
            for file_name in os.listdir(local_path):
                print(file_name,'file_name')
                sftp.put('%s/%s'%(local_path,file_name),'%s/%s'%(remote_path,file_name))
            tasklog_obj.result='upload files successful....'
        else:
            #从远程下载文件，先下载到堡垒机，再从堡垒机发送到浏览器
            local_download_path='{down_dir}\{task_id}'.format(down_dir=settings.FILE_DOWNLOAD_PATH,task_id=tasklog_obj.task_id)
            if not os.path.exists(local_download_path):
                os.mkdir(local_download_path)
            file_name=os.path.basename(remote_path)
            new_path=os.path.join(local_download_path,(tasklog_obj.host_user_bind.host.addr+'.'+file_name))
            print(new_path)
            sftp.get('%s'%(remote_path), new_path)
            #sftp.get('%s'%(remote_path), '%s/%s/%s'(local_download_path,tasklog_obj.host_user_bind.host.addr,file_name))
            tasklog_obj.result = 'download files %s successful....'%remote_path
        t.close()
        tasklog_obj.status=0
        tasklog_obj.save()
    except Exception as e:
        print(e,'-------')
        import traceback
        traceback.print_exc()
        tasklog_obj.status=1
        tasklog_obj.result=str(e)
        tasklog_obj.save()


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ServerAudits.settings")
    import django
    django.setup()
    from audit import models

    task_id = sys.argv[1]
    task_log_objs=models.TaskLog.objects.filter(task_id=task_id).all()
    task_obj=models.Task.objects.filter(id=task_id).first()
    if task_obj.task_type==0:
        task_func=cmd_run
    else:
        task_func=file_transfer
    pool = multiprocessing.Pool(processes=10)
    for tasklog in task_log_objs:
        pool.apply_async(task_func, args=(tasklog.id, task_obj.content))
    pool.close()
    pool.join()


