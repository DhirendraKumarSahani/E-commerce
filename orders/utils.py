from .models import ShippingRule

def calculate_shipping(cart_items, state, shipping_type='STANDARD'):

    items_total = sum(
        float(item['price']) * int(item['quantity'])
        for item in cart_items
    )

    # 1️⃣ Product level free shipping check
    all_free = all(item.get('free_shipping', False) for item in cart_items)
    if all_free:
        return 0

    # 2️⃣ Fetch rule (state + type)
    rule = ShippingRule.objects.filter(
        is_active=True,
        shipping_type=shipping_type,
        state=state
    ).first()

    if not rule:
        rule = ShippingRule.objects.filter(
            is_active=True,
            shipping_type=shipping_type,
            state__isnull=True
        ).first()

    if not rule:
        return 0

    # 3️⃣ Min order free shipping
    if rule.min_order_free_shipping and items_total >= float(rule.min_order_free_shipping):
        return 0

    return float(rule.base_cost)
