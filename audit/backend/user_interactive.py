__author__ = 'Administrator'
from django.contrib.auth import authenticate
# import subprocess,string,random
from audit import models
from audit.backend import session_interactive
class UserShell():
    def __init__(self):
        # self.sys_argv=sys_argv
        self.user=None

    def auth(self):
        i=0
        while i<3:
            print('------进入账户姓名验证-----------')
            username=input('姓名：').strip()
            password=input('密码：').strip()
            user=authenticate(username=username,password=password)
            if not user:
                i=i+1
                print('账密错误')
            else:
                self.user=user
                return True
        else:
            print('最多输入三次')
    def input_token(self):
        i=0
        while i<3:
            token_input=input('请输入token值>>>').strip()
            if len(token_input)==8:
                token_obj=models.Token.objects.filter(val=token_input).first()
                print(token_obj)
                if token_obj:
                    return token_obj
            i+=1
        print('too much try!')

    def start(self):
        token_obj=self.input_token()
        if token_obj:
            user_obj = token_obj.account
            selected_host=token_obj.host_user_bind
            session_interactive.ssh_session(selected_host, user_obj)
        if self.auth():
            host_gruops = self.user.account.host_group.all()
            while True:
                print('---------可登入的服务器组--------')
                # print(self.user.account.host_group.all())
                for index, group in enumerate(host_gruops):
                    print(index, group)
                choice1=input('请选择服务器组：').strip()
                if choice1.isdigit() and int(choice1)<host_gruops.count():
                    selected_group=host_gruops[int(choice1)]
                    print('您选择了   %s组' % selected_group)
                    server_list=selected_group.host_user_binds.all()

                    while True:
                        print('------------可登录的服务器-----------')
                        for index, server in enumerate(server_list):
                            print(index, server)
                        choice2=input('请选择服务器').strip()
                        if choice2.isdigit() and int(choice2)<len(server_list):
                            print('您选择了服务器 %s'%server_list[int(choice2)],'进入下一个界面---->')
                            selected_host=server_list[int(choice2)]
                            user_obj=self.user.account
                            session_interactive.ssh_session(selected_host,user_obj)
                            print(selected_host,selected_host.host.addr,
                                  selected_host.host_user.username,selected_host.host_user.password)

                            # s = string.ascii_lowercase +string.digits
                            # random_tag = ''.join(random.sample(s,10))
                            # session_obj = models.SessionLog.objects.create(account=self.user.account,host_user_bind=selected_host)
                            #
                            # cmd = "sshpass -p %s /usr/local/openssh/bin/ssh %s@%s -p %s -o StrictHostKeyChecking=no -Z %s" \
                            #       %(selected_host.host_user.password, selected_host.host_user.username,selected_host.host.addr, selected_host.host.port, random_tag)
                            # #start strace ,and sleep 1 random_tag, session_obj.id
                            # session_tracker_script = "/bin/sh %s %s %s " %(settings.SESSION_TRACKER_SCRIPT,random_tag,session_obj.id)
                            #
                            # session_tracker_obj =subprocess.Popen(session_tracker_script, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                            #
                            # ssh_channel = subprocess.run(cmd,shell=True)
                            # print(session_tracker_obj.stdout.read(), session_tracker_obj.stderr.read())
                            break
                        elif choice2=='b':
                            break
                elif choice1=='b':
                    break



# class UserShell(object):
#     """用户登录堡垒机后的shell"""
#     print('666666666')
    # def __init__(self,sys_argv):
    #     self.sys_argv = sys_argv
    #     self.user = None
    #
    # def auth(self):
    #
    #     count = 0
    #     while count < 3:
    #         username = input("username:").strip()
    #         password = input("password:").strip()
    #         user = authenticate(username=username,password=password)
    #         #None 代表认证不成功
    #         #user object ，认证对象 ,user.name
    #         if not user:
    #             count += 1
    #             print("Invalid username or password!")
    #         else:
    #             self.user = user
    #             return  True
    #     else:
    #         print("too many attempts.")
    #
    # def start(self):
    #     """启动交互程序"""
    #
    #     if self.auth():
    #         #print(self.user.account.host_user_binds.all()) #select_related()
    #         while True:
    #             host_groups = self.user.account.host_groups.all()
    #             for index,group in enumerate(host_groups):
    #                 print("%s.\t%s[%s]"%(index,group,group.host_user_binds.count()))
    #             print("%s.\t未分组机器[%s]"%(len(host_groups),self.user.account.host_user_binds.count()))
    #
    #             choice = input("select group>:").strip()
    #             if choice.isdigit():
    #                 choice = int(choice)
    #                 host_bind_list = None
    #                 if choice >=0 and choice < len(host_groups):
    #                     selected_group = host_groups[choice]
    #                     host_bind_list = selected_group.host_user_binds.all()
    #                 elif choice == len(host_groups): #选择的未分组机器
    #                     #selected_group = self.user.account.host_user_binds.all()
    #                     host_bind_list = self.user.account.host_user_binds.all()
    #                 if host_bind_list:
    #                     while True:
    #                         for index,host in enumerate(host_bind_list):
    #                             print("%s.\t%s"%(index,host,))
    #                         choice2 = input("select host>:").strip()
    #                         if choice2.isdigit():
    #                             choice2 = int(choice2)
    #                             if choice2 >=0 and choice2 < len(host_bind_list):
    #                                 selected_host = host_bind_list[choice2]
    #                                 print("selected host",selected_host)
    #                         elif choice2 == 'b':
    #                             break


