"""
卡牌文件模板

将此文件复制到某个 mod 的 code/cards/ 目录并重命名, 即为一张新卡牌
文件名即卡牌 name, card_id 自动生成为 "{modid}:{文件名}"

mod 目录结构:
    <modid>/          目录名即 modid, 内部为 Python 包
        __init__.py   包声明
        info.json     可选, 存放 name/version/dependencies 等元信息
        code/
            __init__.py
            cards/    卡牌文件, 每个 py 一张卡, 文件名 card_<id>.py
            keywords/ 关键词, 每个 py 一个, 导出 KEYWORD
                      KeywordData 可以带 procedures(规则效果)
                      也可以用 trigger 声明触发型关键词(如部署/亡计)
        data/zh.json  可选, 官方中文名称与描述, 按卡牌 id 匹配
        assets/
            cards/    卡图, 英文 id 命名, 按国家分目录
            keyword/  关键词图标

info.json 中可以声明依赖, 加载时会先加载依赖的 mod:
    {"name": "My Mod", "dependencies": ["kards"]}

运行期可以用 cards.get("kards:card_102_grenadier") 引用其他 mod 的卡牌,
用 cards.asset("kards", "cards/card_face.png") 取其他 mod 的资源路径

约定:
    1. 卡牌文件导出名为 CARD_DATA 的 CardData 实例
    2. name 取文件名(card_<id>), card_id 为 "{modid}:{name}"
    3. display_name 为游戏内显示的中文名
    4. keywords 为字符串列表, 引用 keywords/ 下定义的关键词 id
    5. 跨 mod 引用一律使用 card_id 字符串, 不要在导入阶段读取其他 mod 的注册表
"""
from main import CardData, CardType, Country

# 文件名使用英文标识符, 例如 my_card.py 对应 name "my_card", card_id "{modid}:my_card"
# display_name 为游戏内显示的中文名
CARD_DATA = CardData(
    type=CardType.INFANTRY,   # 单位类型: INFANTRY/TANK/FIGHTER/BOMBER/ARTILLERY, 指令为 ORDER
    country=Country.NEUTRAL,
    cost=0,
    display_name="卡牌中文名",
    heal_self=False,      # 指令是否改为治疗己方总部(默认伤害敌方总部)
    text="卡牌中文描述",
    rare="standard",
    keywords=[],          # 引用 keywords/ 下的关键词 id, 如 ["blitz"]
    at=0,
    df=0,
    operation_cost=0,
)
