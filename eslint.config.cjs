const tseslint = require('@typescript-eslint/eslint-plugin');
const tsParser = require('@typescript-eslint/parser');

module.exports = [
  {
    files: ['**/*.{js,ts,tsx}'],
    ignores: ['**/node_modules/**', 'dist'],
    languageOptions: {
      ecmaVersion: 2024,
      sourceType: 'module',
      parser: tsParser
    },
    plugins: {
      '@typescript-eslint': tseslint
    },
    rules: {}
  }
];
