from scrapy.utils.reqser import request_to_dict, request_from_dict
from scrapy.http import Request
from scrapy.http import Response
from urllib import urlencode
import functools
import re

try:
    import cPickle as pickle
except ImportError:
    import pickle


class Base(object):
    """Per-spider queue/stack base class"""

    def __init__(self, server, spider, key, queue_name):
        """Initialize per-spider redis queue.

        Parameters:
            server -- redis connection
            spider -- spider instance
            key -- key for this queue (e.g. "%(spider)s:queue")
        """
        self.server = server
        self.spider = spider
        self.key = key % {'spider': queue_name}

    def _encode_request(self, request):
        """Encode a request object"""
        return pickle.dumps(request_to_dict(request, self.spider), protocol=-1)

    def _decode_request(self, encoded_request):
        """Decode an request previously encoded"""
        return request_from_dict(pickle.loads(encoded_request), self.spider)

    def __len__(self):
        """Return the length of the queue"""
        raise NotImplementedError

    def push(self, request):
        """Push a request"""
        raise NotImplementedError

    def pop(self, timeout=0):
        """Pop a request"""
        raise NotImplementedError

    def clear(self):
        """Clear queue/stack"""
        self.server.delete(self.key)


class SpiderQueue(Base):
    """Per-spider FIFO queue"""

    def __len__(self):
        """Return the length of the queue"""
        return self.server.llen(self.key)

    def push(self, request):
        """Push a request"""
        self.server.lpush(self.key, self._encode_request(request))

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.brpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.rpop(self.key)
        if data:
            return self._decode_request(data)


class SpiderPriorityQueue(Base):
    """Per-spider priority queue abstraction using redis' sorted set"""

    def __len__(self):
        """Return the length of the queue"""
        return self.server.zcard(self.key)

    def push(self, request):
        """Push a request"""
        data = self._encode_request(request)
        pairs = {data: -request.priority}
        self.server.zadd(self.key, **pairs)

    def pop(self, timeout=0):
        """
        Pop a request
        timeout not support in this queue class
        """
        # use atomic range/remove using multi/exec
        pipe = self.server.pipeline()
        pipe.multi()
        pipe.zrange(self.key, 0, 0).zremrangebyrank(self.key, 0, 0)
        results, count = pipe.execute()
        if results:
            return self._decode_request(results[0])


class SpiderSimpleQueue(Base):
    """ url + callback """

    def __len__(self):
        """Return the length of the queue"""
        return self.server.llen(self.key)

    def push(self, request):
        """Push a request"""
        print 'push url: ' + request.url
        self.server.lpush(self.key, request.url.split('.com')[1])

    # def pop(self, timeout=0):
    #     """Pop a request"""
    #     if timeout > 0:
    #         url = self.server.brpop(self.key, timeout=timeout)
    #         if isinstance(url, tuple):
    #             url = url[1]
    #     else:
    #         url = self.server.rpop(self.key)
    #     if url:
    #         try:
    #             if "/follow" in url or "/fans" in url:
    #                 cb = getattr(self.spider, "parse_relationship")
    #             elif "/profile" in url:
    #                 cb = getattr(self.spider, "parse_tweets")
    #             elif "/info" in url:
    #                 cb = getattr(self.spider, "parse_information")
    #             else:
    #                 raise ValueError("Method not found in: %s( URL:%s )" % (self.spider, url))
    #             return Request(url="https://weibo.cn%s" % url, callback=cb)
    #         except AttributeError:
    #             raise ValueError("Method not found in: %s( URL:%s )" % (self.spider, url))
    def pop(self, timeout=0):
        """Pop a request"""
        #print "popup a number"
        if timeout > 0:
            url = self.server.brpop(self.key, timeout=timeout)

            if isinstance(url, tuple):
                url = url[1]

        else:
            print self.key
            url = self.server.rpop(self.key)
        if url:
            #print ('getlongtext' in url)
            try:
                if "web/category" in url:
                    url = url.split('.')[1]
                    cb = getattr(self.spider, "parse_information")
                    print "web/category: https://weibo.cn%s" % url
                    return Request(url="http://movie.weibo." + url, callback=cb)
                elif "review?pids=Pl_Core_MixedFeed__57" in url:
                    #print 'review after first page: ' + url
                    cb = getattr(self.spider, "public_comment_review_page")
                    my_re = '&page=(\\d+)'
                    rg = re.compile(my_re, re.IGNORECASE|re.DOTALL)
                    my_page = rg.search(url)
                    my_page = my_page.group(1)
                    url_ = "https://weibo.com" + url
                    func = functools.partial(cb, page=int(my_page))
                    #print "after first page review url: " + url_
                    return Request(url=url_, callback=func, method='GET')
                elif "review?feed_filter=1" in url:
                    print 'review: ' + url
                    cb = getattr(self.spider, "public_comment_review_page")
                    func = functools.partial(cb, page=1)
                    url_ = "https://weibo.com" + url
                    print "review url: " + url_
                    return Request(url=url_, callback=func, method = 'GET')
                    #return Request(url=url_, callback=cb, method='GET')
                elif "p/aj/v6/mblog/mbloglist" in url:
                    cb = getattr(self.spider, "public_comment_from_pagebar")
                    url_ = 'https://weibo.com' + url
                    print 'mbloglist: ' + url_
                    return Request(url = url_, callback=cb, method='GET')
                elif "100120" in url:
                    cb = getattr(self.spider, "public_comment_from_root")
                    url_ = "https://weibo.com" + url
                    print 'before url: ' + url
                    print 'Good job:' + url_
                    return Request(url=url_, callback=cb, method = 'GET')
                elif "/comment/big" in url:
                    cb = getattr(self.spider, "main_comment_handle")
                    return Request(url=url, callback=cb, method = 'GET')
                elif "getlongtext" in url:
                    cb = getattr(self.spider, "personal_comment_getlongtext")
                    url_ = 'https://weibo.com' + url
                    return Request(url=url_, callback=cb, method = 'GET')
                #elif "100120" in url:
                #    url_ =url.split("/p")
                #    url_= "/p"+url_[1]
                #    cb = getattr(self.spider, "parse_detail")
                #    return Request(url="https://weibo.com"+url_, callback=cb, meta={
                #        'dont_redirect': True,
                #        'handle_httpstatus_list': [200, 302]
                #    }  )

            except AttributeError:
                raise ValueError("Method not found in: %s( URL:%s )" % (self.spider, url))


class SpiderStack(Base):
    """Per-spider stack"""
    def __len__(self):
        """Return the length of the stack"""
        return self.server.llen(self.key)

    def push(self, request):
        """Push a request"""
        self.server.lpush(self.key, self._encode_request(request))

    def pop(self, timeout=0):
        """Pop a request"""
        if timeout > 0:
            data = self.server.blpop(self.key, timeout)
            if isinstance(data, tuple):
                data = data[1]
        else:
            data = self.server.lpop(self.key)

        if data:
            return self._decode_request(data)


__all__ = ['SpiderQueue', 'SpiderPriorityQueue', 'SpiderSimpleQueue', 'SpiderStack']
