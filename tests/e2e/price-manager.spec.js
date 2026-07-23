// @ts-check
const { test, expect } = require('@playwright/test');
const {
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
} = require('./helpers');

let session;
let companyId;
let companyCurrencyId;
let usdId;

test.beforeAll(async ({ request }) => {
  session = await authenticateRpc(request);
  companyId = session.user_companies.current_company;
  const [company] = await read(request, 'res.company', [companyId], [
    'currency_id',
  ]);
  companyCurrencyId = company.currency_id[0];
  usdId = await currencyByName(request, 'USD');
  if (usdId !== companyCurrencyId) {
    // 1 company currency = 0.5 USD, so a USD amount doubles once converted.
    await setRate(request, usdId, companyId, 0.5);
  }
});

/** Approve a cost or price record and return it refreshed. */
async function approve(request, model, id, fields) {
  await callKw(request, model, 'action_submit', [[id]]);
  await callKw(request, model, 'action_approve', [[id]]);
  const [record] = await read(request, model, [id], fields);
  return record;
}

test.describe('sales.cost approval', () => {
  test('only the same item and supplier pair is deactivated', async ({
    request,
  }) => {
    const productId = await makeProduct(request, 'PW Cost Item');
    const supplierA = await makePartner(request, 'PW Supplier A');
    const supplierB = await makePartner(request, 'PW Supplier B');

    const costA = await create(request, 'sales.cost', {
      name: 'PW Cost A1',
      product_template_id: productId,
      partner_id: supplierA,
      exw_cost: 100,
    });
    const costB = await create(request, 'sales.cost', {
      name: 'PW Cost B1',
      product_template_id: productId,
      partner_id: supplierB,
      exw_cost: 80,
    });
    await approve(request, 'sales.cost', costA, ['state']);
    await approve(request, 'sales.cost', costB, ['state']);

    // Supplier B's approval must leave supplier A's cost alone.
    const [a] = await read(request, 'sales.cost', [costA], ['state']);
    expect(a.state).toBe('active');

    const costA2 = await create(request, 'sales.cost', {
      name: 'PW Cost A2',
      product_template_id: productId,
      partner_id: supplierA,
      exw_cost: 120,
    });
    await approve(request, 'sales.cost', costA2, ['state']);

    const records = await read(
      request,
      'sales.cost',
      [costA, costA2, costB],
      ['state'],
    );
    const byId = Object.fromEntries(records.map((r) => [r.id, r.state]));
    expect(byId[costA]).toBe('inactive');
    expect(byId[costA2]).toBe('active');
    expect(byId[costB]).toBe('active');
  });

  test('landed cost sums the components and converts to company currency', async ({
    request,
  }) => {
    test.skip(usdId === companyCurrencyId, 'company already runs in USD');
    const productId = await makeProduct(request, 'PW Converted Cost Item');
    const supplierId = await makePartner(request, 'PW Converted Supplier');
    const costId = await create(request, 'sales.cost', {
      name: 'PW Converted Cost',
      product_template_id: productId,
      partner_id: supplierId,
      currency_id: usdId,
      exw_cost: 60,
      processing_cost: 30,
      freight_cost: 10,
    });

    const [cost] = await read(request, 'sales.cost', [costId], [
      'landed_cost',
      'landed_cost_company',
      'landed_cost_display',
    ]);
    expect(cost.landed_cost).toBeCloseTo(100, 2);
    // rate 0.5: 100 USD is worth 200 in the company currency.
    expect(cost.landed_cost_company).toBeCloseTo(200, 2);
    expect(cost.landed_cost_display).toContain('=');
  });
});

test.describe('sales.price margin', () => {
  test('gross margin converts the landed cost into the price currency', async ({
    request,
  }) => {
    test.skip(usdId === companyCurrencyId, 'company already runs in USD');
    const productId = await makeProduct(request, 'PW Margin Item');
    const supplierId = await makePartner(request, 'PW Margin Supplier');
    const costId = await create(request, 'sales.cost', {
      name: 'PW Margin Cost',
      product_template_id: productId,
      partner_id: supplierId,
      currency_id: usdId,
      exw_cost: 100,
    });
    const priceId = await create(request, 'sales.price', {
      name: 'PW Margin Price',
      product_template_id: productId,
      cost_id: costId,
      currency_id: companyCurrencyId,
      exw_price: 250,
    });

    const [price] = await read(request, 'sales.price', [priceId], [
      'landed_cost',
      'landed_cost_converted',
      'selling_price',
      'gross_margin',
      'landed_cost_display',
      'selling_price_display',
    ]);
    expect(price.landed_cost).toBeCloseTo(100, 2);
    // 100 USD becomes 200 in the price (company) currency.
    expect(price.landed_cost_converted).toBeCloseTo(200, 2);
    expect(price.selling_price).toBeCloseTo(250, 2);
    // (250 - 200) / 200
    expect(price.gross_margin).toBeCloseTo(0.25, 4);
    expect(price.landed_cost_display).toContain('=');
    expect(price.selling_price_display).not.toContain('=');
  });

  test('approving pushes the selling price onto the product', async ({
    request,
  }) => {
    const productId = await makeProduct(request, 'PW Publish Item');
    const supplierId = await makePartner(request, 'PW Publish Supplier');
    const costId = await create(request, 'sales.cost', {
      name: 'PW Publish Cost',
      product_template_id: productId,
      partner_id: supplierId,
      exw_cost: 50,
    });
    await approve(request, 'sales.cost', costId, ['state']);
    const priceId = await create(request, 'sales.price', {
      name: 'PW Publish Price',
      product_template_id: productId,
      cost_id: costId,
      exw_price: 90,
    });
    await approve(request, 'sales.price', priceId, ['state']);

    const [product] = await read(request, 'product.template', [productId], [
      'standard_price',
      'list_price',
    ]);
    expect(product.standard_price).toBeCloseTo(50, 2);
    expect(product.list_price).toBeCloseTo(90, 2);
  });
});

test.describe('purchase order pricing', () => {
  /** Build a draft order line the way the web client does. */
  async function newOrderLine(request, orderId, productId) {
    return create(request, 'purchase.order.line', {
      order_id: orderId,
      product_id: productId,
      product_qty: 1,
    });
  }

  test("a set vendor prices the line from that vendor's cost", async ({
    request,
  }) => {
    const templateId = await makeProduct(request, 'PW PO Item');
    const [template] = await read(request, 'product.template', [templateId], [
      'product_variant_id',
    ]);
    const variantId = template.product_variant_id[0];
    const cheap = await makePartner(request, 'PW Cheap Vendor');
    const pricey = await makePartner(request, 'PW Pricey Vendor');

    const cheapCost = await create(request, 'sales.cost', {
      name: 'PW PO Cheap',
      product_template_id: templateId,
      partner_id: cheap,
      exw_cost: 70,
    });
    const priceyCost = await create(request, 'sales.cost', {
      name: 'PW PO Pricey',
      product_template_id: templateId,
      partner_id: pricey,
      exw_cost: 130,
    });
    await approve(request, 'sales.cost', cheapCost, ['state']);
    await approve(request, 'sales.cost', priceyCost, ['state']);

    const orderId = await create(request, 'purchase.order', {
      partner_id: pricey,
    });
    const lineId = await newOrderLine(request, orderId, variantId);
    const [line] = await read(request, 'purchase.order.line', [lineId], [
      'price_unit',
    ]);
    expect(line.price_unit).toBeCloseTo(130, 2);
  });

  test('a manual price is never overwritten', async ({ request }) => {
    const templateId = await makeProduct(request, 'PW PO Manual Item');
    const [template] = await read(request, 'product.template', [templateId], [
      'product_variant_id',
    ]);
    const variantId = template.product_variant_id[0];
    const vendorId = await makePartner(request, 'PW Manual Vendor');
    const costId = await create(request, 'sales.cost', {
      name: 'PW PO Manual Cost',
      product_template_id: templateId,
      partner_id: vendorId,
      exw_cost: 45,
    });
    await approve(request, 'sales.cost', costId, ['state']);

    const orderId = await create(request, 'purchase.order', {
      partner_id: vendorId,
    });
    const lineId = await newOrderLine(request, orderId, variantId);
    await write(request, 'purchase.order.line', [lineId], { price_unit: 999 });
    await write(request, 'purchase.order.line', [lineId], { product_qty: 3 });

    const [line] = await read(request, 'purchase.order.line', [lineId], [
      'price_unit',
    ]);
    expect(line.price_unit).toBeCloseTo(999, 2);
  });
});

test.describe('price form rendering', () => {
  test('the landed cost line shows both currencies', async ({
    page,
    request,
  }) => {
    test.skip(usdId === companyCurrencyId, 'company already runs in USD');
    const productId = await makeProduct(request, 'PW Form Item');
    const supplierId = await makePartner(request, 'PW Form Supplier');
    const costId = await create(request, 'sales.cost', {
      name: 'PW Form Cost',
      product_template_id: productId,
      partner_id: supplierId,
      currency_id: usdId,
      exw_cost: 100,
    });
    const priceId = await create(request, 'sales.price', {
      name: 'PW Form Price',
      product_template_id: productId,
      cost_id: costId,
      currency_id: companyCurrencyId,
      exw_price: 250,
    });

    await login(page);
    await page.goto(
      `/odoo/action-abp_price_manager.action_price_management/${priceId}`,
    );
    const landed = page.locator('.o_form_view [name="landed_cost_display"]');
    await expect(landed).toContainText('=');
    await expect(
      page.locator('.o_form_view [name="gross_margin"]'),
    ).toContainText('25');
  });
});
