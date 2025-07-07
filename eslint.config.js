import tseslint from '@typescript-eslint/eslint-plugin';
import tsParser from '@typescript-eslint/parser';

export default [
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
