# Nginx (web)

Модуль Nginx, який обслуговує статичний фронтенд і проксіює API-запити у backend-контейнер.

## Архітектурна роль

Модуль є edge-рівнем системи: приймає HTTP-трафік користувача, віддає frontend-статику і маршрутизує API-запити у backend.

## Відповідальність

- віддача `web/index.html`, `web/style.css`, `web/script.js`;
- reverse proxy для `/api/*` на `http://api:8080`;
- SPA-fallback через `try_files`.

## Структура

- `default.conf` - Nginx-конфігурація маршрутизації.
- `web/index.html` - сторінка інтерфейсу.
- `web/style.css` - стилі.
- `web/script.js` - запити до API і рендер результатів.

## Як це працює

1. Користувач відкриває `/`, Nginx повертає `index.html`.
2. `script.js` відправляє запит на `/api/top-pharmacies`.
3. `location /api/` проксіює запит на `http://api:8080/api/`.
4. Відповідь API повертається в браузер без CORS-конфлікту.
5. За кнопкою збереження frontend формує `pharmacies_report.json` через Blob.

## Конфігурація маршрутизації (`default.conf`)

- контейнер слухає `80` порт;
- `location /api/` проксіюється на backend-сервіс `api`;
- статика обслуговується з `/usr/share/nginx/html`.

## Бібліотеки та підходи

- Nginx як reverse proxy + static server;
- frontend без framework-залежностей (vanilla JS);
- SPA-поведінка через `try_files $uri $uri/ /index.html`.

## Точки розширення

- додати кешування/стиснення статики (gzip або brotli);
- налаштувати security headers (CSP, X-Frame-Options, Referrer-Policy);
- додати health endpoint і тонкі timeout/retry-параметри proxy;
- розділити dev/prod конфіги Nginx.

## Запуск модуля

Модуль розрахований на запуск у складі `docker compose` з кореня проєкту:

```bash
docker compose up --build
```
