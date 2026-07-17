# Copyright 2026
{
    "name": "CRM Product Creation & Approval",
    "version": "19.0.1.0.0",
    "summary": (
        "Applies the Dynamic Approval Workflow to Products and lets CRM "
        "stages open an in-pipeline product creation tab"
    ),
    "description": """
CRM Product Creation & Approval
================================

This module is an *add-on* to ``dynamic_approval_workflow`` — it does not
modify that module in any way, it only depends on it and adds new
configuration / views on top of it and of ``product`` / ``crm``.

Part 1 — Product Approval (mirrors the Sales Order sample)
------------------------------------------------------------
* ``product.template`` inherits ``approval.mixin`` (same engine already used
  for Sales Orders in ``dynamic_approval_workflow``).
* A ready-to-use ``approval.workflow.config`` is seeded for the
  ``product.template`` model (see ``data/approval_workflow_data.xml``) —
  duplicate/edit it from *Approvals > Configuration > Workflow Configs* the
  same way the Sales Order one is edited.
* The Product form gets a *Submit for Approval* button, an *Approval
  Status* badge and an *Approvals* smart button, just like Sales Orders.
* While a product's ``approval_state`` is ``pending_approval``, ``rejected``
  or freshly created via the CRM tab below, it is kept **archived**
  (``active = False``) so it cannot be selected on quotations or purchase
  orders until Accounting approves its selling price / cost price. It is
  automatically re-activated as soon as it is approved.
* A *Reset to Draft* button lets the requester edit and resubmit a
  rejected/returned product.

Part 2 — CRM Pipeline product creation
------------------------------------------------------------
* ``crm.stage`` gets a new **Create Product** checkbox (Settings >
  Technical > CRM > Stages, or CRM > Configuration > Stages).
* On the Pipeline (opportunity) form, when the current stage has that
  checkbox enabled, an extra **New Products** tab appears next to
  **Contacts**, showing an editable list of products linked to that
  opportunity where salespeople can create new products inline.
* Any product created from that tab is automatically submitted to the
  Product Approval workflow from Part 1 — no extra click required.
    """,
    "author": "Snow",
    "website": "",
    "category": "Sales/CRM",
    "depends": ["dynamic_approval_workflow", "product", "crm"],
    "data": [
        "data/approval_workflow_data.xml",
        "views/product_template_views.xml",
        "views/crm_stage_views.xml",
        "views/crm_lead_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
