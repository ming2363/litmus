# 修复下单失败后库存仍被占住

网店结算会先按订单行预占库存，收费成功后再把这些预占转成已售。赠品也要占一件，并和商品走同一次提交或释放。现在失败的订单会留下一部分预占，后面的订单还能在同一份库存上继续成交。请让成功和失败两条路径的库存都符合下面的规则。

## 库存账本 `warehouse.stock.StockBook`

每个 SKU 有三份数量：可售 `available`、预占 `held`、已售 `sold`。

- `add_sku(sku, available)`：`sku` 必须是非空 `str`，`available` 必须是大于等于 0 的 `int`，且不能是 `bool`。否则抛出 `ValueError`。同一个 `sku` 不能加入两次，再次加入也抛出 `ValueError`。
- `snapshot(sku)`：返回 `(available, held, sold)`。未知 SKU 抛出 `warehouse.errors.UnknownSku`，属性 `sku` 是这个编号。
- `reserve(sku, qty)`：`qty` 必须是大于 0 的 `int`，且不能是 `bool`，否则 `ValueError`。未知 SKU 抛出 `UnknownSku`。可售不足时抛出 `warehouse.errors.InsufficientStock`，属性 `sku` 是这个编号，并且这一次调用不改变该 SKU。成功时 `available` 减少 `qty`，`held` 增加 `qty`。
- `release(sku, qty)`：预占不足时抛出 `ValueError`，并且不改变该 SKU。成功时 `held` 减少 `qty`，`available` 增加 `qty`。
- `commit(sku, qty)`：预占不足时抛出 `ValueError`，并且不改变该 SKU。成功时 `held` 减少 `qty`，`sold` 增加 `qty`。

## 预占会话 `warehouse.holds.HoldSession`

`HoldSession(book)` 记住这一单里通过它预占的每一笔。

- `reserve(sku, qty)`：调用账本的 `reserve`。只有账本预占成功后，才把 `(sku, qty)` 记入本会话。
- `rollback()`：把本会话已经记下的每一笔都 `release` 掉，然后清空会话。没有任何记录时什么都不做。连续调用两次，第二次仍然什么都不做。
- `commit()`：把本会话已经记下的每一笔都 `commit` 掉，然后清空会话。没有任何记录时什么都不做。

## 赠品 `warehouse.promotions.attach_gift(book, session, gift_sku)`

`gift_sku` 是 `None` 或 `""` 时不做任何事。否则必须通过 `session.reserve(gift_sku, 1)` 预占一件。赠品因此会被同一次 `rollback` 释放，也会被同一次 `commit` 转成已售。不要绕过会话直接改账本。

## 订单和回执

```text
OrderLine(sku, qty)
Order(order_id, user_id, lines, gift_sku, coupon, amount_cents)
Receipt(order_id, user_id, pay_id, lines, gift_sku, amount_cents)
```

三者都在 `warehouse.models` 里，是冻结的数据类。`lines` 是 `OrderLine` 的序列。

## `warehouse.checkout.checkout(book, gateway, order)`

按下面的顺序执行，前面一步失败就不要做后面的步骤：

1. 检查每一行。`sku` 必须是非空 `str`，`qty` 必须是大于 0 的 `int` 且不能是 `bool`。任一行使 `ValueError`。此时还没有预占，也还没有调用 `gateway.charge`。
2. 按 `lines` 的顺序，用同一个 `HoldSession` 预占每一行的 `qty`。
3. `gift_sku` 不是 `None` 也不是 `""` 时，调用 `attach_gift` 再预占一件。赠品可以和某一行是同一个 SKU，这时要在商品数量之外再占一件。
4. 检查优惠券。`None`、`""` 和 `"SAVE10"` 可以通过。其他值抛出 `warehouse.errors.CouponError`，属性 `code` 是原来的券码。这一步失败时不要调用 `gateway.charge`。
5. 调用 `gateway.charge(user_id, amount_cents)`，它返回支付单号字符串。`warehouse.errors.PaymentDeclined` 要原样继续抛出，不要包装成别的异常。
6. 只有收费成功，才把本会话里的全部预占（含赠品）转成已售，并返回 `Receipt`。`pay_id` 是 `charge` 的返回值。`order_id`、`user_id`、`gift_sku`、`amount_cents` 与订单相同，不重新计算金额。`lines` 与订单逐项的 `sku`、`qty` 相同。不要修改订单对象。

第 2 步到第 5 步抛出的 `InsufficientStock`、`UnknownSku`、`CouponError`、`PaymentDeclined`，都必须在离开 `checkout` 之前把本单已经预占的商品和赠品全部释放。失败之后，每个 SKU 的 `snapshot` 与调用 `checkout` 之前相同。支付被拒时 `charge` 恰好被调用一次。库存不足、未知 SKU 或优惠券无效时，`charge` 一次都不要调用。

`gateway` 只需要提供 `charge(user_id, amount_cents)`。

只修改 `warehouse/` 下的 Python 文件，不要改测试。

## 如何自测

`python3 litmus.py check`
