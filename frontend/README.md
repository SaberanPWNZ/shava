# Svelte + Vite + Tailwind CSS

Цей проект створений з шаблоном Svelte + Vite та налаштованим Tailwind CSS для стилізації.

## 🚀 Встановлені технології

- **Svelte 5** - реактивний фреймворк з новими runes
- **Vite** - швидкий bundler та dev server
- **Tailwind CSS** - utility-first CSS фреймворк
- **PostCSS** - для обробки CSS
- **Autoprefixer** - автоматичні вендорні префікси

## 🛠️ Рекомендовані розширення VS Code

- [Svelte for VS Code](https://marketplace.visualstudio.com/items?itemName=svelte.svelte-vscode)
- [Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss)

## 📂 Структура проекту

```
frontend/
├── src/
│   ├── lib/           # Svelte компоненти
│   ├── assets/        # Статичні ресурси
│   ├── App.svelte     # Головний компонент
│   ├── main.js        # Точка входу
│   └── app.css        # Tailwind CSS директиви
├── public/            # Публічні файли
└── index.html         # HTML шаблон
```

## 🚀 Команди

```bash
# Встановлення залежностей
npm install

# Запуск dev сервера
npm run dev

# Збірка для production
npm run build

# Попередній перегляд production збірки
npm run preview
```

## 🎨 Використання Tailwind CSS

Проект налаштований для використання Tailwind CSS. Всі стилі можна писати за допомогою utility класів:

```svelte
<div class="bg-blue-500 text-white p-4 rounded-lg hover:bg-blue-600 transition-colors">
  Приклад з Tailwind класами
</div>
```

## 🔧 Налаштування

- `tailwind.config.js` - конфігурація Tailwind CSS
- `postcss.config.js` - конфігурація PostCSS
- `vite.config.js` - конфігурація Vite
- `svelte.config.js` - конфігурація Svelte

## 📚 Додаткова інформація

Для більших проектів розгляньте можливість використання [SvelteKit](https://github.com/sveltejs/kit#readme), який надає повноцінний фреймворк з роутингом, SSR та іншими можливостями.
