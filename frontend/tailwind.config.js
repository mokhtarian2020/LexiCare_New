/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Palette healthcare professionale
        primary: {
          light: '#E3F2FD',
          DEFAULT: '#1976D2',
          dark: '#0D47A1',
        },
        secondary: {
          light: '#E8F5E9',
          DEFAULT: '#2E7D32',
          dark: '#1B5E20',
        },
        danger: {
          light: '#FFEBEE',
          DEFAULT: '#D32F2F',
          dark: '#B71C1C',
        },
        warning: {
          light: '#FFF8E1',
          DEFAULT: '#FFA000',
          dark: '#FF6F00',
        },
        neutral: {
          light: '#ECEFF1',
          DEFAULT: '#607D8B',
          dark: '#263238',
        },
        sanitario: '#0277BD', // Blu sanitario italiano
      },
      fontFamily: {
        sans: [
          'Inter',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif'
        ],
      },
      boxShadow: {
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
    },
  },
  plugins: [],
};
