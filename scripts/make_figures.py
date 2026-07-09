"""Генератор графиков для курса crypto-vol-course.

Запуск:
    .venv/bin/python scripts/make_figures.py

Все SVG складываются в assets/. Параметры подобраны под крипту (высокая σ, r=0).
"""
from __future__ import annotations

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import norm

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(ASSETS, exist_ok=True)

plt.rcParams.update({
    "figure.figsize": (8, 5),
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 11,
    "axes.titlesize": 13,
    "svg.fonttype": "none",  # текст остаётся текстом (Кириллица через системный шрифт)
})


# ---------- Black-Scholes (r=0 по умолчанию, крипто) ----------
def _d1(S, K, T, sigma, r=0.0):
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

def _d2(S, K, T, sigma, r=0.0):
    return _d1(S, K, T, sigma, r) - sigma * np.sqrt(T)

def call_price(S, K, T, sigma, r=0.0):
    d1, d2 = _d1(S, K, T, sigma, r), _d2(S, K, T, sigma, r)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

def delta_call(S, K, T, sigma, r=0.0):
    return norm.cdf(_d1(S, K, T, sigma, r))

def delta_put(S, K, T, sigma, r=0.0):
    return norm.cdf(_d1(S, K, T, sigma, r)) - 1.0

def gamma(S, K, T, sigma, r=0.0):
    return norm.pdf(_d1(S, K, T, sigma, r)) / (S * sigma * np.sqrt(T))

def vega(S, K, T, sigma, r=0.0):
    # на 1 вол-пункт (÷100)
    return S * norm.pdf(_d1(S, K, T, sigma, r)) * np.sqrt(T) / 100.0

def theta_call(S, K, T, sigma, r=0.0):
    # за день (÷365)
    d1, d2 = _d1(S, K, T, sigma, r), _d2(S, K, T, sigma, r)
    t = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)
    return t / 365.0


def save(fig, name):
    path = os.path.join(ASSETS, name)
    fig.tight_layout()
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print("wrote", os.path.relpath(path))


# ---------- Урок 1: payoff колла и пута ----------
def fig_payoff_call_put():
    K, prem = 100, 6
    S = np.linspace(60, 140, 400)
    fig, ax = plt.subplots()
    ax.plot(S, np.maximum(S - K, 0) - prem, label="Long call (профит)")
    ax.plot(S, np.maximum(K - S, 0) - prem, label="Long put (профит)")
    ax.axhline(0, color="k", lw=0.8)
    ax.axvline(K, color="gray", ls="--", lw=0.8)
    ax.annotate("страйк K", (K, ax.get_ylim()[0]), xytext=(K + 2, -30), fontsize=9)
    ax.set_title("Payoff опционов на экспирации (за вычетом премии)")
    ax.set_xlabel("Цена актива на экспирации")
    ax.set_ylabel("Профит")
    ax.legend()
    save(fig, "payoff_call_put.svg")


# ---------- Урок 1: straddle (LP ≈ short straddle) ----------
def fig_straddle():
    K, prem = 100, 12  # премия за колл+пут
    S = np.linspace(60, 140, 400)
    long_str = np.maximum(S - K, 0) + np.maximum(K - S, 0) - prem
    fig, ax = plt.subplots()
    ax.plot(S, long_str, label="Long straddle (покупка воли)")
    ax.plot(S, -long_str, label="Short straddle ≈ LP в AMM")
    ax.axhline(0, color="k", lw=0.8)
    ax.axvline(K, color="gray", ls="--", lw=0.8)
    ax.fill_between(S, -long_str, 0, where=(-long_str > 0), alpha=0.1, color="C1")
    ax.set_title("Straddle: short straddle повторяет профиль LP (short gamma)")
    ax.set_xlabel("Цена актива на экспирации")
    ax.set_ylabel("Профит")
    ax.legend()
    save(fig, "straddle_payoff.svg")


# ---------- Урок 2: цена BS vs внутренняя стоимость (временная стоимость) ----------
def fig_price_vs_payoff():
    K, T, sigma = 100, 0.5, 0.6
    S = np.linspace(60, 140, 400)
    intrinsic = np.maximum(S - K, 0)
    price = call_price(S, K, T, sigma)
    fig, ax = plt.subplots()
    ax.plot(S, intrinsic, "k--", label="Внутренняя стоимость max(S−K,0)")
    ax.plot(S, price, "C0", label="Цена колла по BS (T=0.5, σ=60%)")
    ax.fill_between(S, intrinsic, price, alpha=0.15, color="C0", label="Временная стоимость")
    ax.axvline(K, color="gray", ls="--", lw=0.8)
    ax.set_title("Цена опциона = внутренняя + временная стоимость (выпуклость)")
    ax.set_xlabel("Цена актива S")
    ax.set_ylabel("Стоимость опциона")
    ax.legend()
    save(fig, "price_vs_payoff.svg")


# ---------- Урок 3: профили греков ----------
def fig_greeks():
    K, T, sigma = 100, 0.25, 0.6
    S = np.linspace(60, 140, 400)
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    (a, b), (c, d) = axes
    a.plot(S, delta_call(S, K, T, sigma), label="call")
    a.plot(S, delta_put(S, K, T, sigma), label="put")
    a.set_title("Delta"); a.axvline(K, color="gray", ls="--", lw=0.8); a.legend()
    b.plot(S, gamma(S, K, T, sigma), "C2")
    b.set_title("Gamma (макс. у ATM)"); b.axvline(K, color="gray", ls="--", lw=0.8)
    c.plot(S, vega(S, K, T, sigma), "C3")
    c.set_title("Vega (на 1 вол-пункт)"); c.axvline(K, color="gray", ls="--", lw=0.8)
    d.plot(S, theta_call(S, K, T, sigma), "C4")
    d.set_title("Theta (за день, call)"); d.axvline(K, color="gray", ls="--", lw=0.8)
    for ax in (a, b, c, d):
        ax.set_xlabel("Цена актива S")
    fig.suptitle("Профили греков против цены актива (K=100, T=0.25, σ=60%)", fontsize=13)
    save(fig, "greeks_profiles.svg")


# ---------- Урок 3: gamma-theta PnL дельта-хеджированной позиции ----------
def fig_pnl_gamma_theta():
    g, th = 0.02, 8.0   # условные gamma и |theta| за период
    dS = np.linspace(-40, 40, 400)
    gamma_pnl = 0.5 * g * dS ** 2
    theta_pnl = -th * np.ones_like(dS)
    net = gamma_pnl + theta_pnl
    fig, ax = plt.subplots()
    ax.plot(dS, gamma_pnl, "C2", label="Gamma-PnL = ½·Γ·dS²")
    ax.plot(dS, theta_pnl, "C4", label="Theta-PnL = Θ·dt (расход)")
    ax.plot(dS, net, "C0", lw=2, label="Итог (long gamma)")
    ax.axhline(0, color="k", lw=0.8)
    be = np.sqrt(2 * th / g)
    ax.axvline(be, color="gray", ls=":", lw=0.9)
    ax.axvline(-be, color="gray", ls=":", lw=0.9)
    ax.annotate("порог: RV = IV", (be, 0), xytext=(be + 1, 5), fontsize=9)
    ax.set_title("Дельта-хедж: gamma против theta (в плюсе, если RV > IV)")
    ax.set_xlabel("Движение актива за период, dS")
    ax.set_ylabel("PnL")
    ax.legend()
    save(fig, "pnl_gamma_theta.svg")


# ---------- Урок 4: улыбка и skew ----------
def fig_smile_skew():
    F = 100
    K = np.linspace(70, 130, 400)
    x = np.log(K / F)  # log-moneyness
    atm, curv = 0.60, 1.2
    smile = atm + curv * x ** 2
    put_skew = atm + curv * x ** 2 - 0.6 * x     # низкие страйки дороже
    call_skew = atm + curv * x ** 2 + 0.6 * x    # высокие страйки дороже
    fig, ax = plt.subplots()
    ax.plot(K, smile * 100, label="Симметричная улыбка")
    ax.plot(K, put_skew * 100, label="Put-skew (risk-off)")
    ax.plot(K, call_skew * 100, label="Call-skew (бычий режим)")
    ax.axvline(F, color="gray", ls="--", lw=0.8)
    ax.annotate("ATM (форвард)", (F, ax.get_ylim()[0]), xytext=(F + 1, 62), fontsize=9)
    ax.set_title("Срез по страйку: улыбка и skew")
    ax.set_xlabel("Страйк K")
    ax.set_ylabel("Implied volatility, %")
    ax.legend()
    save(fig, "vol_smile_skew.svg")


# ---------- Урок 4: term structure ----------
def fig_term_structure():
    T = np.linspace(0.02, 1.0, 400)
    contango = 0.55 + 0.12 * (1 - np.exp(-2 * T))
    backwardation = 0.85 - 0.25 * (1 - np.exp(-2 * T))
    event = contango + 0.18 * np.exp(-((T - 0.12) ** 2) / (2 * 0.02 ** 2))  # бугор под событие
    fig, ax = plt.subplots()
    ax.plot(T, contango * 100, label="Contango (спокойный режим)")
    ax.plot(T, backwardation * 100, label="Backwardation (стресс)")
    ax.plot(T, event * 100, label="Событийный бугор (разлок/релиз)")
    ax.set_title("Срез по сроку: term structure ATM-волатильности")
    ax.set_xlabel("Срок до экспирации, годы")
    ax.set_ylabel("ATM implied volatility, %")
    ax.legend()
    save(fig, "term_structure.svg")


# ---------- Урок 5: IV против RV во времени (VRP) ----------
def fig_iv_vs_rv():
    rng = np.random.default_rng(7)
    n = 252
    rv = np.zeros(n)
    rv[0] = 0.55
    sh = rng.normal(0, 1, n)
    for i in range(1, n):
        rv[i] = 0.50 + 0.82 * (rv[i - 1] - 0.50) + 0.06 * sh[i]
    # два стрессовых всплеска, где RV выстреливает выше IV
    for c, w, a in [(90, 6, 0.55), (180, 5, 0.40)]:
        rv += a * np.exp(-((np.arange(n) - c) ** 2) / (2 * w ** 2))
    rv = np.clip(rv, 0.2, None)
    # IV: сглаженный прогноз RV + премия
    iv = np.copy(rv)
    for i in range(1, n):
        iv[i] = 0.90 * iv[i - 1] + 0.10 * rv[i]
    iv = iv + 0.08
    t = np.arange(n)
    fig, ax = plt.subplots()
    ax.plot(t, iv * 100, "C0", label="Implied vol (IV)")
    ax.plot(t, rv * 100, "C3", label="Realized vol (RV)")
    ax.fill_between(t, iv * 100, rv * 100, where=(iv >= rv), alpha=0.15, color="C0",
                    label="VRP > 0 (продавец воли в плюсе)")
    ax.fill_between(t, iv * 100, rv * 100, where=(iv < rv), alpha=0.25, color="C3",
                    label="VRP < 0 (стресс, short vol в минусе)")
    ax.set_title("Volatility risk premium: IV обычно выше RV, но схлопывается в стресс")
    ax.set_xlabel("Дни")
    ax.set_ylabel("Волатильность, %")
    ax.legend(fontsize=9)
    save(fig, "iv_vs_rv.svg")


# ---------- Урок 5: scatter IV против последующей RV ----------
def fig_vrp_scatter():
    rng = np.random.default_rng(3)
    iv = rng.uniform(0.4, 1.1, 200)
    rv = iv - 0.09 + rng.normal(0, 0.10, 200)   # в среднем RV ниже IV на премию
    rv = np.clip(rv, 0.1, None)
    fig, ax = plt.subplots()
    ax.scatter(iv * 100, rv * 100, s=18, alpha=0.6, color="C4")
    lim = [30, 120]
    ax.plot(lim, lim, "k--", lw=1, label="RV = IV (нулевой VRP)")
    ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_title("Точки под диагональю: реализованная вола чаще ниже вменённой")
    ax.set_xlabel("Implied vol на входе, %")
    ax.set_ylabel("Последующая realized vol, %")
    ax.legend()
    save(fig, "vrp_scatter.svg")


# ---------- Урок 6: форвардная/базисная кривая ----------
def fig_basis_curve():
    S = 100.0
    T = np.linspace(0, 1.0, 400)
    contango = S * np.exp(0.09 * T)       # положительный carry
    backwardation = S * np.exp(-0.07 * T) # отрицательный (стресс/дефицит предложения)
    fig, ax = plt.subplots()
    ax.axhline(S, color="k", lw=1, label="Спот S")
    ax.plot(T, contango, "C0", label="Contango: F > S (обычный режим)")
    ax.plot(T, backwardation, "C3", label="Backwardation: F < S (стресс)")
    ax.set_title("Форвардная кривая: базис = F − S по срокам")
    ax.set_xlabel("Срок до экспирации, годы")
    ax.set_ylabel("Цена фьючерса F")
    ax.legend()
    save(fig, "basis_curve.svg")


# ---------- Урок 6: cash-and-carry — сходимость базиса ----------
def fig_cash_and_carry():
    rng = np.random.default_rng(11)
    n = 200
    t = np.linspace(0, 1, n)              # доля прожитого срока
    spot = 100 + np.cumsum(rng.normal(0, 1.1, n))  # случайный путь спота
    basis0 = 6.0
    fut = spot + basis0 * (1 - t)          # базис линейно сходится к нулю к экспирации
    fig, ax = plt.subplots()
    ax.plot(t, spot, "C1", label="Спот")
    ax.plot(t, fut, "C0", label="Фьючерс (продан)")
    ax.fill_between(t, spot, fut, alpha=0.15, color="C0", label="Базис → 0")
    ax.axhline(spot[0] + basis0, color="gray", ls=":", lw=0.9)
    ax.annotate("зафиксированная доходность = базис", (0.05, spot[0] + basis0 + 0.5), fontsize=9)
    ax.set_title("Cash-and-carry: long спот + short фьючерс фиксирует базис")
    ax.set_xlabel("Доля прожитого срока (0 → экспирация)")
    ax.set_ylabel("Цена")
    ax.legend()
    save(fig, "cash_and_carry.svg")


def main():
    fig_payoff_call_put()
    fig_straddle()
    fig_price_vs_payoff()
    fig_greeks()
    fig_pnl_gamma_theta()
    fig_smile_skew()
    fig_term_structure()
    fig_iv_vs_rv()
    fig_vrp_scatter()
    fig_basis_curve()
    fig_cash_and_carry()
    print("done ->", ASSETS)


if __name__ == "__main__":
    main()
