import type { Config } from 'tailwindcss'

export default {
    content: [
        './app/**/*.{vue,js,ts}',
        './components/**/*.{vue,js,ts}',
        './layouts/**/*.vue',
        './pages/**/*.vue',
        './plugins/**/*.{js,ts}',
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                // Primary - Syuuraa Green
                primary: {
                    DEFAULT: '#166534',
                    50: '#f0fdf4',
                    100: '#dcfce7',
                    200: '#bbf7d0',
                    300: '#86efac',
                    400: '#4ade80',
                    500: '#22c55e',
                    600: '#16a34a',
                    700: '#166534',
                    800: '#14532d',
                    900: '#052e16',
                },
                // Secondary - Gold
                secondary: {
                    DEFAULT: '#CA8A04',
                    50: '#fefce8',
                    100: '#fef9c3',
                    200: '#fef08a',
                    300: '#fde047',
                    400: '#facc15',
                    500: '#eab308',
                    600: '#ca8a04',
                    700: '#a16207',
                    800: '#854d0e',
                    900: '#713f12',
                },
            },
            fontFamily: {
                sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
                arabic: ['Amiri', 'serif'],
            },
        },
    },
    plugins: [],
} satisfies Config
