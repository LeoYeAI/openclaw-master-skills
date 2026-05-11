const js = require('@eslint/js');
const {
  baseRules,
  testRules,
  nodeGlobals,
  testGlobals,
  ignores,
} = require('../_config/eslint.base.js');

module.exports = [
  js.configs.recommended,
  {
    files: ['src/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      globals: nodeGlobals,
    },
    rules: baseRules,
  },
  {
    files: ['tests/**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
      globals: testGlobals,
    },
    rules: testRules,
  },
  { ignores },
];
