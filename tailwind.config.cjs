module.exports = {
  content: [
    './src/**/*.{astro,html,js,jsx,ts,tsx}',
    './node_modules/flowbite/**/*.js' // Si usas Flowbite
  ],
  theme: {
    extend: {
      colors: {
        'gft-blue': '#213f7f',
        'gft-blue-light': '#3a5a9a',
      },
      fontFamily: {
        sans: ['Noto Sans', 'sans-serif'],
        montserrat: ['Montserrat', 'sans-serif'],
      },
      animation: {
        fadeIn: 'fadeIn 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('flowbite/plugin') // Opcional
  ],
}