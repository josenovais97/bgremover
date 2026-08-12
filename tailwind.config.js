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
      // Inter is self-hosted (static/css/inter.css). There is deliberately no
      // second `display` family: two have now been tried and removed (Bricolage
      // Grotesque, which was configured for months without a single @font-face
      // behind it, and Instrument Serif, which was real but fought the interface
      // it sat in). Weight and size carry the hierarchy instead.
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        // Resolve to CSS variables so each page can set its own accent (the
        // per-tool signature colour) — see input.css :root and base.html.
        // primary/primaryHover are SURFACES (white text sits on them, so they
        // don't vary by theme); primaryText is the accent as TEXT on the page
        // background, and inverts in dark mode. Using primary for text is the
        // bug this split exists to prevent — reach for primaryText there.
        primary: 'rgb(var(--color-primary) / <alpha-value>)',
        primaryHover: 'rgb(var(--color-primary-hover) / <alpha-value>)',
        primaryText: 'rgb(var(--color-primary-text) / <alpha-value>)',
        // Second text stop, for a gradient painted as text (bg-clip-text).
        primaryTextAlt: 'rgb(var(--color-primary-text-alt) / <alpha-value>)',
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
        // Scroll-triggered reveal. Deliberately small: 10px and a fifth of a
        // second reads as "the page is alive", 40px and half a second reads as
        // "the page is slow". Only transform + opacity, so it stays on the
        // compositor and cannot cause layout.
        'rise': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'none' },
        },
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.5s ease-out both',
        'float': 'float 6s ease-in-out infinite',
        'rise': 'rise 0.42s cubic-bezier(.22,.68,.3,1) both',
      },
    },
  },
  plugins: [],
};
