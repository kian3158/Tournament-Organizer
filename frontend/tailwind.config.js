/** @type {import('tailwindcss').Config} */
const token = (name) => `rgb(var(${name}) / <alpha-value>)`;

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: token("--bg"),
        surface: token("--surface"),
        elevated: token("--elevated"),
        border: token("--border"),
        fg: token("--fg"),
        muted: token("--muted"),
        accent: {
          DEFAULT: token("--accent"),
          hover: token("--accent-hover"),
          fg: token("--accent-fg"),
        },
        win: token("--win"),
        danger: token("--danger"),
      },
      borderColor: {
        DEFAULT: token("--border"),
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ['"Space Grotesk"', "Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
