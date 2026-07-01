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
                'brown-deep': '#5D4037',
                'brown-earth': '#6D4C41',
                'brown-light': '#8D6E63',
                'forest-green': '#2E7D32',
                'olive-green': '#6B8E23',
                'moss-green': '#7CB342',
                'light-sage': '#C5D8B5',
                'warm-sand': '#F5E6D3',
                'cream-white': '#FAF7F2',
                'charcoal': '#333333',
                'amber': '#E8A317',
                'terracotta': '#D2691E',
            },
            fontFamily: {
                'sans': ['Inter', 'system-ui', 'sans-serif'],
                'heading': ['Poppins', 'Inter', 'sans-serif'],
            },
        },
    },
    plugins: [],
}