const { defineConfig, devices } = require('@playwright/test');
module.exports = defineConfig({
  testDir: './tests', timeout: 60000, retries: process.env.CI ? 1 : 0,
  reporter: [['list'], ['html', { outputFolder: 'playwright-report', open: 'never' }]],
  use: { baseURL: process.env.QA_BASE_URL, browserName: 'chromium', locale: 'ru-RU', timezoneId: 'Europe/Chisinau', colorScheme: 'dark', reducedMotion: 'reduce', trace: 'retain-on-failure' },
  projects: [
    { name: 'desktop', use: { browserName: 'chromium', viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 } },
    { name: 'mobile', use: { ...devices['iPhone 13'], browserName: 'chromium', viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 } }
  ]
});
