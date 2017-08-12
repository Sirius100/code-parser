#!/usr/bin/env python3
import sys
import requests
from selenium.webdriver.common.proxy import * # эта бибилиотека нужна ждя пуска мозилы через порт 8080
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from browsermobproxy  import Server, Client # попробую реализовать схему скрипт firefox->browsermobproxy->burpsuite

#=====================================================================================
class BMP_FF():
    """
    Класс для работы браузера Firefox через прокси browsermobproxy
    для перехвата и анализа Get запросов.
    Разобраться как удалять har
    разобраться как удалять экземпляр класса с помощью del
    метод read_data_proxy не реализован
    """
 
    def __init__(self):
        """инициализация настроек браузера Firefox для работы через прокси"""
        #путь прописывать полностью от home до бинарника который скачивается отдельно не через pip install
        self.bmpproxy = Server(r'//home//sirius//project//python_sir//SBBs_sdo//lib//python3.5//site-packages//browsermob-proxy//bin//browsermob-proxy',{'port':8082}) # указываю  путь к  бинарнику и на каком порту слушать трафик
        self.bmpproxy.start() # start browsermobproxy
        self.bmp_port = self.bmpproxy.create_proxy() # назначение порта неизвестно
        self.resp = requests.post('http://localhost:8082/proxy',{}) # отправляю запрос для получения №порта на котором поднял проксик browsermobproxy
        self.browser_port = self.resp.json()['port'] # через этот порт работает браузер
        self.port_ff_net = 'localhost:' + str(self.browser_port) # получаю строку типа "localhost : 8082"

        self.proxy_my_ff = Proxy({
            'proxyType' : ProxyType.MANUAL,
            'httpProxy' : self.port_ff_net,
            'ftpProxy'  : self.port_ff_net,
            'sslProxy'  : self.port_ff_net,
            'socksProxy': self.port_ff_net,
            'noProxy'   : ''
        })
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference("network.proxy.type" , 1)
        self.profile.set_preference("network.proxy.http" , "localhost")
        self.profile.set_preference("network.proxy.http_port" , self.browser_port) 
        self.profile.set_proxy(self.proxy_my_ff)



    def start_firefox_url(self,site_url): #site_url адрес нужного сайта
        """метод вызова браузера с заданными  настройками прокси в
        методе  __init__ и переход на заданный адрес сайта"""
        try:
            self.url = 'http://www.%s' % (site_url)
            self.driver = webdriver.Firefox(self.profile)
            self.resp= requests.put('http://localhost:8082/proxy/' + str(self.browser_port) + '/har', {"initialPageRef": ""})# начинаю сессию мониторинга
            self.driver.get(self.url)
            self.resp = requests.get('http://localhost:8082/proxy/' + str(self.browser_port) + '/har') #read data in har
            sys.stdout.write('порт прокси браузера = ' + str(self.browser_port) + '\n' + 'порт для har = ' + str(self.browser_port) + '\n' )

        except WebDriverException as err:
            print('отработало исключение в методе start_firefox_url')
            self.bmp_stop()
            print('объект уничтожен')

    def start_data_proxy(self):
        """метод выводит какие данные прошли через прокси bmpproxy"""
        self.resp_har = requests.put('http://localhost:8082/proxy/' + str(self.bmp_port.port) + '/har', {"initialPageRef": ""})# начинаю сессию мониторинга
    def read_data_proxy(self):
        self.resp = requests.get('http://localhost:8082/proxy/' + str(self.bmp_port.port) + '/har')
        self.resp.content
        self.resp.json()
        
    def bmp_stop(self):
        """метод отстановки browsermobproxy но порты почему то заняты остаются ((("""
        self.bmpproxy.stop()
        sys.stdout.write('brouwsermobproxy остановлен, объект уничтожен' + '\n')
#======================================================================================
