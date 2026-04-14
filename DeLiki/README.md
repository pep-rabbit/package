# DeLiki API

HTTP API-сервіс, який повертає топ аптек у вибраному місті за назвою медичної програми/препарату.

## Архітектурна роль

Модуль відповідає за бізнес-логіку пошуку і ранжування аптек та надає єдиний HTTP-контракт для клієнтів (`Nginx web`, `user-cli`).

## Відповідальність

- читає локальні CSV з `src/data`;
- фільтрує аптеки за населеним пунктом;
- розраховує `activity_score` за агрегованими виплатами;
- повертає відсортований список аптек для клієнтів (web/cli).

## Структура та шари

- `src/main.py` - ініціалізація Litestar-застосунку та CORS.
- `src/endpoin.py` - web-шар: endpoint і схема відповіді (`msgspec.Struct`).
- `src/core/logic.py` - data/business-шар: Polars-пайплайн для фільтрації і ранжування.
- `src/data/` - локальні вхідні датасети.

## Алгоритм

1. У `src/core/logic.py` завантажуються CSV через `polars`.
2. Довідник аптек фільтрується за `city`.
3. Дані оплат агрегуються по `legal_entity_edrpou` в `activity_score`.
4. Набори даних джойняться по коду юридичної особи.
5. Результат фільтрується за `medical_program` і обрізається до топ-5.

## Життєвий цикл запиту

1. Клієнт викликає `GET /api/top-pharmacies`.
2. Endpoint у `src/endpoin.py` передає параметри у `get_top_pharmacies`.
3. `logic.py` виконує lazy-пайплайн Polars та `collect_async()`.
4. Endpoint перетворює DataFrame у typed-структури `PharmacyInfo`.
5. Litestar віддає JSON-відповідь.

## API модуля

### `GET /api/top-pharmacies`

Параметри:

- `city` - назва міста.
- `medical_program` - МНН або назва медичної програми.

Поля відповіді:

- `legal_entity_name`
- `division_name`
- `division_addresses`
- `division_phone`
- `division_type`
- `division_settlement`
- `activity_score`

Приклад:

```text
/api/top-pharmacies?city=Київ&medical_program=Інсуліни
```

## Бібліотеки та підходи

- `litestar` - HTTP-фреймворк і маршрутизація.
- `polars` - швидка обробка CSV, lazy-обчислення, агрегації.
- `msgspec` - типізована серіалізація відповіді.
- `granian` - ASGI-сервер для запуску в контейнері/локально.

Ключовий підхід: heavy-операції виконуються в data-шарі через Polars-пайплайн, endpoint зберігає мінімальну orchestration-логіку.

## Точки розширення

- додати нові фільтри (наприклад, тип відділення, регіон);
- додати інший алгоритм ранжування (комбінований score);
- винести роботу з датасетами в окремий сервіс/репозиторій;
- додати кешування підготовленого DataFrame.

## Запуск модуля окремо

```bash
granian src.main:app --host 0.0.0.0 --port 8080 --interface asgi
```