# End-to-end tests

Playwright suite driving a **running** Odoo instance — it does not start one.

## Setup

```bash
cd tests
npm install
npx playwright install chromium
```

## Run

Start Odoo with `../odoo.conf` and the `abp_price_manager` module installed on
the target database, then:

```bash
ODOO_DB=abp ODOO_LOGIN=admin ODOO_PASSWORD=admin npm test
```

| Variable | Default |
| --- | --- |
| `ODOO_URL` | `http://localhost:8069` |
| `ODOO_DB` | `abp` |
| `ODOO_LOGIN` | `admin` |
| `ODOO_PASSWORD` | `admin` |

`npm run test:headed` watches the browser, `npm run report` opens the HTML
report.

## What is covered

`e2e/price-manager.spec.js` — approving a cost only deactivates the previous
one of the same item **and** supplier, multi-currency landed cost and gross
margin, approved values reaching the product, purchase order lines priced from
the approved cost (and manual prices left alone), plus a form-rendering check
of the `amount = converted amount` lines.

Records are created through JSON-RPC and left behind; run against a scratch
database. The currency assertions pin the USD rate to `0.5` on `2026-01-01`
and are skipped when the company already runs in USD.
