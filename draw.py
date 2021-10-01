import pathlib
import random
from io import BytesIO
from typing import Optional, Union

import httpx
from PIL import Image, ImageDraw

images_dir = pathlib.Path(__file__).absolute().parent / 'images'
images_count = len(list(images_dir.iterdir()))


def help_image() -> Image.Image:
    # 200x200

    cells = []
    cell = []
    for i in range(1, images_count + 1):
        if len(cell) < 4:
            cell.append(i)
        else:
            cells.append(cell)
            cell = []
    else:
        if cell:
            cells.append(cell)

    width = 4 * 200
    height = len(cells) * 200
    image = Image.new('RGBA', (width, height))
    for row, cell in enumerate(cells):
        for col, idx in enumerate(cell):
            img = Image.open(images_dir / f'{idx}.png')
            img = img.resize((200, 200))
            draw = ImageDraw.Draw(img)
            draw.text((88, 88), str(idx))
            image.paste(img, (col * 200, row * 200))

    return image


def combine(
    avatar_url: Union[str, int], image_idx: int = None
) -> Optional[Image.Image]:
    """
    :param avatar_url: 头像链接或QQ号
    :param image_idx: 模板序号，索引从1开始, 不合法数值都会使用随机替代
    """
    if isinstance(avatar_url, int):
        avatar_url = f'http://q1.qlogo.cn/g?b=qq&nk={avatar_url}&s=640'

    try:
        content = httpx.get(avatar_url, timeout=20).content
    except Exception as e:
        print(e)
        return

    avatar = Image.open(BytesIO(content))
    if avatar.mode != 'RGBA':
        avatar = avatar.convert('RGBA')

    if not (image_idx and 1 <= image_idx <= images_count):
        image_idx = random.randint(1, images_count)
    image = Image.open(images_dir / f'{image_idx}.png')

    # 确保头像图片为正方形
    if avatar.size[0] != avatar.size[1]:
        avatar = avatar.crop((0, 0, min(avatar.size), min(avatar.size)))
    # 确保头像和模板图片一样大, 只缩小不放大
    c = avatar.size[0] - image.size[0]
    if c > 0:
        avatar = avatar.resize(image.size)
    elif c < 0:
        image = image.resize(avatar.size)
    # 合并
    avatar.paste(image, (0, 0), image)
    return avatar


if __name__ == "__main__":
    help_image().save('test.png')
