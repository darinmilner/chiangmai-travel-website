/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./templates/**/*.html",
        "./templates/**/*.tmpl",
        "./templates/**/*.gohtml",
        "./static/**/*.js",
    ],
    theme: {
        extend: {
            colors: {
                // ---------- Resort-Style Green Palette ----------
                'resort-green': '#1B5E20',      // Primary - dark, luxurious
                'deep-teal': '#004D40',          // Secondary - resort feel
                'sage-green': '#558B2F',         // Accent - natural
                'palm-green': '#A5D6A7',         // Light background
                'mint': '#C8E6C9',               // Alternative light green

                // ---------- Brown Palette (Meat Shop) ----------
                'brown-deep': '#5D4037',
                'brown-earth': '#6D4C41',
                'brown-light': '#8D6E63',

                // ---------- Neutrals ----------
                'warm-sand': '#F5E6D3',
                'cream-white': '#FAF7F2',
                'charcoal': '#333333',

                // ---------- Accents ----------
                'amber': '#E8A317',
                'terracotta': '#D2691E',
            },
            fontFamily: {
                'sans': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
                'heading': ['Poppins', 'Inter', 'sans-serif'],
            },
        },
    },
    plugins: [],
}