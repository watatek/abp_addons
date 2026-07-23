// @ts-check
const { expect } = require('@playwright/test');

const DB = process.env.ODOO_DB || 'abp';
const LOGIN = process.env.ODOO_LOGIN || 'admin';
const PASSWORD = process.env.ODOO_PASSWORD || 'admin';

/** Authenticate the browser context against Odoo through the login form. */
async function login(page) {
  await page.goto('/web/login');
  const dbInput = page.locator('input[name="db"]');
  if (await dbInput.count()) {
    await dbInput.fill(DB);
  }
  await page.fill('input[name="login"]', LOGIN);
  await page.fill('input[name="password"]', PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/(odoo|web)(\/|\?|$)/);
}

/** Authenticate an APIRequestContext so it can issue call_kw requests. */
async function authenticateRpc(request) {
  const response = await request.post('/web/session/authenticate', {
    data: {
      jsonrpc: '2.0',
      method: 'call',
      params: { db: DB, login: LOGIN, password: PASSWORD },
    },
  });
  const body = await response.json();
  expect(body.error, JSON.stringify(body.error)).toBeUndefined();
  return body.result;
}

/** Call a model method over JSON-RPC and return its result. */
async function callKw(request, model, method, args = [], kwargs = {}) {
  const response = await request.post('/web/dataset/call_kw', {
    data: {
      jsonrpc: '2.0',
      method: 'call',
      params: { model, method, args, kwargs },
    },
  });
  const body = await response.json();
  expect(body.error, JSON.stringify(body.error)).toBeUndefined();
  return body.result;
}

const create = (request, model, vals) =>
  callKw(request, model, 'create', [vals]);

const read = async (request, model, ids, fields) =>
  callKw(request, model, 'read', [ids, fields]);

const write = (request, model, ids, vals) =>
  callKw(request, model, 'write', [ids, vals]);

/** Currency by ISO name, activated so its rate is usable. */
async function currencyByName(request, name) {
  const ids = await callKw(request, 'res.currency', 'search', [
    [['name', '=', name]],
  ], { limit: 1, context: { active_test: false } });
  expect(ids.length, `currency ${name} not found`).toBeGreaterThan(0);
  await write(request, 'res.currency', ids, { active: true });
  return ids[0];
}

/** Set an explicit rate so conversions in the assertions are predictable. */
async function setRate(request, currencyId, companyId, rate, date = '2026-01-01') {
  const existing = await callKw(request, 'res.currency.rate', 'search', [
    [
      ['currency_id', '=', currencyId],
      ['company_id', '=', companyId],
      ['name', '=', date],
    ],
  ]);
  if (existing.length) {
    return write(request, 'res.currency.rate', existing, { rate });
  }
  return create(request, 'res.currency.rate', {
    currency_id: currencyId,
    company_id: companyId,
    name: date,
    rate,
  });
}

/** A storable product usable both in Price Manager and in purchase orders. */
async function makeProduct(request, name) {
  return create(request, 'product.template', {
    name,
    purchase_ok: true,
    is_storable: true,
  });
}

const makePartner = (request, name) =>
  create(request, 'res.partner', { name });

module.exports = {
  DB,
  LOGIN,
  PASSWORD,
  login,
  authenticateRpc,
  callKw,
  create,
  read,
  write,
  currencyByName,
  setRate,
  makeProduct,
  makePartner,
};
