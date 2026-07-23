Recording a cost
~~~~~~~~~~~~~~~~

#. Go to *Price Manager > Cost Management* and create a record.
#. Fill in the cost name, the item, the supplier and the currency.
#. Enter the EXW, processing and freight costs. The landed cost is computed
   as ``EXW + Processing + Freight`` and cannot be edited.
#. Click **Submit**. The record moves from *Draft* to *Submitted* and the
   input fields become read-only.
#. An approver clicks **Approve** (from the form, or directly from the list
   view button). The record becomes *Active*, the approver and the approval
   date are stamped, any other *Active* cost for the same item is set to
   *Inactive*, and the landed cost is written to the product cost.
#. **Decline** sends a submitted record to *Inactive*; **Deactivate** does the
   same for an already active one.

Recording a selling price
~~~~~~~~~~~~~~~~~~~~~~~~~

#. Go to *Price Manager > Price Management* and create a record.
#. Pick the item first: the *Cost Name* field only proposes cost records
   belonging to that item, and changing the item clears the selected cost.
#. The landed cost is copied from the selected cost record and is read-only.
#. Enter the EXW, processing and freight prices. The selling price is their
   sum, and the gross margin is
   ``(Selling Price - Landed Cost) / Landed Cost``, displayed as a
   percentage.
#. The Submit / Approve / Decline / Deactivate flow is identical to the cost
   one. Approving writes the selling price to the product sales price and
   deactivates the previous active price of that item.

Notes
~~~~~

* Deactivating or declining a record does **not** reset the value already
  written on the product; the product keeps the last approved figure until a
  new record is approved.
* Editing a cost or price component on a record that is already *Active*
  pushes the new value to the product immediately.
