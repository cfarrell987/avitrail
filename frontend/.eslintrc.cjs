module.exports = {
  root: true,
  env: {
    browser: true,
    es2022: true,
    node: true
  },
  extends: ['eslint:recommended', 'plugin:vue/vue3-essential'],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    'no-unused-vars': 'warn',
    // Page/layout components (Dashboard.vue, Home.vue, Navbar.vue, ...) are
    // never used as custom HTML tags, so there's no risk of colliding with
    // a native/future element name — the rule's actual concern.
    'vue/multi-word-component-names': 'off'
  }
}
