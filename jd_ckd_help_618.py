'''
new Env('全民拆快递-助力');
export RabbitToken="token值"

变量:
RabbitToken： 机器人给你发的token

log剩余次数大于5000方可使用
'''
import asyncio
import json

from utils.common import UserClass, printf, print_api_error, print_trace, TaskClass


class CKDHelpUserClass(UserClass):
    def __init__(self, cookie):
        super(CKDHelpUserClass, self).__init__(cookie)
        self.inviteCode = ""
        self.appname = "50180"
        self._help_num = None
        self._error = 0
        self.Origin = "https://wbbny.m.jd.com"
        self.referer = "https://wbbny.m.jd.com/"

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, value):
        self._error = value
        if self._error >= 3:
            self.black = True
            self.need_help = False
            self.can_help = False

    async def opt(self, opt):
        await self.set_joyytoken()
        # self.set_shshshfpb()
        _opt = {
            "method": "post",
            "log": True,
            "api": "client.action",
            "body_param": {
                "appid": "signed_wh5",
                "client": "wh5",
                "clientVersion": "1.0.0",
                "functionId": opt['functionId']
            }
        }
        _opt.update(opt)
        return _opt

    def log_format(self, body, log_data):
        body.update({"log": log_data["log"]})
        body.update({"random": log_data["random"]})
        # body = f"body={json.dumps(body, separators=(',', ':'))}"
        body = {
            "body": json.dumps(body, separators=(',', ':'))
        }
        return body

    @property
    def help_num(self):
        if self._help_num == None:
            self._help_num = 0
        return self._help_num

    @help_num.setter
    def help_num(self, value):
        self._help_num = value

    async def get_invite_code(self):
        try:
            body = {}
            opt = {
                "functionId": "promote_getTaskDetail",
                "body": body,
                "need_log": False
            }
            status, result = await self.jd_api(await self.opt(opt))
            self.need_help = False
            if result and result.get("code") == 0:
                if result.get("data") and result['data'].get('bizCode') == 0 and result['data']["result"].get('inviteId'):
                    self.help_num = result['data']['result']['taskVos'][0]['times']
                    self.inviteCode = result['data']['result']['inviteId']
                    self.printf(f"【助力码】: \t{self.inviteCode}")
                    self.need_help = True
                else:
                    msg = result['data'].get("bizMsg", "")
                    if '未登录' in msg:
                        self.valid = False
                        self.can_help = False
                    elif '助力次数用完啦' in msg:
                        self.can_help = False
                    elif '火爆' in msg:
                        self.need_help = False
                        self.can_help = False
                    elif '邀请过' in msg:
                        pass
                    elif '好友人气爆棚了' in msg:
                        self.can_help = False
                    elif msg == "success":
                        self.need_help = False
                        self.printf("助力已满")
                        return
                    print_api_error(opt, status)
                    print(result)
            else:
                msg = result['msg']
                if '登陆失败' in msg:
                    self.valid = False
                    self.can_help = False
                self.printf(f"{msg}")
        except:
            print_trace()

    async def help(self, inviter):
        try:
            if not inviter.need_help:
                return
            if inviter.help_num >= inviter.MAX_HELP_NUM:
                inviter.need_help = False
                printf(f"车头[{inviter.Name}]\t 助力已满({inviter.help_num}/{inviter.MAX_HELP_NUM})")
                return
            body = {
                "actionType": 0,
                "inviteId": inviter.inviteCode,
            }
            opt = {
                "functionId": "promote_collectScore",
                "body": body,
            }
            status, res_data = await self.jd_api(await self.opt(opt))
            code = res_data['code']
            if code == 0:
                if res_data['data'].get("bizCode") == 0:
                    inviter.help_num += 1
                    self.printf(f"助力[{inviter.Name}]成功({inviter.help_num}/{inviter.MAX_HELP_NUM})")
                else:
                    msg = res_data['data'].get("bizMsg", "")
                    if '未登录' in msg:
                        self.valid = False
                        self.can_help = False
                    elif '次数用完啦' in msg:
                        self.can_help = False
                    elif '火爆' in msg:
                        # inviter.error += 1
                        self.error += 1
                    elif '邀请过' in msg:
                        pass
                    elif '好友人气爆棚了' in msg:
                        inviter.need_help = False
                    self.printf(f"助力失败[{code}]: {msg}")
            else:
                msg = res_data['msg']
                if '登陆失败' in msg:
                    self.valid = False
                    self.can_help = False
                self.printf(f"{msg}")
        except:
            print_trace()


if __name__ == '__main__':
    task = TaskClass("invite")
    task.MAX_HELP_NUM = 8
    task.name = 'ZNS_HELP'
    task.need_appck = True
    task.init_config(CKDHelpUserClass)
    asyncio.run(task.main("全民拆快递-助力"))
