/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        // Paleta pastel basada en el logo de Papelera La Plata
        turquesa: {
          50: '#effbfb', 100: '#d9f5f5', 200: '#bdeeee', 300: '#9de5e5', 400: '#7fdcdc',
          500: '#5ccaca', 600: '#3fb0b0', 700: '#2a8a8a', 800: '#226e6e', 900: '#1d5a5a',
        },
        rojo: {
          50: '#fef4f3', 100: '#fde3e1', 200: '#fbcdca', 300: '#f8b0ab', 400: '#f58f88',
          500: '#ea7770', 600: '#d95f58', 700: '#b44740', 800: '#913a34', 900: '#76322d',
        },
        amarillo: { 50: '#fffbef', 100: '#fdf2cf', 200: '#fbe8ad', 400: '#f8db8f', 500: '#f0c860', 700: '#9a7419' },
        violeta: { 50: '#f7f5ff', 100: '#eeeaff', 200: '#ddd5fe', 400: '#c9bbfb', 500: '#b4a3f3', 700: '#6a56c2' },
        tinta: { DEFAULT: '#1c1c1c', 700: '#3a3a3a', 500: '#666666', 300: '#a8a8a8', 200: '#dcdde3', 100: '#ededed', 50: '#f8f8f6' },
      },
      fontFamily: {
        display: ['Oswald', 'Impact', 'sans-serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(17,17,17,.03), 0 4px 16px rgba(17,17,17,.05)',
        pop: '0 12px 40px rgba(17,17,17,.12)',
      },
    },
  },
  plugins: [],
}
