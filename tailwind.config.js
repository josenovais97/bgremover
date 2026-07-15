/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
  ],
  // Classes assembled dynamically in JS (toasts) — keep them from being purged.
  safelist: [
    { pattern: /(bg|text|border)-(green|red|blue)-(50|200|500|800)/, variants: ['dark'] },
    { pattern: /(bg|text|border)-(green|red|blue)-900\/40/, variants: ['dark'] },
    { pattern: /(bg|text|border)-(green|red|blue)-(200|800)\/40/, variants: ['dark'] },
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['"Bricolage Grotesque"', 'Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Resolve to CSS variables so each page can set its own accent (the
        // per-tool signature colour) — see input.css :root and base.html.
        primary: 'rgb(var(--color-primary) / <alpha-value>)',
        primaryHover: 'rgb(var(--color-primary-hover) / <alpha-value>)',
      },
      keyframes: {
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'float': {
          '0%,100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.5s ease-out both',
        'float': 'float 6s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
