"""头像生成
发送 头像生成帮助 获取帮助
发送 头像生成+{模板序号}+{一张图片}, 如果不指定模板序号，则随机选择。如果不没有图片，则使用发送人当前头像
"""
from io import BytesIO
import time

from botoy import GroupMsg, S
from botoy import decorators as deco
from botoy.parser import group as gp

from .draw import combine, help_image


@deco.ignore_botself
@deco.in_content('头像生成')
def receive_group_msg(ctx: GroupMsg):
    img = None

    if ctx.Content == '头像生成帮助':
        img = help_image()
    else:
        content = ctx.Content
        pic = gp.pic(ctx)
        if pic:
            content = pic.Content
            avatar_url = pic.GroupPic[0].Url
        else:
            avatar_url = ctx.FromUserId

        try:
            image_idx = int(content[4:])
        except Exception:
            image_idx = None

        times = 5  # 因为会莫名其妙出现 mask transparency 相关的错误
        while times > 0:
            times -= 1
            try:
                img = combine(avatar_url, image_idx)
                break
            except Exception:
                time.sleep(3)

    if img:
        with BytesIO() as buf:
            img.save(buf, 'png')
            S.image(buf)
    else:
        S.text('处理失败')
