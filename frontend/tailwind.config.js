/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        soc: {
          bg: "#0f172a",
          panel: "#1e293b",
          border: "#334155",
          accent: "#38bdf8",
        },
      },
    },
  },
  plugins: [],
};
