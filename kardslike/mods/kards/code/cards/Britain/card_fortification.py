"""防御工事"""
from main import BattleGround, Card, CardData, CardType, Country, Event, EventType, Procedure


def action(card: Card, event: Event, ground: BattleGround) -> None:
    """
    使友方总部获得 +7 防御力

    Args:
        card: 效果所属卡牌
        event: 事件
        ground: 战斗全局参数
    """
    ground.buff(ground.hqs[event.player], df=7)


from main import Rarity

CARD_DATA = CardData(
    type=CardType.ORDER,
    country=Country.BRITAIN,
    cost=3,
    display_name="防御工事",
    text="使友方总部获得 +7 防御力。",
    rare=Rarity.STANDARD,
    procedures=[Procedure(EventType.USE, lambda card, event, ground: event.dict.get("source") is card, action)],
)
