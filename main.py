# -*- coding: utf8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
import Image
from ocr import*
import time


#-------- <<Edit here>> --------
costype = '103-2-3'


username = 's103xxxx'
password = 'password'

classNO = ["GS415,A","LS212,A"]
classTime = ["108", "311"]

delay = 2
#-------------------------------
#####################by ALitTLeQ

def message(s):
    print unicode(s, 'utf-8')

def isvilid(text):
    if len(text)!=4: return False
    if text.isupper()==False: return False
    for i in text:
        if i.isalnum()==False : return False
    return True


def OCR(browser):
    browser.execute_script('document.getElementById("Panel2").getElementsByTagName("img")[2].style="left:0px;top:0px;position:absolute;";')
    browser.save_screenshot("shot.png")
    im = Image.open("shot.png")
    im.crop( (0, 0, 60, 20) ).save( "captcha.png" )
    captchaer = Captcha("")
    code = captchaer.ocr_png("captcha.png")
    print code
    return code

def login(browser):
    try:
        browser.get('https://isdna1.yzu.edu.tw/CnStdSel/index.aspx')
    
        code = OCR(browser)
        while( isvilid(code)== False):
            browser.refresh()
            code = OCR(browser)
            
        username_text = browser.find_element_by_name('Txt_User')
        password_text = browser.find_element_by_name('Txt_Password')
        cosType_text = browser.find_element_by_name('DPL_SelCosType')
        captcha_text = browser.find_element_by_name('Txt_CheckCode')  # Find the search box
        btn_OK = browser.find_element_by_id('btnOK')
        
        username_text.send_keys(username)
        password_text.send_keys(password)
        cosType_text.send_keys(costype)
        captcha_text.send_keys(code)
        btn_OK.click()

    except Exception:
        time.sleep(delay)
        return False

    try:
        WebDriverWait(browser, 3).until(EC.alert_is_present(),
                                       'Timed out waiting for PA creation ' +
                                       'confirmation popup to appear.')
        alert = browser.switch_to_alert()
        

        print alert.text
        if unicode('為保障全校同學選課之公平性', 'utf-8') in alert.text:
            alert.accept()
            return True
        else:
            alert.accept()
            return False
        #print "alert accepted"
    except TimeoutException:
        print "no alert"
        return False


def waitAlert(browser):
    alert = browser.switch_to_alert()    
    print alert.text
    alert.accept()
    
def ClassInfo( classNo ):
    for s in open('DATA', 'r'):
        if( classNo in s ):
            return s[:-1]
    return None

def AllClassInfo(classNO):
    info = []
    for theClass in classNO:
        result = ClassInfo(theClass)
        if(result != None):
            info.append(result)
            print result
        else:
            message("message: 查無課程資訊 - " + theClass)
            exit()
    return info


if __name__ == '__main__':
    
    browser = webdriver.Firefox()
    browser.implicitly_wait(10) # seconds
    reLogin = True
    while(reLogin):
        #Login
        while(login(browser) == False):
            print "Login Fail! Retry.."
        print "Login Success!"

        #Select Class
        reLogin = False

        message("正在取得課程資料..")
        classInfo = AllClassInfo(classNO)
        try:
            while( reLogin == False ):
                #CosInfo(browser, 'GN212,A')
                #CosInfo
                for index,info in enumerate(classInfo):
                    print info
                    sel = info[7:16]
                    
                    browser.switch_to_frame("CosInfo")
                    browser.execute_script('document.location.href = "https://isdna1.yzu.edu.tw/cnstdsel/SelCurr/CosInfo.aspx?mCosInfo='+sel+'"')
                    try:
                        alert = browser.switch_to_alert()
                        print alert.text
                        alert.dismiss()
                        reLogin = True
                    except NoAlertPresentException :
                        limit = browser.find_element_by_xpath("//td[@class='cls_info_main'][10]").text
                        count = browser.find_element_by_xpath("//td[@class='cls_info_main'][11]").text
                        print count + ' / ' + limit 

                        browser.switch_to.default_content()

                        #LeftCosList
                        if(int(limit) > int(count)):
                            browser.switch_to_frame("LeftCosList")
                            browser.execute_script('document.location.href = "https://isdna1.yzu.edu.tw/CnStdSel/SelCurr/CosList.aspx?schd_time='+classTime[index]+'"')

                            
                            btn = browser.find_element_by_xpath('//input[contains(@id,"'+sel+'")]')        
                            btn.click()

                            classInfo.remove(info);
                
                            waitAlert(browser)
                            waitAlert(browser)
                          
                        browser.switch_to.default_content()

                time.sleep(delay)
        
        except Exception:
            print "Exception!!"
            reLogin = True

    browser.quit()
