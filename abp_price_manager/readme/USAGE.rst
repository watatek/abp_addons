Recording a cost
~~~~~~~~~~~~~~~~

#. Go to *Price Manager > Cost Management* and create a record.
#. Fill in the cost name, the item, the supplier and the currency.
#. Enter the EXW, processing and freight costs. The landed cost is computed
   as ``EXW + Processing + Freight`` and cannot be edited. It is displayed in
   the record currency, followed by ``= <amount>`` in the company currency
   when the two differ.
#. Click **Submit**. The record moves from *Draft* to *Submitted* and the
   input fields become read-only.
#. An approver clicks **Approve** (from the form, or directly from the list
   view button). The record becomes *Active*, the approver and the approval
   date are stamped, any other *Active* cost for the same item **and the same
   supplier** is set to *Inactive*, and the landed cost is written to the
   product cost. Costs of other suppliers for the item stay active.
#. **Decline** sends a submitted record to *Inactive*; **Deactivate** does the
   same for an already active one.

Recording a selling price
~~~~~~~~~~~~~~~~~~~~~~~~~

#. Go to *Price Manager > Price Management* and create a record.
#. Pick the item first: the *Cost Name* field only proposes cost records
   belonging to that item, and changing the item clears the selected cost.
#. The landed cost is copied from the selected cost record and is read-only.
   It is shown in the cost currency, followed by ``= <amount>`` in the price
   currency when the two differ.
#. Choose the price currency. The gross margin always compares like with
   like: the landed cost is converted into the price currency first.
#. Enter the EXW, processing and freight prices. The selling price is their
   sum — shown the same way, with its company-currency equivalent — and the
   gross margin is
   ``(Selling Price - converted Landed Cost) / converted Landed Cost``,
   displayed as a percentage.
#. The Submit / Approve / Decline / Deactivate flow is identical to the cost
   one. Approving writes the selling price to the product sales price and
   deactivates the previous active price of that item.

Buying an item
~~~~~~~~~~~~~~

#. Create a purchase order. If the vendor is already set, adding a line for an
   item fills the unit price from the active cost of *that* vendor.
#. If the vendor is still empty, pick the item first: the line is priced from
   the cheapest active cost across vendors and the order takes that supplier.
#. Amounts are converted into the order currency at the order date.
#. Typing a price by hand disables the automation for that line — the approved
   cost no longer overwrites it.

Notes
~~~~~

* Deactivating or declining a record does **not** reset the value already
  written on the product; the product keeps the last approved figure until a
  new record is approved.
* Editing a cost or price component on a record that is already *Active*
  pushes the new value to the product immediately.
