/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        cream: "#FAF3E8",
        "cream-deep": "#F2E8D8",
        ink: "#2B2420",
        "ink-soft": "#5C5147",
        cookbook: {
          50: "#EEF1ED",
          100: "#D7DED4",
          400: "#5C7259",
          600: "#3D5240",
          700: "#2F4032",
          900: "#1C2A1E",
        },
        terracotta: {
          400: "#D98A5F",
          500: "#C7754A",
          600: "#A65E38",
        },
        gold: {
          400: "#E3BD7E",
          500: "#D4A85A",
          600: "#B8893D",
        },
      },
      fontFamily: {
        display: ["Fraunces", "ui-serif", "Georgia", "serif"],
        body: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "paper-texture":
          "radial-gradient(circle at 1px 1px, rgba(43,36,32,0.04) 1px, transparent 0)",
      },
    },
  },
  plugins: [],
};
