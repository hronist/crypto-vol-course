# Анализ опционного рынка для крипто-квантов

Мини-курс по тому, как аналитики оценивают рынок опционов — для сильных крипто-нативов
(понимающих стакан, AMM, перпы, фандинг, арбитраж, MEV, Rust/ноды), но не работавших с
опционами.

Каждый урок — отдельная статья с определениями терминов по ходу, **Словарём урока** и
контрольными вопросами в конце.

- 📚 Полный план курса (12 уроков, 4 блока, пороги готовности): [SYLLABUS.md](SYLLABUS.md)
- 📂 Уроки: каталог [`lessons/`](lessons/)

## Уроки

1. [Основы анализа опционного рынка (crypto edition)](lessons/lesson-01-osnovy-analiza-opcionov.md)
   — базовый словарь опционов; IV/RV/VRP; мост «AMM LP ≈ short straddle, IL = short gamma»;
   греки, поверхность волатильности, индекс IV (крипто-VIX), funding; цели и задачи анализа.
2. [Модели ценообразования опционов (crypto edition)](lessons/lesson-02-modeli-cenoobrazovaniya.md)
   — безарбитражность, риск-нейтральная оценка, put-call parity через перп-базис,
   Black-Scholes, переход цена ↔ IV, греки как производные; крипто-специфика:
   линейные vs обратные контракты, 24/7, carry вместо ставки, джампы; более богатые модели.
3. [Греки: откуда берутся и зачем нужны](lessons/lesson-03-greki.md)
   — грек как частная производная модели; аналитический и численный расчёт; Delta/Gamma/
   Vega/Theta/Rho + второй порядок; PnL-разложение и трейд-офф gamma vs theta; применения:
   хедж, агрегация риска, PnL attribution.
4. [Поверхность волатильности: skew, smile, term structure](lessons/lesson-04-poverhnost-volatilnosti.md)
   — от одной IV к поверхности; котировка по дельте, risk reversal и butterfly; skew/smile и
   их причины; term structure (contango/backwardation, события); безарбитражность и
   параметризация (SVI/SABR); торговля формой поверхности.
5. [Implied vs realized и volatility risk premium](lessons/lesson-05-iv-vs-rv-vrp.md)
   — измерение RV (close-to-close, Parkinson, Garman-Klass, Yang-Zhang); прогноз (EWMA,
   GARCH, HAR-RV); VRP как источник дохода и когда он схлопывается; дельта-хедж на практике,
   gamma-scalping, косты.

## Графики

Количественные графики (payoff, профили греков, улыбка/skew, term structure) лежат в
[`assets/`](assets/) как SVG и воспроизводимо генерируются скриптом:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/make_figures.py    # пересобрать все assets/*.svg
```

## Как проходить

- **Читать рынок:** уроки 1–3 (Блок I).
- **Писать и бэктестить простые стратегии:** уроки 1–4 + практикум 7–8.
- **Запускать капитал:** добавить риск и исполнение (уроки 10–11).

Подробнее о порогах готовности — в [SYLLABUS.md](SYLLABUS.md).
