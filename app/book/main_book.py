
from os import stat
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as Chrome_Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options as Firefox_Options
import warnings,sys,time,os,traceback,datetime
import multiprocessing as mp
from loguru import logger
from app.book.book_func import Book
from app.utils.exception_utils import *
from app.client.wechat import WeChat
from app.db import MainDb
from app.db.models import Users,UserAction
from app.conf import ModuleConf
from app.helper import RsaHelper
from config.config import Config
warnings.filterwarnings('ignore')

class ParallelAppoint():#并行预约
    def __init__(self,appoint) :
        self.appoint=appoint

    def browser_conf(self):#浏览器设置（目前只支持chrome）
        if Config._browser == "chrome":
            chrome_options = Chrome_Options()
            #chrome_options.add_argument("--headless")
            if sys.platform.startswith('win'):
                executable_path=os.path.join(Config.get_driver_path(),'chromedriver.exe')
            elif sys.platform.startswith('linux'):
                executable_path=os.path.join(Config.get_driver_path(), 'chromedriver.bin')
            self.driver = webdriver.Chrome(
                chrome_options=chrome_options,
                executable_path=executable_path,
                service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1','--ignore-certificate-errors']
                )
            #driver.implicitly_wait(8)
            #,
            #    service_args = ['--ignore-ssl-errors=true', '--ssl-protocol=any']
            logger.debug('chrome launched')
        elif Config._browser == "firefox":
            firefox_options = Firefox_Options()
            firefox_options.add_argument("--headless")
            if sys.platform.startswith('win'):
                executable_path=os.path.join(Config.get_driver_path(),'geckodriver.exe')
            elif sys.platform.startswith('linux'):
                executable_path=os.path.join(Config.get_driver_path(), 'geckodriver')

            self.driver = webdriver.Firefox(
                options=firefox_options,
                executable_path=executable_path
                )
            # 打开一个网页
            self.driver.get('https://www.example.com')

      
            #driver.implicitly_wait(8)
            #,
            #    service_args = ['--ignore-ssl-errors=true', '--ssl-protocol=any']
            logger.debug('firefox launched')
        else:
            logger.error("不支持此类浏览器")
            raise Exception("不支持此类浏览器")   
         
    def appoint_process(self,appoint_time_list,field_num_list):#单次预约场地操作
        self.browser_conf()
        string_list=[]
        try:
            user_account=RsaHelper.decrypt_message(RsaHelper._private_key,self.appoint.users_info.ACCOUNT)
            user_password=RsaHelper.decrypt_message(RsaHelper._private_key,self.appoint.users_info.PASSWORD)
            if self.appoint.status>=1:
                logger.info(f"到达预约准备时间，开始登录操作")
                self.appoint.update_plan()
                Book.login(self.driver, user_account, user_password,self.appoint.appoint_plan_today.GYM)#登录
                while self.appoint.status==1:
                    self.appoint.status,_=self.appoint.judge_begin_appoint_time()                       
            if self.appoint.status==2:
                logger.info(f"到达预约开始时间，开始预约操作")
                book_status,appoint_time_list,field_num=Book.book(self.driver, appoint_time_list,Config._appoint_delay_day, field_num_list,self.appoint.to_do_dict,self.appoint.users_info.USERID,self.appoint.users_info.PHONE)#预约
                if book_status==1:
                    string_list.insert(0,f"本次预约成功！已自动使用校园卡支付。预约结果为：\n"
                                        f"\n————————————\n"
                                        f"【预约账号】：{user_account}\n"
                                        f"【预约场馆】：{self.appoint.gym_name}\n"
                                        f"【预约日期】：{self.appoint.date}\n"
                                        f"【预约时段】：{appoint_time_list}\n"
                                        f"【预约场地】：{field_num}\n"
                                        f"\n————————————\n"
                                        f"本次预约结束\n")  
                else:
                    string_list.insert(0,f"本次预约成功！但是尚未支付！预约结果为：\n"
                                        f"\n————————————\n"
                                        f"【预约账号】：{user_account}\n"
                                        f"【预约场馆】：{self.appoint.gym_name}\n"
                                        f"【预约日期】：{self.appoint.date}\n"
                                        f"【预约时段】：{appoint_time_list}\n"
                                        f"【预约场地】：{field_num}\n"
                                        f"\n————————————\n"
                                        f"如您没有收到支付链接，请在10分钟内在智慧场馆——个人中心——场馆预约——预约记录中支付订单，逾期未支付场地会被自动取消。本次预约结束。\n")                  
        
        except AppointError as e:
            string_list.insert(0,f"本次预约失败！失败原因为：\n"
                    f"预约重试次数超出限制\n"
                    f"本次预约结束")
            #ExceptionUtils.print_exception(e)   
            logger.error(e.args)    
        except WebDriverException as e:
            result="".join(e.args)
            string_list.insert(0,f"本次预约失败！失败原因为：\n"
                    f"{result}")
            ExceptionUtils.print_exception(e)
            logger.error(result)
        except LoginError as e:#判断出错原因
            result="".join(e.args)
            string_list.insert(0,f"本次预约失败！失败原因为：\n"
                    f"IAAA登录失败，请检查账号密码\n"
                    f"本次预约结束")
            logger.error(result)
        except SoldError as e:
            result="".join(e.args)
            string_list.insert(0,f"本次预约失败！失败原因为：\n"
                                f"{result}\n"
                                f"本次预约结束")
            #ExceptionUtils.print_exception(e)
            logger.error(result)
        except Successful as e:
            pass
        except VerifyError as e:
            result="".join(e.args)
            string_list.insert(0,f"本次预约失败！失败原因为：\n"
                                f"验证失败！{result}\n"
                                f"本次预约结束")
            #ExceptionUtils.print_exception(e)
            logger.error(result)        
        except OtherError as e:#判断出错原因
            result="".join(e.args)
            string_list.insert(0,f"本次预约失败！失败原因为：\n"
                    f"{result}")
            #ExceptionUtils.print_exception(e)
            #print(type(e.args))
            logger.error(result)
        except Exception as e:
            ExceptionUtils.print_exception(e)
        finally:
            self.driver.quit()
            text = "\n".join(string_list)
            self.appoint.WX.send_msg(title="【预约结果】 ",text=text,user_id=self.appoint.users_info.USERID)
            time.sleep(360)

        #self.driver.quit()
        """     def judge_begin_appoint_time(self):#将当前时间与时间节点进行对比
                now = datetime.datetime.today()
                str_now=str(now).split()[1][:-7]
                time_hour = datetime.datetime.strptime(
                    str_now, "%H:%M:%S")
                execute_start_time = datetime.datetime.strptime(#预约场地操作开始时间
                    self.appoint.config.execute_start_time, "%H:%M:%S")
                execute_ready_time=execute_start_time - datetime.timedelta(minutes=1)#登录操作开始时间在预约场地操作开始前1分钟
                execute_finish_time = datetime.datetime.strptime(#预约场地结束时间
                    self.appoint.config.execute_finish_time, "%H:%M:%S")
                if  execute_ready_time <= time_hour < execute_start_time:#登录操作
                    return 1,0
                elif execute_start_time <= time_hour < execute_finish_time:#预约场地
                    return 2,0
                else:#睡眠，时长
                    if execute_ready_time > time_hour:#今天还没到预约时间
                        time_difference = execute_ready_time - time_hour
                        seconds_difference = time_difference.total_seconds()
                    elif execute_ready_time < time_hour:#今天过了预约时间，明天预约
                        time_difference = execute_ready_time+datetime.timedelta(hours=24) - time_hour
                        seconds_difference = time_difference.total_seconds() 
                    if seconds_difference>=20:
                        seconds_difference-=10
                    else:
                        seconds_difference=1              
                    return 3,seconds_difference """

class Appoint():
    field_list=[]
    appoint_time_list_now=[]
    date=None
    gym_name=None
    appoint_status=True
    def __init__(self,username) :     
        self.WX=WeChat()   
        self.init_data(username) 

    def init_data(self,username=None):#初始化
        if username!=None:
            self.username=username

        self.db=MainDb()
        self.users_info=self.db.query(Users).filter_by(USERID=self.username).first()        
        self.appoint_plans = self.db.query(UserAction).filter_by(USERID=self.username).all()        
        self.to_do_dict=dict([("verify",self.users_info.VERIFY),("pay",self.users_info.PAY)]) 
        
    def update_plan(self):#更新预约计划
        #self.db
        self.init_data()
        now = datetime.datetime.today()
        today = datetime.datetime.strptime(str(now)[:10], "%Y-%m-%d")
        #appoint_time_list_now = []
        for plan in self.appoint_plans:
            if plan.DATE!=None:#具体日期
                date = datetime.datetime.strptime(
                    plan.DATE, "%Y%m%d")
                delta_day = (date-today).days
            elif plan.WEEKDAY!=None:#周几的格式
                delta_day = (int(plan.WEEKDAY)+6-today.weekday()) % 7
                date = today+datetime.timedelta(days=delta_day)
                date=date.strftime( "%Y-%m-%d")
            if  delta_day == Config._appoint_delay_day:
                self.date=date
                logger.debug(f"{self.date}在预约可预约日期范围内")
                results_weekday = [result for result in self.appoint_plans if result.WEEKDAY == plan.WEEKDAY]
                self.appoint_time_list_now=eval(results_weekday[0].APPOINTTIME)
                break
            else:
                pass
                #logger.debug(f"{date}不在预约可预约日期范围内")        
        self.appoint_plan_today=self.db.query(UserAction).filter_by(USERID=self.username,WEEKDAY=plan.WEEKDAY).first()
        self.gym_name=ModuleConf.GYM_MENU.get(self.appoint_plan_today.GYM).get("name")
        self.field_list=eval(self.appoint_plan_today.FIELD)
        if len(self.appoint_time_list_now) == 0:#今日无需预约
            self.appoint_status=False
            logger.warning("目前预约时间表中没有可预约的时段")
        #self.appoint_plans=self.db.query(UserAction).filter_by(USERID=self.username).all()

    def sys_path(self):#配置设置（暂时没用）
        path = 'driver'
        if Config._browser == "chrome":
            if sys.platform.startswith('win'):
                return os.path.join(path, 'chromedriver.exe')
            elif sys.platform.startswith('linux'):
                return os.path.join(path, 'chromedriver.bin')
            else:
                raise Exception('不支持该系统')
        elif Config._browser == "firefox":
            if sys.platform.startswith('win'):
                return os.path.join(path, 'geckodriver.exe')
            elif sys.platform.startswith('linux'):
                return os.path.join(path, 'geckodriver.bin')
            else:
                raise Exception('不支持该系统')

    def judge_begin_appoint_time(self):#将当前时间与时间节点进行对比
        now = datetime.datetime.today()
        str_now=str(now).split()[1][:-7]
        time_hour = datetime.datetime.strptime(
            str_now, "%H:%M:%S") 
              
        execute_start_time = datetime.datetime.strptime(#预约场地操作开始时间
            Config._execute_start_time, "%H:%M:%S")
        execute_ready_time=execute_start_time - datetime.timedelta(seconds=30)#登录操作开始时间在预约场地操作开始前30秒
        notice_time=execute_start_time - datetime.timedelta(minutes=5)#通知时间在预约场地操作开始前5分钟
        execute_finish_time = datetime.datetime.strptime(#预约场地结束时间
            Config._execute_finish_time, "%H:%M:%S")
        
        if  execute_ready_time <= time_hour < execute_start_time:#登录操作
            return 1,0
        elif execute_start_time <= time_hour < execute_finish_time:#预约场地
            return 2,0
        elif notice_time <= time_hour < execute_ready_time:#五分钟前微信通知
            time_difference=execute_ready_time-time_hour
            seconds_difference = time_difference.total_seconds()
            if seconds_difference>=15:
                seconds_difference-=5
            else:
                seconds_difference=1
            return 4,seconds_difference
        else:#离开始还有很久，睡眠操作，返回睡眠时长（秒）
            if notice_time > time_hour:#今天还没到预约时间
                time_difference = notice_time - time_hour
                seconds_difference = time_difference.total_seconds()
            elif execute_finish_time < time_hour:#今天过了预约时间，明天预约
                time_difference = execute_finish_time+datetime.timedelta(hours=24) - time_hour
                seconds_difference = time_difference.total_seconds() 
            if seconds_difference>=20:
                seconds_difference-=10
            else:
                seconds_difference=1              
            return 3,seconds_difference
   
    def appoint_func(self):#预约操作      
        notice_flag=0
        while True:                       
            self.status,sleep_time=self.judge_begin_appoint_time()
            if self.status==3:#休眠
                target_time = datetime.datetime.today()+datetime.timedelta(seconds=sleep_time)
                logger.info(f"尚未到达预约开始时间，休眠至{target_time}")
                time.sleep(sleep_time)
                continue
            else:#准备开始预约     
                self.update_plan()
                if not self.appoint_status:#今日无需预约
                    #logger.warning("目前预约时间表中没有可预约的时段")
                    time.sleep(3600)
                    continue
                else:
                    if self.status==4:#通知
                        if notice_flag==0:
                            string_list=[]
                            account=RsaHelper.decrypt_message(RsaHelper._private_key,self.users_info.ACCOUNT)
                            string_list.insert(0,f"将于5分钟后开始预约日期为{self.date}的场地，您的预约方案为：\n"
                                               f"\n————————————\n"
                                               f"【预约账号】：{account}\n"
                                               f"【预约场馆】：{self.gym_name}\n"
                                               f"【预约时段】：{self.appoint_time_list_now}\n"
                                               f"【预约场地】：{self.appoint_plan_today.FIELD}\n"
                                               f"【支付方式】：{ModuleConf.PAY_MENU.get(self.users_info.PAY)}\n"
                                               f"\n————————————\n"
                                               f"本日预约方案将在开始预约前1分钟锁定，如有变更请尽快修改。")
                            text = "\n".join(string_list)
                            self.WX.send_msg(title="【预约提醒】 ",text=text,user_id=self.users_info.USERID)
                            notice_flag=1
                        time.sleep(sleep_time)
                    else:#开始预约
                        self.multi_run(Config._mode)
                        time.sleep(60)
                        notice_flag=0

    def multi_run(self,mode):
        if mode==0:#单进程预约
            ParallelAppoint(self).appoint_process(self.appoint_time_list_now,self.field_list)
        elif mode==1:#多进程预约每个时段
            pool = mp.Pool(processes = 2)
            for appoint_time_now in self.appoint_time_list_now:
                pool.apply_async(ParallelAppoint(self).appoint_process, ([appoint_time_now],self.field_list))
            pool.close()
            #pool.join()
        elif mode==2:#多进程预约每个时段*每个场地
            pool=mp.Pool(processes = 30)
            for field_num in self.field_list:
                for appoint_time_now in self.appoint_time_list_now:
                    pool.apply_async(ParallelAppoint(self).appoint_process, ([appoint_time_now],[field_num]))
            pool.close()
            #pool.join()



