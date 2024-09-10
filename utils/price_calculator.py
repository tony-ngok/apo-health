from em_tasks.utils.exchange_rate import ExchangeRate

class PriceCalculator():
  def __init__(self, price_rules=None, target_currency='USD', min_profit_amount=10, default_qty=50):
    self.rules = {
      'roi': 0.75,
      'ad_cost': 3,
      'transfer_cost': 0,
      'tax_rate': 0.09
    }

    if price_rules:
      self.rules.update(price_rules)

    self.min_profit_amount = min_profit_amount
    self.default_qty = default_qty
    self.target_currency = target_currency
    self.exchange_rate = ExchangeRate.get_exchange_rate('USD', target_currency)

  def calc_offer(self, src_offer):
    if isinstance(src_offer, bool) and not src_offer:
      offer = False
    elif src_offer is None or src_offer.get('price', 0) == 0:
      offer = {'price': 0, 'quantity': 0}
    else:
      src_currency = src_offer.get('currency', 'USD')
      src_price_in_usd = src_offer['price']
      if src_currency != 'USD':
        exchange_rate = ExchangeRate.get_exchange_rate('USD', src_currency)
        src_price_in_usd = src_offer['price'] / exchange_rate
      price_in_usd = (self.rules['ad_cost'] + self.rules['transfer_cost'] + src_price_in_usd * (1 + self.rules['tax_rate'])) * (1 + self.rules['roi']) / 0.97
      price_in_usd = max(src_price_in_usd + self.rules['transfer_cost'] + self.min_profit_amount, price_in_usd)
      price = price_in_usd * self.exchange_rate
      cost = self.calc_cost(src_offer)
      if (cost / price) > 0.5:
        price += 5

      offer = {'price': round(price, 2), 'quantity': self.default_qty}

    return offer

  def calc_cost(self, src_offer):
    if not src_offer or not src_offer.get('price', 0):
      return 0

    src_currency = src_offer.get('currency', 'USD')
    src_price_in_usd = src_offer['price']
    if src_currency != 'USD':
      exchange_rate = ExchangeRate.get_exchange_rate('USD', src_currency)
      src_price_in_usd = src_offer['price'] / exchange_rate

    return round(src_price_in_usd * self.exchange_rate, 2)

  def calc_profit(self, src_offer):
    if not src_offer or not src_offer['price']:
      return

    offer = self.calc_offer(src_offer)
    if not offer or not offer['price']:
      return

    cost = self.calc_cost(src_offer)
    profit = offer['price'] - cost - offer['price'] * 0.0875

    return round(profit, 2)

  def calc_profit_rate(self, src_offer):
    if not src_offer or not src_offer['price']:
      return

    offer = self.calc_offer(src_offer)
    if not offer or not offer['price']:
      return

    cost = self.calc_cost(src_offer)
    profit = offer['price'] - cost - offer['price'] * 0.0875

    return round(profit / offer['price'] * 100, 2)
