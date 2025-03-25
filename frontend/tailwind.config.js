/** @type {import('tailwindcss').Config} */
module.exports = {
  // Define content sources - all HTML templates and JavaScript files
  content: [
    "../app/templates/**/*.html",
    "../app/static/js/**/*.js",
  ],
  // Enable dark mode by default
  darkMode: 'class',
  theme: {
    extend: {
      // We can extend the default theme here later if needed
    },
  },
  // Include DaisyUI and Typography plugins
  plugins: [
    require('daisyui'),
    require('@tailwindcss/typography')
  ]
}
