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
      // All three faces are self-hosted (static/css/inter.css + display.css).
      //
      // The old note here said there was "deliberately no second display family"
      // because one had been configured and never used. The opposite had quietly
      // become true: input.css named Bricolage Grotesque in its `h1` rule with no
      // @font-face behind it, so every headline on the site rendered in Inter
      // while claiming otherwise. Both faces are now real files.
      //
      //   sans     Inter — body, UI, everything unmarked
      //   display  Bricolage Grotesque — headlines and the knockout
      //   mono     IBM Plex Mono — DATA only (dimensions, formats, model names)
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Instrument Serif', 'Georgia', 'Times New Roman', 'serif'],
        mono: ['Plex Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      colors: {
        // THE NEUTRAL RAMP IS THE DIRECTION.
        //
        // Passe-partout is built on mat board and paper, not on white and blue-
        // grey — and the whole site is written in Tailwind's `gray-*` utilities.
        // Redefining the ramp here re-grounds every existing border, caption and
        // muted label at once, with no template churn: `bg-white` still means
        // paper (the mount), `gray-200` still means a hairline, they are simply
        // the right colours now. Doing this by hand would have meant editing
        // ~47 templates and would have drifted the first time one was missed.
        //
        // Green-grey rather than blue-grey, keyed to the mat board (#E7E8E3).
        // Every step from 500 down clears AA as text on the mat board, which the
        // old blue-grey 400/500 did not — see AccentContrastTests, which now
        // measures against the real ground instead of against white.
        gray: {
          50:  '#F7F7F5',  // paper, one step off white
          100: '#EFEFEC',
          200: '#E1E2DC',  // hairlines
          300: '#C7C9C1',
          400: '#63685F',  // small uppercase labels — 4.64:1 on mat board
          500: '#54594F',  // secondary text
          600: '#4B4F47',  // body copy — 6.80:1
          700: '#383B35',
          800: '#282A25',
          900: '#1B1D1A',  // ink
          950: '#131511',
        },
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
