// @ts-check
const { defineConfig, devices } = require('@playwright/test');

/**
 * The suite drives a running Odoo instance (see ../odoo.conf), it does not
 * start one. Override the target with ODOO_URL / ODOO_DB / ODOO_LOGIN /
 * ODOO_PASSWORD.
 */
module.exports = defineConfig({
  testDir: './e2e',
  timeout: 120_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.ODOO_URL || 'http://localhost:8069',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'off',
    viewport: { width: 1600, height: 900 },
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});
