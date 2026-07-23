This module adds a **Price Manager** application that keeps the purchase cost
and the selling price of an item under an explicit approval flow, instead of
letting users type them directly on the product form.

It introduces two models:

* ``sales.cost`` (*Cost Management*) — EXW cost, processing cost and freight
  cost for a given item and supplier. The **landed cost** is the sum of the
  three. The record also carries a currency and the matching
  ``res.currency`` rate.
* ``sales.price`` (*Price Management*) — EXW price, processing price and
  freight price for a given item. The **selling price** is the sum of the
  three, the landed cost is inherited from the linked cost record, and the
  **gross margin** is derived from both.

Both models share the same status flow — *Draft*, *Submitted*, *Active*,
*Inactive* — and record who approved the line and when.

Only one cost and one price may be *Active* for a given item at a time.
Approving a new one automatically deactivates the previous one, and the
approved values are written to the product:

* landed cost → ``product.template.standard_price``
* selling price → ``product.template.list_price``

Because those two product fields are now driven by this module, they are made
read-only on the product form.
