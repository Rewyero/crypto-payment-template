/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'background-dark': '#1a1c2e',
        'background-darker': '#13141f',
        'text': '#a3bffa',
        'text-light': '#dde4ff',
        'text-dark': '#718096',
        'accent-blue': '#4a90e2',
        'accent-purple': '#9f7aea',
      },
      fontFamily: {
        'sans': ['Inter', 'ui-sans-serif', 'system-ui'],
        'space': ['Space Mono', 'monospace'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
  ],
} 