/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    fontFamily: {
      sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
    },
    extend: {
      colors: {
        primary: {
          light: '#7B68EE', // Light blue
          DEFAULT: '#1E90FF', // Blue
          dark: '#5263ff', // Dark blue
        },
        secondary: {
          light: '#a0aec0', // Light gray
          DEFAULT: '#718096', // Gray
          dark: '#2d3748', // Dark gray
        },
        background: '#f7fafc', // Very light gray/off-white
        surface: '#ffffff', // White
        error: '#e53e3e', // Red
        success: '#48bb78', // Green
        warning: '#ed8936', // Orange
      },
    },
  },
  plugins: [],
}

