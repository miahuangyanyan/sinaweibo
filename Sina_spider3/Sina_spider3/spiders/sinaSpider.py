# encoding=utf-8
# ------------------------------------------
#   版本：3.0
#   日期：2016-12-01
#   作者：九茶<http://blog.csdn.net/bone_ace>
# ------------------------------------------

import sys
import logging
import datetime
import requests
import re
import json
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.keys import  Keys
import  selenium.webdriver.support.ui as ui
from selenium.webdriver.common.action_chains import  ActionChains
import time

from Sina_spider3.weiboID import weiboID
from Sina_spider3.scrapy_redis.spiders import RedisSpider
from scrapy.selector import Selector
from scrapy.http import Request
from Sina_spider3.items import TweetsItem, InformationItem, RelationshipsItem
import urllib
import scrapy
from urllib import urlencode

reload(sys)
sys.setdefaultencoding('utf8')


class Spider(RedisSpider):
    name = "SinaSpider"
    # host = "https://weibo.cn"
    redis_key = "SinaSpider:start_urls"
    start_urls = list(set(weiboID))
    logging.getLogger("requests").setLevel(logging.WARNING)  # 将requests的日志级别设成WARNING

    def start_requests(self):
        # for uid in self.start_urls:
        #     yield Request(url="https://weibo.cn/%s/info" % uid, callback=self.parse_information)

        country = ['401', '400', '402', '403', '404']
        year = ['2016', '2017', '2015', '2014', '2013']
        headers={'Content-Type':'application/x-www-form-urlencoded','Referer':'http://movie.weibo.com/movie/web/category',
                'X - Requested - With':'XMLHttpRequest'}
        try:
            for year_ in year:
                 for country_ in country:
                   for  page_ in range (50):
                    params = {'type': 0, 'year': year_, 'country': country_, 'page': page_}
                    response=requests.post('http://movie.weibo.com/movie/webajax/category',headers=headers, data=params)
                    #print response.text.decode('unicode_escape')
                    # print response.text
                    info = response.json()['data']['list']
                    if len(info) == 0:
                        break
                    for info_ in info:
                        film_id = info_['film_id']
                        name = info_['name']
                        print film_id
                        print name
                        request_url="http://weibo.com/p/100120"+str(film_id)
                        print 'my_request_url: ' + request_url
                        yield  Request(url= request_url,callback=self.parse_detail)
                        # request_url = ""

        except:
            print('Connection Error!')
    def parse_detail(self,response):
        selector = Selector(response)
        item = InformationItem()
        text1 = selector.xpath("/html/script[8]/text()").extract()
        print text1

    def movie_number_summary(self, response):
        print 'move_number_summary'
        #print response.text
        selector = Selector(response)
        #text = selector.xpath("/html/script[contains(., '"domid": "Pl_Core_T8CustomTriColumn__16"')]/text()").re(r'(?ms)FM\.view\((\{.*?\})\)')
        text = selector.xpath("/html/script").re(r'(?ms)FM\.view\((\{.*?\})\)')
        for x in text:
            fm = json.loads(x)
            if fm['domid'] == 'Pl_Core_T8CustomTriColumn__16':
                html = fm['html']
                tree = etree.HTML(html)
                #print etree.tostring(tree)
                list_reg = '//strong/text()'
                lst = tree.xpath(list_reg)
                focus_num, comment_num, play_num = lst
                print '********************foucus_num: ' + focus_num
                print '********************comment_num: ' + comment_num
                print '********************play_num: ' + play_num
                break
        #text = json.loads(text[0].encode('utf-8'))['html']
        #print 'html: ' + text

    def public_comment_from_root(self, response):
        print 'public_comment_from_root'
        self.movie_number_summary(response)
        selector = Selector(response)
        #print response.text
        text = selector.xpath("/html/script[contains(., 'pids=Pl_Core_MixedFeed__12')]/text()").re(r'(?ms)FM\.view\((\{.*?\})\)')[0]
        text = json.loads(text.encode('utf-8'))['html']
        url = self.more_comment_from_root(text)
        if url == '':
            print 'url is null, start get_start'
            for x in  self.get_star(text):
                yield x
            self.get_small_comment(text)
        else:
            print 'url is not null, send into Request'
            yield  Request(url = url, callback=self.parse_detail)

    def public_comment_review_page(self, response, page):
        print 'public_comment_review_page==================================================='
        selector = Selector(response)
        text = selector.xpath("/html/script[contains(., 'pids=Pl_Core_MixedFeed__57')]/text()").re(r'(?ms)FM\.view\((\{.*?\})\)')[0]
        text = json.loads(text.encode('utf-8'))['html']
        for x in self.get_star(text):
            yield x
        self.get_small_comment(text)
        page_text = selector.xpath('/html/head/script[3]/text()').extract()[0]

        page_id = 0
        reg = 'CONFIG\\[\'page_id\'\\]=\\\'(.*?)\\\';';
        #print 'page_text: ' + page_text
        page_id_rg = re.compile(reg, re.IGNORECASE|re.DOTALL)
        m = page_id_rg.search(page_text)
        if m:
            print 'get page_id: ' + str(m.group(1))
            page_id = m.group(1)
        body = {
            'ajwvr' : '6',
            'domain':'100120',
            'feed_filter':'1',
            'pagebar':'1',
            'tab':'review',
            'current_page':'2',
            'pl_name':'Pl_Core_MixedFeed__57',
            'id':'100120181704',
            'script_uri':'/p/100120181704/review',
            'feed_type':'1',
            'page':'1',
            'pre_page':'1',
            'domain_op':'100120',
        }
        body['script_uri'] = '/p/' + str(page_id) + 'review'
        body['pagebar'] = 0
        body['page'] = page
        body['pre_page'] = page
        body['id'] = page_id
        body['current_page'] = (page-1) * 3 + 1
        first_pagebar_url = 'https://weibo.com/p/aj/v6/mblog/mbloglist?' + urlencode(body)
        #yield Request(url = first_pagebar_url, callback=self.public_comment_from_pagebar)
        body['pagebar'] = 1
        body['current_page'] += 1
        second_pagebar_url = 'https://weibo.com/p/aj/v6/mblog/mbloglist?' + urlencode(body)
        yield Request(url = second_pagebar_url, callback=self.public_comment_from_pagebar)

    def personal_comment_getlongtext(self, response):
        print '~~~~~~~~~~~~~~~~~~~~~personal_comment_getlongtext~~~~~~~~~~~~~~~~~~~~~~~~~'
        text = json.loads(response.text)['data']['html']
        tree = etree.HTML(text.decode('utf-8'))
        #print etree.tostring(tree)
        list_reg = '/html/*'
        lst = tree.xpath(list_reg)
        for x in lst:
            #print 'x.tag: ' + x.tag
            comment = ''.join(x.itertext())
            star = 0
            for y in x.getchildren():
                #print 'y.tag: ' + y.tag
                if y.tag == 'img':
                    #print y.get('title')
                    if y.get('title') == '[星星]':
                        star += 2
                    if y.get('title') == '[半星]':
                        star += 1
            star = star/2.0
            print 'long comment: ' + comment
            print 'star: ' + str(star)
            break


    def public_comment_from_pagebar(self, response):
        print '=====================public_comment_from__pagebar========================='
        text = json.loads(response.text)['data']
        #print 'pagebar: ' + text
        for x in self.get_star(text):
            yield x
        print '++++++++++++++++++++++end of get star++++++++++++++++++++++++++'
        yield self.get_next_page(text)


    def get_next_page(self, text):
        print '------------------------------get_next_page---------------------'
        url_ = self.get_next_page_url(text)
        #print 'get_next_page url: ' + url_
        if url_ == '':
            print 'not next page, skill now'
            return
        #print 'yiedl requeset get_next_page'
        return  Request(url=url_, callback=self.public_comment_review_page)

    def get_next_page_url(self, text):
        print 'get_next_page_url'
        tree = etree.HTML(text.decode('utf-8'))
        list_reg = '//*[@bpfilter="page"]'
        #print etree.tostring(tree)
        lst = tree.xpath(list_reg)
        if len(lst) == 0:
            print 'not next page can get'
        else:
            print lst[-1]
            url = lst[-1].get('href')
            #print 'get_next_page_url before split: ' + url
            url = url.split('review?')
            url_ = "https://weibo.com" + url[0] + '/review?' + url[1]
            print 'get_next_page_url: ' + url_
            return url_
        return ''

    def more_comment_from_root(self, response):
        print 'more_comment_from_root'
        tree = etree.HTML(response)
        list_reg = '//*[@class="WB_cardmore WB_cardmore_noborder S_txt1 clearfix"]'
        lst = tree.xpath(list_reg)
        if len(lst) != 0:
            lst = lst[0].get('href')
            print 'lst.get: ' + str(lst)
            return lst
        return ''

    def get_star(self, text):
        print "enter get_star"
        tree = etree.HTML(text.decode('utf-8'))
        #print etree.tostring(tree)
        list_reg = '//*[@class="WB_detail"]'
        lst = tree.xpath(list_reg)
        for x in lst:
            #print 'x.tag: ' + str(x.tag)
            for z in x.getchildren():
                #print 'z.tag: ' + str(z.tag)
                #print 'z.getclass: ' + z.get('class')
                if z.get('class') == 'WB_text W_f14':
                    ## need to just is there have more text message
                    comment = ''.join(z.itertext())
                    if '展开全文' in comment:
                        #Get a request to get long comment
                        print 'find 展开全文, yield a request for long comment'
                        for y in z.getchildren():
                            if y.get('class') == 'WB_text_opt':
                                action_data = y.get('action-data')
                                url_ = 'https://weibo.com/p/aj/mblog/getlongtext?ajwvr=6&' + action_data
                                print 'get long comment: ' + url_
                                yield Request(url = url_)
                                break
                        break
                    else:
                        print "z.text: " + comment
                        star = 0
                        for y in z.getchildren():
                            #print 'y.tag: ' + y.tag
                            if y.tag == 'img':
                                #print y.get('title')
                                if y.get('title') == '[星星]':
                                    star += 2
                                if y.get('title') == '[半星]':
                                    star += 1
                        star = star/2.0
                        print 'star: ' + str(star)
                    break
        #for x in lst:
        #    for y in  x.getchildren():
        #        if y.get('class') == 'WB_info':
        #            print y.getchildren()[0].get('nick-name')

    def get_small_comment(self, text):
        #find id from https://weibo.com/aj/v6/comment/small?ajwvr=6&act=list&mid=4055977453853446&uid=2501831957&isMain=true&dissDataFromFeed=%5Bobject%20Object%5D&ouid=2390209393&location=page_100120_home&filter_actionlog=1&_t=0&__rnd=1508642596984
        # and then jump to https://weibo.com/aj/v6/comment/big?ajwvr=6&id=4055977453853446&from=singleWeiBo
        # do this in function: get_url_from_small_comment_more
        #url = self.get_url_from_small_comment_more(text)
        #Request(url = url, callback=self.parse_detail)
        print 'get_small_comment'

        return

    def get_url_from_small_comment_more(self, text):
        return

    def main_comment_handle(self, response):
        #start process https://weibo.com/aj/v6/comment/big?ajwvr=6&id=4055977453853446&root_comment_max_id=160943824670004&root_comment_max_id_type=0&root_comment_ext_param=&page=2&filter=hot&sum_comment_number=765&filter_tips_before=0&from=singleWeiBo&__rnd=1508643907810
        # it sould be call 3 times for above url and then enter more link
        #more link:Request URL:https://weibo.com/aj/v6/comment/big?ajwvr=6&id=4055977453853446&root_comment_max_id=139778239997705&root_comment_max_id_type=0&root_comment_ext_param=&page=5&filter=hot&sum_comment_number=991&filter_tips_before=1&from=singleWeiBo&__rnd=1508644004054
        return


















        # yield  Request(url="http://movie.weibo.com/movie/web/category",callback=self.parse_information)

    # def parse_information(self, response):
    #     """ 抓取个人信息 """
    #     print "----parseinformation"
    #     informationItem = InformationItem()
    #     selector = Selector(response)
    #     ID = re.findall('(\d+)/info', response.url)[0]
    #     try:
    #         text1 = ";".join(selector.xpath('body/div[@class="c"]//text()').extract())  # 获取标签里的所有text()
    #         nickname = re.findall('昵称[：:]?(.*?);'.decode('utf8'), text1)
    #         gender = re.findall('性别[：:]?(.*?);'.decode('utf8'), text1)
    #         place = re.findall('地区[：:]?(.*?);'.decode('utf8'), text1)
    #         briefIntroduction = re.findall('简介[：:]?(.*?);'.decode('utf8'), text1)
    #         birthday = re.findall('生日[：:]?(.*?);'.decode('utf8'), text1)
    #         sexOrientation = re.findall('性取向[：:]?(.*?);'.decode('utf8'), text1)
    #         sentiment = re.findall('感情状况[：:]?(.*?);'.decode('utf8'), text1)
    #         vipLevel = re.findall('会员等级[：:]?(.*?);'.decode('utf8'), text1)
    #         authentication = re.findall('认证[：:]?(.*?);'.decode('utf8'), text1)
    #         url = re.findall('互联网[：:]?(.*?);'.decode('utf8'), text1)
    #
    #         informationItem["_id"] = ID
    #         if nickname and nickname[0]:
    #             informationItem["NickName"] = nickname[0].replace(u"\xa0", "")
    #         if gender and gender[0]:
    #             informationItem["Gender"] = gender[0].replace(u"\xa0", "")
    #         if place and place[0]:
    #             place = place[0].replace(u"\xa0", "").split(" ")
    #             informationItem["Province"] = place[0]
    #             if len(place) > 1:
    #                 informationItem["City"] = place[1]
    #         if briefIntroduction and briefIntroduction[0]:
    #             informationItem["BriefIntroduction"] = briefIntroduction[0].replace(u"\xa0", "")
    #         if birthday and birthday[0]:
    #             try:
    #                 birthday = datetime.datetime.strptime(birthday[0], "%Y-%m-%d")
    #                 informationItem["Birthday"] = birthday - datetime.timedelta(hours=8)
    #             except Exception:
    #                 informationItem['Birthday'] = birthday[0]   # 有可能是星座，而非时间
    #         if sexOrientation and sexOrientation[0]:
    #             if sexOrientation[0].replace(u"\xa0", "") == gender[0]:
    #                 informationItem["SexOrientation"] = "同性恋"
    #             else:
    #                 informationItem["SexOrientation"] = "异性恋"
    #         if sentiment and sentiment[0]:
    #             informationItem["Sentiment"] = sentiment[0].replace(u"\xa0", "")
    #         if vipLevel and vipLevel[0]:
    #             informationItem["VIPlevel"] = vipLevel[0].replace(u"\xa0", "")
    #         if authentication and authentication[0]:
    #             informationItem["Authentication"] = authentication[0].replace(u"\xa0", "")
    #         if url:
    #             informationItem["URL"] = url[0]
    #
    #         try:
    #             urlothers = "https://weibo.cn/attgroup/opening?uid=%s" % ID
    #             r = requests.get(urlothers, cookies=response.request.cookies, timeout=5)
    #             if r.status_code == 200:
    #                 selector = etree.HTML(r.content)
    #                 texts = ";".join(selector.xpath('//body//div[@class="tip2"]/a//text()'))
    #                 if texts:
    #                     num_tweets = re.findall('微博\[(\d+)\]'.decode('utf8'), texts)
    #                     num_follows = re.findall('关注\[(\d+)\]'.decode('utf8'), texts)
    #                     num_fans = re.findall('粉丝\[(\d+)\]'.decode('utf8'), texts)
    #                     if num_tweets:
    #                         informationItem["Num_Tweets"] = int(num_tweets[0])
    #                     if num_follows:
    #                         informationItem["Num_Follows"] = int(num_follows[0])
    #                     if num_fans:
    #                         informationItem["Num_Fans"] = int(num_fans[0])
    #         except Exception, e:
    #             pass
    #     except Exception, e:
    #         pass
    #     else:
    #         yield informationItem
    #     yield Request(url="https://weibo.cn/%s/profile?filter=1&page=1" % ID, callback=self.parse_tweets, dont_filter=True)
    #     yield Request(url="https://weibo.cn/%s/follow" % ID, callback=self.parse_relationship, dont_filter=True)
    #     yield Request(url="https://weibo.cn/%s/fans" % ID, callback=self.parse_relationship, dont_filter=True)
    def parse_information(self,response):
        print "parse_information"


    def parse_tweets(self, response):
        """ 抓取微博数据 """
        selector = Selector(response)
        ID = re.findall('(\d+)/profile', response.url)[0]
        divs = selector.xpath('body/div[@class="c" and @id]')
        for div in divs:
            try:
                tweetsItems = TweetsItem()
                id = div.xpath('@id').extract_first()  # 微博ID
                content = div.xpath('div/span[@class="ctt"]//text()').extract()  # 微博内容
                cooridinates = div.xpath('div/a/@href').extract()  # 定位坐标
                like = re.findall('赞\[(\d+)\]'.decode('utf8'), div.extract())  # 点赞数
                transfer = re.findall('转发\[(\d+)\]'.decode('utf8'), div.extract())  # 转载数
                comment = re.findall('评论\[(\d+)\]'.decode('utf8'), div.extract())  # 评论数
                others = div.xpath('div/span[@class="ct"]/text()').extract()  # 求时间和使用工具（手机或平台）

                tweetsItems["_id"] = ID + "-" + id
                tweetsItems["ID"] = ID
                if content:
                    tweetsItems["Content"] = " ".join(content).strip('[位置]'.decode('utf8'))  # 去掉最后的"[位置]"
                if cooridinates:
                    cooridinates = re.findall('center=([\d.,]+)', cooridinates[0])
                    if cooridinates:
                        tweetsItems["Co_oridinates"] = cooridinates[0]
                if like:
                    tweetsItems["Like"] = int(like[0])
                if transfer:
                    tweetsItems["Transfer"] = int(transfer[0])
                if comment:
                    tweetsItems["Comment"] = int(comment[0])
                if others:
                    others = others[0].split('来自'.decode('utf8'))
                    tweetsItems["PubTime"] = others[0].replace(u"\xa0", "")
                    if len(others) == 2:
                        tweetsItems["Tools"] = others[1].replace(u"\xa0", "")
                yield tweetsItems
            except Exception, e:
                pass

        url_next = selector.xpath('body/div[@class="pa" and @id="pagelist"]/form/div/a[text()="下页"]/@href'.decode('utf8')).extract()
        if url_next:
            yield Request(url=self.host + url_next[0], callback=self.parse_tweets, dont_filter=True)

    def parse_relationship(self, response):
        """ 打开url爬取里面的个人ID """
        selector = Selector(response)
        if "/follow" in response.url:
            ID = re.findall('(\d+)/follow', response.url)[0]
            flag = True
        else:
            ID = re.findall('(\d+)/fans', response.url)[0]
            flag = False
        urls = selector.xpath('//a[text()="关注他" or text()="关注她"]/@href'.decode('utf')).extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        for uid in uids:
            relationshipsItem = RelationshipsItem()
            relationshipsItem["Host1"] = ID if flag else uid
            relationshipsItem["Host2"] = uid if flag else ID
            yield relationshipsItem
            yield Request(url="https://weibo.cn/%s/info" % uid, callback=self.parse_information)

        next_url = selector.xpath('//a[text()="下页"]/@href'.decode('utf8')).extract()
        if next_url:
            yield Request(url=self.host + next_url[0], callback=self.parse_relationship, dont_filter=True)
