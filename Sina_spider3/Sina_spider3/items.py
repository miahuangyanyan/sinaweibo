# encoding=utf-8
# ------------------------------------------
#   版本：3.0
#   日期：2016-12-01
#   作者：九茶<http://blog.csdn.net/bone_ace>
# ------------------------------------------

from scrapy import Item, Field


class InformationItem(Item):

    Film_id = Field()
    Film_nmae = Field()
    User_id = Field()
    Review = Field()
    Date = Field()
    Append_review  =Field()  #楼中楼的评论
    Score = Field() # 星星的等级





class TweetsItem(Item):
    """ 微博信息 """
    _id = Field()  # 用户ID-微博ID
    ID = Field()  # 用户ID
    Content = Field()  # 微博内容
    PubTime = Field()  # 发表时间
    Co_oridinates = Field()  # 定位坐标
    Tools = Field()  # 发表工具/平台
    Like = Field()  # 点赞数
    Comment = Field()  # 评论数
    Transfer = Field()  # 转载数


class RelationshipsItem(Item):
    """ 用户关系，只保留与关注的关系 """
    Host1 = Field()
    Host2 = Field()  # 被关注者的ID
