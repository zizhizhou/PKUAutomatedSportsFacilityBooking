from app.client.wechat import WeChat
import re,ast
from app.conf import ModuleConf
from app.db.main_db import MainDb
from loguru import logger
from app.db.models import UserAction,Users
from app.utils.command import Command
from app.helper import RsaHelper
class Account_Cmd():
    def __init__(self):
        self.WX=WeChat()
        self.db=MainDb()


    @staticmethod
    def check_account_params(param_dict):
        # appoint_list=["Week","Gym","Field","Time",Status]
        # if param_dict.get("Status"):
        #     appoint_list.append("Status")
        # if param_dict.get("Wechat"):
        #     appoint_list.append("Wechat")
        # if set(param_dict.keys()).issubset(set(appoint_list)):
        try:
            if set(param_dict.get("Week")).issubset(set(ModuleConf.WEEK_MENU.keys())) and \
                set(param_dict.get("Gym")).issubset(set(ModuleConf.GYM_MENU.keys())) and \
                    set(param_dict.get("Field")).issubset(set(ModuleConf.GYM_MENU.keys())) and \
                        set(param_dict.get("Time")).issubset(set(ModuleConf.TIME_MENU.keys())):
                return True

            else:
                return False
        except:
            return False


    @staticmethod
    def check_account(user_id:str):
        """检查是否登录
            0为未登录
            1为已登录
        Args:
            user_id (str): 用户id
        """
        user_info = MainDb().query(Users).filter_by(USERID=user_id).first() 
        if user_info:
            return True
        else:
            return False   
    def view_personal_info(self,  user_id,param_dict,response_code):
        if not Account_Cmd.check_account(user_id):
            self.WX.send_msg(title="您尚未添加个人信息！请先在“我的—添加个人信息”中添加个人信息", user_id=user_id)
            return
        user = self.db.query(Users).filter_by(USERID=user_id).first() 
        string_list=[]
        id=user.ID
        phone=user.PHONE
        account=RsaHelper.decrypt_message(RsaHelper._private_key,user.ACCOUNT)
        pay=ModuleConf.PAY_MENU.get(user.PAY)
        if param_dict.get("Account") or param_dict.get("Password") or param_dict.get("Phone") or param_dict.get("Pay"):
            msg_title="【编辑个人信息】"
            string_list.append("————————————\n")
            if param_dict.get("Account"):
                string_list.append(f"成功修改账号为{param_dict.get('Account')}\n"
                                   "————————————\n")
                user.ACCOUNT=RsaHelper.encrypt_message(RsaHelper._public_key,param_dict.get("Account"))
            if param_dict.get("Password"):
                string_list.append(f"成功修改密码\n"
                                   "————————————\n")
                user.PASSWORD=RsaHelper.encrypt_message(RsaHelper._public_key,param_dict.get('Password'))      
            if param_dict.get("Phone"):
                string_list.append(f"成功修改电话号码为{param_dict.get('Phone')}\n"
                                   "————————————\n")
                user.PHONE=param_dict.get("Phone")       
            if param_dict.get("Pay"):
                string_list.append(f"成功修改支付方式为{ModuleConf.PAY_MENU.get( param_dict.get('Pay'))}\n"
                                   "————————————\n")
                user.PAY=param_dict.get("Pay")   
                self.db.commit()    
        else:
            msg_title="【查看个人信息】"
            string_list.append("————————————\n"
                                f"【ID】：{id}\n"
                                f"【用户名】：{user_id}\n"
                                f"【IAAA账号】：{account}\n"
                                f"【电话号码】：{phone}\n"
                                f"【支付方式】：{pay}\n"
                                f"————————————\n"
                                f"编辑个人信息指令为：\n/Edit_Personal_Info [--Account=<account>] [--Password=<password>] [--Phone=<phone>] [--Pay={0|1|2|3}]\n根据需要选择参数进行修改，没有参数则为查询个人信息\n")
        send_text = "\n".join(string_list)
        self.WX.send_msg(title=msg_title,text=send_text,user_id=user_id)
    def help_personal_info(self,  user_id,param_dict,response_code):
            self.WX.send_msg(title="添加个人信息指令为：\n/Add_Personal_Info --Account=<account> --Password=<password> --Phone=<phone> [--Pay={0|1|2|3}]\n\
其中参数account为IAAA登录账号；password为IAAA登录密码；phone为电话号码；参数Pay为可选，值为0~3，默认为0，0代表不自动支付：预约成功后需自行至智慧场馆中登录；\
1为校园卡自动支付：预约成功后会使用校园卡自动支付；2为微信支付：预约成功后会发送微信付款二维码；3为支付宝支付：预约成功后会发送支付宝付款二维码。\n\
如果需要预约的账号为“12345678”，密码为“12345abcde”，手机号为：“18866669999”，选择支付方式为“校园卡自动支付”，则应输入指令：\n\
/Add_Personal_Info --Account=12345678 --Password=12345abcde --Phone=18866669999 --Pay=1\n\
 注销个人信息指令为：\n/Delete_Personal_Info\n\
查询个人信息指令为：\n/Edit_Personal_Info [--Account=<account>] [--Password=<password>] [--Phone=<phone>] [--Pay={0|1|2|3}]\n根据需要选择参数进行修改，没有参数则为查询个人信息\n\
个人信息帮助指令为：\n/Help_Personal_Info\n\
请按照格式输入指令", user_id=user_id)

    def add_personal_info(self,  user_id,param_dict,response_code):
        if Account_Cmd.check_account(user_id):
            self.WX.send_msg(title="您已添加了个人信息！如需修改，请在“我的—修改个人信息”中修改个人信息", user_id=user_id)
            return
        if len(param_dict)==0:
            self.WX.send_msg(title="添加个人信息之前，您应当点击“其他-隐私政策”阅读并知晓可能的隐私风险，\n\
指令为\n/Add_Personal_Info --Account=<account> --Password=<password> --Phone=<phone> [--Pay={0|1|2|3}]\n\
其中account为IAAA登录账号，password为IAAA登录密码，phone为电话号码，参数Pay为可选，值为0~3，默认为0，0代表不自动支付：预约成功后需自行至智慧场馆中登录；\
1为校园卡自动支付：预约成功后会使用校园卡自动支付；2为微信支付：预约成功后会发送微信付款二维码；3为支付宝支付：预约成功后会发送支付宝付款二维码。\n\
如果需要预约的账号为“12345678”，密码为“12345abcde”，手机号为：“18866669999”，选择支付方式为“校园卡自动支付”，则应输入指令：\n\
/Add_Personal_Info --Account=12345678 --Password=12345abcde --Phone=18866669999 --Pay=1\n请按照格式输入指令", user_id=user_id)
        else:
            # 加密ACCOUNT和PASSWORD
            encrypted_account = RsaHelper.encrypt_message(RsaHelper._public_key, param_dict["Account"])
            encrypted_password = RsaHelper.encrypt_message(RsaHelper._public_key,  param_dict["Password"])
            new_user = Users(
                USERID=user_id,
                PHONE=param_dict["Phone"],
                ACCOUNT=encrypted_account,
                PASSWORD=encrypted_password,
                VERIFY=True,
                PAY='0'
            )
            self.db.insert(new_user)
            self.db.commit()
            user=self.db.query(Users).filter(Users.USERID == user_id).first()
            account=RsaHelper.decrypt_message(RsaHelper._private_key,user.ACCOUNT)
            password=RsaHelper.decrypt_message(RsaHelper._private_key,user.PASSWORD)
            print(f"id:{user.ID},userid:{user.USERID},account:{account},password:{password}")

    def delete_personal_info(self,  user_id,param_dict,response_code):
        if not Account_Cmd.check_account(user_id):
            self.WX.send_msg(title="您尚未添加个人信息！请先在“我的—添加个人信息”中添加个人信息", user_id=user_id)
            return
        user_to_delete = self.db.query(Users).filter_by(USERID=user_id).first()
        self.db.delete(user_to_delete)
        appoints_to_delete = self.db.query(UserAction).filter_by(USERID=user_id).all()
        for appoint_to_delete in appoints_to_delete:
            self.db.delete(appoint_to_delete)
        self.db.commit()
        WeChat().send_msg(title="【注销用户信息】",text="您的所有用户信息和预约已被注销",user_id=user_id)