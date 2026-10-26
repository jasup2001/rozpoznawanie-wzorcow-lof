"""Próba LOF wykorzystana w prezentacji etapu 1.

Wymagania: Python 3.10+ i NumPy (w prezentacji: Python 3.12.14, NumPy 2.3.5).
Instalacja: python -m pip install numpy==2.3.5
Uruchomienie: python eksperyment_lof.py
Opcjonalnie: python eksperyment_lof.py --out wyniki_lof

Kod odtwarza wyłącznie małą próbę z prezentacji. Pełne badanie semestralne
z wieloma ziarnami, konfiguracjami i metodą odniesienia pozostaje planem.
Definicje: Breunig i in. (2000), sekcja 4.
https://doi.org/10.1145/342009.335388
"""

from pathlib import Path
import argparse
import csv
import json
import platform
import time

import numpy as np


def oblicz_lof(punkty, k):
    """LOF dla punktów obecnych w zbiorze, z uwzględnieniem remisów.

    Nie jest to wywołanie gotowego modelu scikit-learn. Poszczególne kroki
    implementują definicję LOF bezpośrednio za pomocą operacji NumPy.
    Punkty nie mogą się powtarzać (zerowa odległość może dać nieskończone lrd).
    Implementacja przechowuje pełną macierz odległości, czyli O(n²) pamięci.
    """
    X = np.asarray(punkty, dtype=float)
    if X.ndim != 2 or not np.isfinite(X).all():
        raise ValueError('Oczekiwano skończonej macierzy punktów n × d.')
    if not isinstance(k, int) or not 1 <= k < len(X):
        raise ValueError('k musi być liczbą całkowitą od 1 do n-1.')
    if len(np.unique(X, axis=0)) != len(X):
        raise ValueError('Ten przykład nie obsługuje identycznych punktów.')

    # D[i,j] to odległość euklidesowa między i a j.
    D = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(axis=2))
    # Punkt nie może być swoim sąsiadem.
    np.fill_diagonal(D, np.inf)

    # Indeksowanie w Pythonie zaczyna się od 0.
    k_distance = np.partition(D, k - 1, axis=1)[:, k - 1]
    # Włączamy wszystkich sąsiadów na granicy k-distance (także remisy).
    sasiedzi = [np.flatnonzero(D[i] <= k_distance[i]) for i in range(len(X))]

    # reach-dist(i,j) = max(k-distance(j), D[i,j]).
    srednia_reach = np.array([
        np.maximum(D[i, js], k_distance[js]).mean()
        for i, js in enumerate(sasiedzi)
    ])
    lrd = 1.0 / srednia_reach
    srednia_lrd_sasiadow = np.array([lrd[js].mean() for js in sasiedzi])
    wynik = srednia_lrd_sasiadow / lrd
    return {
        'k_distance': k_distance,
        'liczba_sasiadow': np.array([len(js) for js in sasiedzi]),
        'srednia_reach': srednia_reach,
        'lrd': lrd,
        'srednia_lrd_sasiadow': srednia_lrd_sasiadow,
        'lof': wynik,
        'sasiedzi': sasiedzi,
    }


def wykonaj_probe():
    # Przykład ze slajdów 6-7: A=0, B=1, C=3, P=10, k=2.
    male_punkty = np.array([[0.], [1.], [3.], [10.]])
    maly = oblicz_lof(male_punkty, 2)
    np.testing.assert_allclose(maly['lrd'], [0.4, 1/3, 0.4, 0.125])
    np.testing.assert_allclose(maly['lof'], [11/12, 6/5, 11/12, 44/15])

    # Ta sama kolejność losowania i parametry co w prezentacji.
    rng = np.random.default_rng(42)
    normalne = rng.normal(0, 0.55, (400, 2))
    anomalie = rng.normal([4, 0], 0.08, (30, 2))
    X = np.vstack([normalne, anomalie])
    etykiety = np.r_[np.zeros(400, dtype=int), np.ones(30, dtype=int)]

    szczegoly, podsumowanie = {}, []
    start = time.perf_counter()
    for k in (10, 40):
        wynik = oblicz_lof(X, k)
        # Większy LOF oznacza wyższą pozycję w rankingu anomalii.
        kolejnosc = np.argsort(-wynik['lof'])
        top30 = kolejnosc[:30]
        szczegoly[str(k)] = wynik
        podsumowanie.append({
            'k': k,
            'mediana_normalnych': float(np.median(wynik['lof'][:400])),
            'mediana_anomalii': float(np.median(wynik['lof'][400:])),
            'wykryte_anomalie_top30': int(etykiety[top30].sum()),
            'recall_top30': float(etykiety[top30].sum() / 30),
        })
    czas = time.perf_counter() - start

    def serializuj(w):
        return {key: ([a.tolist() for a in val] if key == 'sasiedzi' else val.tolist())
                for key, val in w.items()}

    return {
        'python': platform.python_version(), 'numpy': np.__version__,
        'seed': 42, 'budzet_wskazan': 30, 'czas_sekundy': czas,
        'punkty': X.tolist(), 'etykiety': etykiety.tolist(),
        'maly_przyklad': serializuj(maly),
        'szczegoly': {k: serializuj(v) for k, v in szczegoly.items()},
        'podsumowanie': podsumowanie,
    }


def zapisz_wyniki(dane, folder):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / 'wyniki_szczegolowe.json').write_text(
        json.dumps(dane, ensure_ascii=False, indent=2), encoding='utf-8')
    # Szczegóły dla każdego punktu, przydatne do sprawdzenia arkusza Excel.
    pola = ['k_distance', 'liczba_sasiadow', 'srednia_reach',
            'lrd', 'srednia_lrd_sasiadow', 'lof']
    with (folder / 'punkty_i_obliczenia.csv').open('w', newline='', encoding='utf-8-sig') as plik:
        writer = csv.writer(plik, delimiter=';')
        writer.writerow(['id', 'x', 'y', 'anomalia'] +
                        [f'{p}_k{k}' for k in (10, 40) for p in pola])
        for i, (x, y) in enumerate(dane['punkty']):
            writer.writerow([i + 1, x, y, dane['etykiety'][i]] +
                            [dane['szczegoly'][str(k)][p][i] for k in (10, 40) for p in pola])
    with (folder / 'podsumowanie.csv').open('w', newline='', encoding='utf-8-sig') as plik:
        writer = csv.DictWriter(plik, fieldnames=list(dane['podsumowanie'][0]), delimiter=';')
        writer.writeheader()
        writer.writerows(dane['podsumowanie'])


def main():
    parser = argparse.ArgumentParser(description='Próba LOF z prezentacji etapu 1')
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parent / 'wyniki_lof')
    args = parser.parse_args()
    dane = wykonaj_probe()
    zapisz_wyniki(dane, args.out)
    print(f"Python {dane['python']}, NumPy {dane['numpy']}")
    print('Mały przykład, LOF(A,B,C,P):', dane['maly_przyklad']['lof'])
    for r in dane['podsumowanie']:
        print(f"k={r['k']}: mediana normalnych={r['mediana_normalnych']:.6f}, "
              f"mediana anomalii={r['mediana_anomalii']:.6f}, "
              f"wykryte={r['wykryte_anomalie_top30']}/30, recall@30={r['recall_top30']:.1%}")
    print(f"Czas próby: {dane['czas_sekundy']:.4f} s (zależy od komputera)")
    print('Zapisano wyniki w:', args.out.resolve())


if __name__ == '__main__':
    main()
