from app.client.wechat import WeChat
import re,ast
from app.conf import ModuleConf
from app.db.main_db import MainDb
from loguru import logger
from app.db.models import UserAction,Users
from app.utils.command import Command
class Other_Cmd():
    def __init__(self):
        self.WX=WeChat()

    def default(self,user_id,param_dict=None,response_code=None):
        self.WX.send_msg(title="未能识别指令！请检查输入是否有误。", user_id=user_id)
        pass

    def feedback(self,user_id,param_dict,response_code):

        self.WX.send_msg(title="尚在开发，敬请期待！", user_id=user_id)
        pass

    def help(self,user_id,param_dict,response_code):
        string="欢迎使用智慧场馆预约助手，本应用尚在开发中，不能保证稳定运行，本应用可以按照您的设置帮助您在智慧场馆系统中自动预定场地（暂只支持羽毛球场），以下是使用方法介绍：\n \n\
1 概述\n 由于企业微信限制，本应用在微信和企业微信APP上功能略有不同，微信APP上只可通过输入指令进行交互，具体交互指令请点击对应菜单的帮助获得；\
企业微信APP部分功能还可通过企业微信提供的模板卡片进行交互，当有这些功能时，会在前方打“*”以区分。\n \n\
2 个人信息（底部菜单-我的）\n 2.1 添加个人信息\n  按照要求输入指令添加个人信息，包括IAAA登录账号；密码；电话号码；支付方式。关于可能的隐私风险问题，请点击“其他-隐私政策”了解更多信息。\n\
 2.2 *查看&编辑个人信息\n  对个人信息进行查看和编辑。\n 2.3 注销个人信息\n  从数据库中注销个人信息。\n \n\
3 预约场地（底部菜单-预约）\n 3.1 *周常预约\n  预约周一至周日的场地，每周循环预约。\n 3.2 指定日期预约\n  预约指定日期的场地。\n\
 3.3 *查看&编辑预约\n  查看并编辑已有的预约信息\n \n\
4 其他（底部菜单-其他）\n 4.1 使用帮助\n  查看使用帮助\n 4.2 隐私政策\n  查看隐私政策\n 4.3  进行使用反馈"


        self.WX.send_msg(title="【使用帮助】",text=string,user_id=user_id)
        
    def privacy(self,user_id,param_dict,response_code):
        string="由于IAAA登录需求以及技术限制，本应用需要获取您的IAAA账号和密码，在您提交这些信息后，这些信息被RSA加密后储存在后台数据库中，\
其中RSA密钥由应用管理员指定，故理论上有且仅有管理员可以获取您的账号密码。因此，您应当自行部署该应用或选择一名值得信任的应用管理员。\n\
但是由于任何接触到服务端的人都可能通过调试程序、读取内存、网络抓包等等方式获取到应用后台所有数据，或是由于其他未列出的因素导致您的隐私信息泄露，\
故作为开发者，我无法对您的隐私信息安全作出任何保障，亦不对您隐私信息的泄露负责。您应当慎重提交您的IAAA账号和密码，特别是当您不熟悉该应用的部署者和管理员时。\
如您怀疑您的IAAA账号密码已遭泄露，您应当点击底部菜单栏“我的-注销个人信息”在系统中注销您的个人信息，您的所有个人信息和预约信息会在数据库中被彻底删除，\
并且您应该立即修改您的账号密码。\n同时，由于自动预约操作可能导致账号被智慧场馆系统列入风控名单甚至封禁，开发者亦无法为此负责。"

        self.WX.send_msg(title="【隐私政策】",text=string,user_id=user_id)