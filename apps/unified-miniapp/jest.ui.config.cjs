module.exports = {
  rootDir: __dirname,
  globalTeardown: '@dcloudio/uni-automator/dist/teardown.js',
  testEnvironment: '<rootDir>/tests/uni-automator-environment.cjs',
  testEnvironmentOptions: {
    compile: true,
    platform: 'mp-weixin',
    projectPath: __dirname,
    'mp-weixin': {
      port: Number(process.env.WECHAT_DEVTOOLS_AUTO_PORT || 9420),
      account: process.env.WECHAT_DEVTOOLS_ACCOUNT || '',
      args: process.env.WECHAT_DEVTOOLS_ARGS || '',
      cwd:
        process.env.WECHAT_DEVTOOLS_CWD ||
        'C:/Program Files (x86)/Tencent/微信web开发者工具',
      launch: true,
      teardown: process.env.UNI_AUTOMATOR_TEARDOWN || 'disconnect',
      remote: process.env.UNI_AUTOMATOR_REMOTE === 'true',
    },
  },
  testMatch: ['<rootDir>/tests/test_ui.js'],
  testTimeout: 180000,
  reporters: ['default'],
  watchPathIgnorePatterns: ['/node_modules/', '/dist/', '/.git/'],
  moduleFileExtensions: ['js', 'json'],
  testPathIgnorePatterns: ['/node_modules/'],
}
