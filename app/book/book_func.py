from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import quote
from app.helper import Ddddocr
from app.utils.exception_utils import *
from loguru import logger
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from app.conf import ModuleConf
from app.client.wechat import WeChat
from PIL import Image
import time,datetime,warnings,random,re,sys,base64

warnings.filterwarnings('ignore')
class text_to_be_present_in_element_partial(object):
    def __init__(self, locator, text):
        self.locator = locator
        self.text = text

    def __call__(self, driver):
        try:
            element_text = driver.find_element(*self.locator).text
            return self.text in element_text
        except Exception as e:
            return False
        
class Book():
    @staticmethod
    def login(driver, user_name, password,venue):#登录IAAA
        try:
            login_retry=0
            while login_retry<=3:#尝试三次
                
                login_retry+=1
                if login_retry == 3:
                    raise LoginError('IAAA登录失败')
                driver.get(
                    'https://epe.pku.edu.cn/ggtypt/login?service=https://epe.pku.edu.cn/venue-server/loginto')
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, 'logon_button')))
                driver.find_element_by_id('user_name').send_keys(user_name)#填写密码登录
                driver.find_element_by_id('password').send_keys(password)
                driver.find_element_by_id('logon_button').click()
                try:
                    WebDriverWait(driver,
                                5).until(EC.visibility_of_element_located((By.ID, 'homePage')))#判断有没有进主页
                    logger.info('IAAA登录成功')
                    try:
                        if driver.current_url !=ModuleConf.GYM_MENU.get(venue).get("url"):
                            driver.get(ModuleConf.GYM_MENU.get(venue).get("url"))#进场地预约页面
                        WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/table')))
                        gym_name=ModuleConf.GYM_MENU[venue]["name"]
                        logger.debug(f"成功进入预约 {gym_name} 界面" )
                        break                   
                    except:
                        logger.warning(f"尝试进入预约 {gym_name} 界面失败" )
                        continue
            
                except:
                    logger.warning(f'尝试IAAA登录失败，刷新网页重试，第{login_retry}/2次' )
                    driver.get(
                        'https://epe.pku.edu.cn/ggtypt/login?service=https://epe.pku.edu.cn/venue-server/loginto')#刷新网页
                    continue
        except:
            raise OtherError("登录出现其他故障")

    @staticmethod
    def make_appoint(driver,appoint_time_list,delta_day,book_field_num_list,verify_falg,phone):#预约某个体育馆的场地

        #try:
        check_free=[]
        for appoint_time in appoint_time_list:
            check_free.append(Book.click_free(driver,appoint_time, book_field_num_list))#迭代器，选择下一个空闲场地

        try:
            field_chosen=Book.choose_field(driver,delta_day,appoint_time_list,book_field_num_list,check_free)#生成迭代器
            while True:
                status,filed_num=next(field_chosen)
                if not status:
                    break
                try:
                    if Book.submit_appoint(driver,phone):
                        if verify_falg: #需要验证
                            if Book.submit_verify(driver):  #验证                   
                                return True,filed_num   #验证通过
                            else:#验证失败，应该重新选场
                                #retry+=1
                                continue
                        else:#无需验证
                            return True,filed_num   
                except VerifyError as e:#向上传递
                    raise VerifyError(e.args)
                except OtherError as e:
                    raise OtherError(e.args)
                except Exception as e:
                    ExceptionUtils.print_exception(e)
                    logger.warning(f"尝试订{appoint_time_list}时段的{filed_num}号场失败" )
                    driver.refresh()#刷新网页
                    return False,0#重试全部失败了，只能刷新页面                     
        except VerifyError as e:#向上传递
            raise VerifyError(e.args)
        except OtherError as e:
            raise OtherError(e.args)
        except (RuntimeError,StopIteration):
            
            raise SoldError(f"所选时段{appoint_time_list}没有空余场地，本次预约任务结束") #直接退出，本次的预约任务结束       
        except NoSuchElementException:
            driver.refresh()
            return False,0#重试全部失败了，只能刷新页面


    @staticmethod
    def choose_field(driver,delta_day,appoint_time_list,book_field_num_list,check_free=[]):#选定单日所需场地（需修改）#迭代器

        status=0
        WebDriverWait(driver, 10).until(#确定表格加载出来了
                    EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]")))
        if not Book.move_to_date(driver,delta_day):#选择正确的日期
            return 0 
        if len(check_free)==0:
            for appoint_time in appoint_time_list:
                check_free.append(Book.click_free(driver,appoint_time, book_field_num_list))#迭代器，选择下一个空闲场地
        while True:  
            try:    
                choose=[]
                for check in check_free:
                    check_status,field_num=next(check)
                    choose.append(field_num)
                yield 1,choose 
            except StopIteration:
                return False,0
      
    @staticmethod
    def move_to_time(driver,appoint_time):#切换到正确的时间
        WebDriverWait(driver, 10).until(#确认表格表项出现
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/table/tbody/tr[4]")))

        row_len = len(driver.find_element_by_xpath(
            "/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/table/thead/tr")\
                .find_elements_by_tag_name('td'))        
        table_begin_hour=int(driver.find_element_by_xpath(#表格开始时间
            "/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/table/thead/tr/td[2]/div")\
                .text[0:2])
        table_end_hour=int(driver.find_element_by_xpath(#表格结束时间
            f"/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/table/thead/tr/td[{row_len}]/div")\
                .text[6:8])
        if appoint_time.hour<table_begin_hour:#预约时间不在表格范围内
            try:
                driver.find_element_by_class_name('pull-left').click()
            except:
                return 0
            return  Book.move_to_time(driver,appoint_time)
                
        elif appoint_time.hour>=table_end_hour:#预约时间不在表格范围内
            try:
                driver.find_element_by_class_name('pull-right').click()
            except:
                return 0
            return  Book.move_to_time(driver,appoint_time)
        else:#预约时间在表格范围内
            return 1
    
    @staticmethod
    def click_free(driver,appoint_time,  field_num_list):#按列表顺序选择场地和时间
        #for appoint_time in appoint_time_list:#循环订单日场，优先抢到所有场地  
        appoint_time_num = datetime.datetime.strptime(appoint_time, "%H:%M")
        Book.move_to_time(driver,appoint_time_num)#左右移动表格到正确的时间
        WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/table/tbody/tr[3]")))
        title_row=driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/table/thead/tr')
        column_len=len(title_row.find_elements_by_tag_name('td'))
        for column_num in range(1,column_len+1):#判断在哪一列
            if driver.find_element_by_xpath(
                f"/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/table/thead/tr/td[{column_num}]/div")\
                    .text[0:5]==appoint_time:
                break
            else:
                continue
        
        free_fields={}#获取当前列空闲场地
        column_len = len(driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/table/tbody')\
                .find_elements_by_tag_name('tr'))
        for field_num in range(1,column_len):
            try:
                field=driver.find_element_by_xpath(
                    f'/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/table/tbody/tr[{int(field_num)}]/td[{column_num}]/div/div/span')
            except:
                field=driver.find_element_by_xpath(
                f'/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/table/tbody/tr[{int(field_num)}]/td[{column_num}]/div/div/p')
            if len(field.text)!=0 and field.text[0]=="￥":
                free_field=driver.find_element_by_xpath(
                    f'/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/table/tbody/tr[{int(field_num)}]/td[{column_num}]/div')
                if free_field.get_attribute("class")=="reserveBlock position free selected":#如果场地被自己选中了，就再点击一次取消掉
                    free_field.click()
                free_fields[field_num]=field
                #free_fields.append(field)
            elif len(field.text)==0:#没有空闲场地
                continue
            else:
                continue                    
        if len(free_fields)==0:
            return False,0
        if field_num_list==[]:#随机
            free_fields_keys=list(free_fields.keys())
            random.shuffle(free_fields_keys)#打乱
            random_free_fields = {}
            for key in free_fields_keys:
                random_free_fields[key] = free_fields.get(key)

            for field_num,field in random_free_fields.items():
                if field.text[0]=="￥":
                    field.click()
                    logger.info(f"选择{appoint_time}空闲场地，场地编号为{field_num}")
                    yield True, field_num
                    field.click()
                else:
                    continue                    
        else:#非随机
            for field_num in field_num_list:                 
                field=driver.find_element_by_xpath(
                    f'/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div/table/tbody/tr[{int(field_num)}]/td[{column_num}]/div')           
                if len(field.text)!=0 and field.text[0]=="￥":
                    field.click()
                    logger.info(f"选择{appoint_time}空闲场地，场地编号为{field_num}")
                    yield True, field_num
                    field.click()
                else:
                    continue
        return False, 0

    @staticmethod
    def move_to_date(driver,delta_day):#切换到正确的日期页面
        retry=0
        while retry<=3:
            try:
                right_date=driver.find_element_by_xpath(
                    f'/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[1]/div[2]/div[{delta_day+1}]')
                right_date.click()
                if right_date.get_attribute("class")=="active":
                    return 1
                else:
                    return 0
            except Exception as e:
                retry+=1
                continue
        return 0
        #if right_date.get_attribute("class")=="active":
        #    return 1
        #else:
        #    return 0

    @staticmethod
    def submit_appoint(driver,phone):#提交预约表单
        appoint_notice=driver.find_element_by_xpath(
                '/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[5]/div[1]/label/span')
        if(appoint_notice.get_attribute('class')=="ivu-checkbox"):#没有点击”阅读并同意《预约须知》
            appoint_notice.click()
        phone_input=driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[4]/div[2]/form/div[1]/div/div/div/div/div/input')
        if not phone_input.get_attribute("value"):#填写电话号码
            phone_input.send_keys(phone)
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "ivu-checkbox-checked")))
        submit=driver.find_element_by_xpath(
                '/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[5]/div[2]/div[1]')       
        if(submit.get_attribute('class')=="btn" ):
            submit.click()
        logger.debug("提交预约")
        return True

    @staticmethod   
    def submit_verify(driver):#点击验证码
        refresh_nums=0#刷新验证码次数，最多三次，避免刷新太多被封
        appoint_notice="test"
        while refresh_nums<=10:
            refresh_nums+=1
            #if refresh_nums>=
            if refresh_nums==10:
                logger.warning("验证码刷新次数达到5次，刷新重试")
                driver.find_element_by_xpath(
                    '/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[4]/div[3]/div/div[1]/span').click()
                return False
                raise VerifyError("验证码刷新次数达到5次")
            try:#尝试抓提示框
                hint=driver.find_element_by_xpath('/html/body/div[17]/div[2]/div/div/div/div/div[2]/div')
                logger.error(hint.text)
                #driver.find_element_by_xpath('/html/body/div[17]/div[2]/div/div/div/div/div[3]/button').click()
                return False #此时验证码已经没了,只能重新选场地再试一次
            except NoSuchElementException as e:#没抓到提示框
                pass  
            try:         
                WebDriverWait(driver, 5).until(#等验证码图片刷新出来
                    EC.visibility_of_element_located((By.XPATH,
                                                    "/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[4]/div[3]/div/div[2]/div/div[2]/span")))
                WebDriverWait(driver, 5).until(#验证码刷新出来
                        EC.text_to_be_present_in_element((By.XPATH,
                                                        '/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[4]/div[3]/div/div[2]/div/div[2]/span'),"请依次点击"))
                WebDriverWait(driver, 5).until_not(
                    EC.text_to_be_present_in_element((By.XPATH,
                                                    "/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[4]/div[3]/div/div[2]/div/div[2]/span"),appoint_notice))
            except TimeoutException:
                text="验证出错"
                try:#尝试抓提示框（验证码次数超出限制）
                    hint=driver.find_element_by_xpath('/html/body/div[17]/div[2]/div/div/div/div/div[2]/div')
                    logger.error(hint.text)
                    text=hint.text
                    #driver.find_element_by_xpath('/html/body/div[17]/div[2]/div/div/div/div/div[3]/button').click()
                    return False #此时验证码已经没了,只能重新选场地再试一次
                except NoSuchElementException as e:#没抓到提示框
                    pass
                finally:
                    raise VerifyError(text) 
            appoint_notice=driver.find_element_by_xpath(
                '/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[4]/div[3]/div/div[2]/div/div[2]/span').text
            pattern=re.compile('.【(.+)】')
            verify_words=pattern.findall(appoint_notice)#获取待点击汉字     
            verify_word=verify_words[0].split(",")

            image=driver.find_element_by_xpath(#获取验证图片
                "/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[4]/div[3]/div/div[2]/div/div[1]/div/img")
            image_base64_data=image.get_attribute('src')
            img_str = image_base64_data.split(",")[-1] # 删除前面的 “data:image/jpeg;base64,”
            img_str = img_str.replace("%0A", '\n')  # 将"%0A"替换为换行符
            image_ocr = Ddddocr().get_img_xy(base64.b64decode(img_str))
            flag = True
            hans_code=image_ocr.keys()
            for hans_code in verify_word:#是否在验证码内
                if hans_code not in image_ocr.keys():#验证码识别错误,刷新验证码重试
                    driver.find_element_by_xpath(
                        '/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[4]/div[3]/div/div[2]/div/div[1]/div/div').click()
                    #time.sleep(1)
                    flag = False
                    break                   
            if not flag:
                continue
            else:
                for hans_code in verify_word:#确定了都是对的
                    flag = True
                    code_x, code_y = image_ocr[hans_code]              
                    ActionChains(driver).move_to_element_with_offset(image, code_x, code_y).click().perform()
                    time.sleep(random.uniform(0.1, 0.3))
                try:
                    WebDriverWait(driver, 5).until(#验证失败，立即重试
                    EC.text_to_be_present_in_element((By.XPATH,
                                                    '/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[4]/div[3]/div/div[2]/div/div[2]/span'),"验证失败"))
                    #WebDriverWait(driver, 5).until(#验证失败，立即重试
                    #text_to_be_present_in_element_partial((By.XPATH, ' /html/body/div[17]/div[2]/div/div/div/div/div[2]/div'),"验证失败"))
                                                                   
                    logger.warning("验证失败")
                    continue
                except:#可能是成功的，但是需要进一步排除错误
                    try:#尝试抓提示框
                        WebDriverWait(driver, 5).until(#等提示框刷新出来
                                        EC.visibility_of_element_located((By.XPATH,
                                                                        "/html/body/div[17]/div[2]/div/div/div/div/div[2]/div")))
                        hint=driver.find_element_by_xpath('/html/body/div[17]/div[2]/div/div/div/div/div[2]/div')                           
                        logger.error(hint.text)
                        if hint.text=="该场地已被其他人预约，请更换场地或时间后再预约！":
                            driver.find_element_by_xpath('/html/body/div[17]/div[2]/div/div/div/div/div[3]/button/span').click()
                            WebDriverWait(driver, 5).until_not(#等提示框消失
                                            EC.visibility_of_element_located((By.XPATH,                                                                              
                                                                            '/html/body/div[17]/div[2]/div/div/div/div/div[3]/button/span')))                           
                            return False #此时验证码已经没了,只能重新选场地再试一次
                        else:#其他错误
                            driver.find_element_by_xpath('/html/body/div[17]/div[2]/div/div/div/div/div[3]/button').click()  
                            #WebDriverWait(driver, 5).until_not(#等提示框消失
                            #                EC.visibility_of_element_located((By.XPATH,
                            #                                                '/html/body/div[17]/div[2]/div/div/div/div/div[3]/button/span')))
                            #return False
                            raise OtherError(hint.text)                            
                            pass
                    except TimeoutException:#没有提示框
                        try:#判断有没有新窗口弹出  
                            current_handles = driver.window_handles
                            WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))#如果打开了新窗口                     
                            logger.success("验证成功")
                            break#没选错所以超时，验证完成                                                  
                        except TimeoutException as e:#没新窗口弹出  
                            pass
                        
                        continue      
        return True

    @staticmethod
    def book(driver, appoint_time_list,  delta_day, book_field_num_list=[],to_do_dict={"verify":True,"pay":False},user_id=None,phone=None):#预定场地
        book_retry=0
        while book_retry<=16:
            book_retry+=1
            if book_retry==16:
                logger.error("预约重试次数超出限制")
                raise AppointError("预约重试次数超出限制")
            appoint_flag,field_num=Book.make_appoint(driver,appoint_time_list,delta_day,book_field_num_list,to_do_dict["verify"],phone)

            if appoint_flag:
                if not to_do_dict["verify"]:
                    logger.success(f"{appoint_time_list}时段{field_num}号场地预定成功，需要手动填写验证码") 
                    time.sleep(360)
                else:
                    if to_do_dict["pay"]=="1":#校园卡自动支付
                        if Book.pay(driver):
                            logger.success(f"{appoint_time_list}时段{field_num}号场地预定且支付成功") 
                            return 1,appoint_time_list,field_num
                    elif to_do_dict["pay"]=="0":                    
                        logger.success(f"锁定{appoint_time_list}时段{field_num}号场地成功但订单尚未支付，请在10分钟内在智慧场馆——个人中心——场馆预约——预约记录中支付订单，\
                                    逾期未支付场地会被自动取消")
                        return 0,appoint_time_list,field_num                       
                    else:
                        logger.success(f"锁定{appoint_time_list}时段{field_num}号场地成功，用户选择第三方支付")
                        Book.third_party_pay(driver,to_do_dict["pay"],user_id)
                        return 2,appoint_time_list,field_num
                break     
                
    @staticmethod
    def pay(driver):#支付
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)
        WebDriverWait(driver, 5).until(
                    EC.text_to_be_present_in_element((By.XPATH,
        '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[2]/div[1]'),"支付"))
        driver.find_element_by_xpath(#默认使用校园卡支付            
            '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[1]/div[2]/div/div[1]/div[1]').click()
        time.sleep(0.5)       
        driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[2]/div[1]').click()
        logger.success("支付成功")
        return True
    
    @staticmethod
    def third_party_pay(driver,mode,user_id):
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)
        WebDriverWait(driver, 5).until(
                    EC.text_to_be_present_in_element((By.XPATH,
        '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[2]/div[1]'),"支付"))
        driver.find_element_by_xpath(#默认使用校园卡支付            
            '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[1]/div[2]/div/div[1]/div[2]').click()
        time.sleep(0.5)       
        driver.find_element_by_xpath(
            '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[2]/div[1]').click()
        time.sleep(0.5) 
        driver.switch_to.window(driver.window_handles[-1])
        if mode=="2":#微信支付
            driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[3]/label[1]/div').click()
            pass
        elif mode==3:#支付宝支付
            driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[3]/label[2]/div').click()
        time.sleep(0.5)
        driver.find_element_by_xpath(
        '/html/body/div[2]/div/div[2]/div[4]').click()#立即支付
        time.sleep(0.5)
        driver.execute_script("window.scrollTo(document.body.scrollWidth, 0);")
        time.sleep(0.5)
        driver.find_element_by_xpath(
        '/html/body/div[2]/div/div[2]/div[3]/div[2]').screenshot("element_screenshot.png")#截图二维码
        image = Image.open("element_screenshot.png")
        # 将图像转换为Base64格式
        image_bytes = image.tobytes()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        string_list=[]
        string_list.insert(0,f"请您在十分钟内将下方链接复制到浏览器中打开，选择支付方式后截图获得二维码，用对应的支付软件扫码支付。不要在微信中直接点击链接支付："
                            f"也可以在智慧场馆——个人中心——场馆预约——预约记录中支付订单，逾期未支付场地会被自动取消"
                            f"\n————————————\n"
                            f"【支付链接】：\n"
                            f"{driver.current_url}\n"
                            f"\n————————————\n")
        text = "\n".join(string_list)
        WeChat().send_msg(title="【支付场地费用】",text=text,user_id=user_id)
        #logger.success("支付成功")
        return True


