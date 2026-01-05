from .models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

def create_notification(user, title, message, notif_type='system'):
    """
    创建一条通知消息
    
    Args:
        user: 用户对象或用户ID
        title: 通知标题
        message: 通知内容
        notif_type: 通知类型，可选值：system, order, flight, payment, refund, info, warning, alert
        
    Returns:
        Notification: 创建的通知对象
    """
    # 如果传入的是用户ID，获取用户对象
    if isinstance(user, int):
        try:
            user = User.objects.get(id=user)
        except User.DoesNotExist:
            return None
    
    # 创建并保存通知
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notif_type=notif_type,
        is_read=False
    )
    
    return notification

def create_order_notification(user, order, status, additional_info=None):
    """
    创建订单状态变更的通知
    
    Args:
        user: 用户对象或用户ID
        order: 订单对象
        status: 订单新状态
        additional_info: 附加信息
    """
    # 状态到标题和消息的映射
    status_messages = {
        'paid': {
            'title': '订单支付成功',
            'message': f'您的订单 {order.order_number} 已支付成功，我们将尽快为您出票。'
        },
        'ticketed': {
            'title': '订单已出票',
            'message': f'您的订单 {order.order_number} 已出票，请查看订单详情获取机票信息。'
        },
        'refunded': {
            'title': '订单已退款',
            'message': f'您的订单 {order.order_number} 已退款，退款金额将在1-7个工作日内返回您的支付账户。'
        },
        'canceled': {
            'title': '订单已取消',
            'message': f'您的订单 {order.order_number} 已取消。'
        }
    }
    
    # 获取对应状态的消息
    message_data = status_messages.get(status)
    if not message_data:
        return None
    
    title = message_data['title']
    message = message_data['message']
    
    # 添加附加信息
    if additional_info:
        message += f" {additional_info}"
    
    return create_notification(user, title, message, 'order')

def create_payment_notification(user, order, payment_status):
    """
    创建支付相关的通知
    """
    if payment_status == 'success':
        title = '支付成功通知'
        message = f'您的订单 {order.order_number} 支付成功，金额: ¥{order.total_price}。'
        return create_notification(user, title, message, 'payment')
    
    return None

def create_refund_notification(user, order, refund_status, refund_amount=None):
    """
    创建退款相关的通知
    """
    if refund_status == 'processing':
        title = '退款申请已受理'
        message = f'您的订单 {order.order_number} 退款申请已受理，我们将尽快处理。'
        return create_notification(user, title, message, 'refund')
    
    elif refund_status == 'completed':
        title = '退款完成通知'
        amount_text = f'¥{refund_amount}' if refund_amount else ''
        message = f'您的订单 {order.order_number} 退款{amount_text}已完成，将在1-7个工作日内返回原支付账户。'
        return create_notification(user, title, message, 'refund')
    
    return None

def create_flight_notification(user, flight, status_change, additional_info=None):
    """
    创建航班状态变更的通知
    """
    title = '航班状态更新'
    message = f'您的航班 {flight.flight_number} ({flight.departure_city}-{flight.arrival_city}) 状态已更新为: {status_change}。'
    
    if additional_info:
        message += f" {additional_info}"
    
    return create_notification(user, title, message, 'flight')


def create_reschedule_notification(user, original_ticket, new_ticket, reschedule_log):
    """
    创建改签成功的通知
    
    Args:
        user: 用户对象或用户ID
        original_ticket: 原机票对象
        new_ticket: 新机票对象
        reschedule_log: 改签记录对象
        
    Returns:
        Notification: 创建的通知对象
    """
    original_flight = reschedule_log.original_flight
    new_flight = reschedule_log.new_flight
    
    title = '机票改签成功'
    message = (
        f'您的机票已成功改签。'
        f'原航班: {original_flight.flight_number} ({original_flight.departure_city}-{original_flight.arrival_city})，'
        f'新航班: {new_flight.flight_number} ({new_flight.departure_city}-{new_flight.arrival_city})，'
        f'新座位: {new_ticket.seat_number}。'
    )
    
    # 添加差价信息
    price_diff = reschedule_log.price_difference
    if price_diff > 0:
        message += f' 已补差价: ¥{price_diff}。'
    elif price_diff < 0:
        message += f' 退还差价: ¥{abs(price_diff)}。'
    
    # 添加手续费信息
    if reschedule_log.reschedule_fee > 0:
        message += f' 改签手续费: ¥{reschedule_log.reschedule_fee}。'
    
    return create_notification(user, title, message, 'order')


def create_timeout_notification(user, order):
    """
    创建订单超时取消的通知
    
    Args:
        user: 用户对象或用户ID
        order: 被取消的订单对象
        
    Returns:
        Notification: 创建的通知对象
    """
    title = '订单已超时取消'
    message = (
        f'您的订单 {order.order_number} 因超时未支付已自动取消，'
        f'订单金额: ¥{order.total_price}。'
        f'如需继续购票，请重新预订。'
    )
    
    return create_notification(user, title, message, 'order')