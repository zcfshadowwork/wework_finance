# -*- coding:utf-8 -*-


# media file format
FILE_TYPE_MAP = {'voice': '.amr',
                 'emotion1': '.png',
                'emotion2': '.gif',
                 'image': '.jpg',
                 'video': '.mp4'}

# all message type
MSG_TYPE_MAP = {'text': '文本',
                'image': '图片',
                'voice': '语音',
                'video': '视频',
                'emotion': '表情',
                'file': '文件',
                'disagree': '不同意会话聊天内容',
                'agree': '同意会话聊天内容',
                'card': '名片',
                'location': '位置',
                'link': '链接',
                'weapp': '小程序消息',
                'chatrecord': '会话记录消息',
                'collect': '填表消息',
                'redpacket': '红包消息',
                'meeting': '会议邀请消息',
                'docmsg': '在线文档消息',
                'markdown': 'MarkDown格式消息',
                'news': '图文消息',
                'calendar': '日程消息',
                'mixed': '混合消息',
                'meeting_voice_call': '会议内容',
                'voip_doc_share': '会议共享文档',
                'external_redpacket': '互通红包消息',
                'sphfeed': '视频号消息',
                }

CORP_ID = "企业微信id"

CHAT_SECRET = "企业微信secret"

PRI_KEY = "企业微信private_key"