# CRM Product Creation & Approval

Add-on for **Dynamic Approval Workflow** (v19.0.1.0). This module does **not**
modify `dynamic_approval_workflow` — it only depends on it and adds new
configuration and views on top of `product` and `crm`.

## Installation

This folder must sit **next to** (not inside) `dynamic_approval_workflow` in
your Odoo custom `addons_path`, e.g.:

```
custom-addons/
├── dynamic_approval_workflow/
└── crm_product_approval/
```

Then, as usual: Apps > Update Apps List > search "CRM Product Creation &
Approval" > Install.

## Part 1 — Product Approval

`product.template` now inherits `approval.mixin`, the same engine already
used for Sales Orders in `dynamic_approval_workflow`:

- **Submit for Approval** button + **Approval Status** badge + **Approvals**
  smart button on the Product form (same pattern as the Sales Order sample).
- A ready-to-use `approval.workflow.config` named *Product Price Approval*
  is seeded (`data/approval_workflow_data.xml`) with one stage, *Accounting
  Price Approval*.
- While pending approval (or rejected), the product is kept **archived**
  (`active = False`) so it cannot be picked on quotations/purchase orders.
  It is re-activated automatically once approved.
- **Reset to Draft** button lets the requester edit and resubmit a
  rejected/returned product.

### Point the approval to your real Accounting group

Out of the box the stage approver is the generic *Approval Manager* group
from Dynamic Approval Workflow (so it works immediately after install).
If the Accounting/Invoicing app is installed, go to
*Approvals > Configuration > Workflow Configs > Product Price Approval*,
open its stage, and change **Approver Group** to your real Accounting group
(e.g. *Billing Administrator*), or switch **Approver Type** to *Specific
User* / *Dynamic Field* if you prefer.

## Part 2 — CRM Pipeline product creation

- `crm.stage` gets a new **Create Product** checkbox (CRM > Configuration >
  Stages, or Settings > Technical > CRM > Stages).
- On the Pipeline form, when the opportunity's current stage has that
  checkbox enabled, an extra **New Products** tab appears next to
  **Contacts**, with an editable product list.
- Any product created there is linked to the opportunity
  (`product.template.crm_lead_id`) and is **automatically submitted** to the
  Product Approval workflow from Part 1 — no manual click needed.

## Files

```
crm_product_approval/
├── __init__.py
├── __manifest__.py
├── data/
│   └── approval_workflow_data.xml   # seeds the Product Price Approval config
├── models/
│   ├── __init__.py
│   ├── product_template.py          # approval.mixin + auto submit/archive
│   ├── crm_stage.py                 # create_product checkbox
│   └── crm_lead.py                  # product_ids one2many + tab visibility
└── views/
    ├── product_template_views.xml   # Submit/Approve UI on the Product form
    ├── crm_stage_views.xml          # checkbox on the Stage config form
    └── crm_lead_views.xml           # "New Products" tab on the Pipeline form
```
