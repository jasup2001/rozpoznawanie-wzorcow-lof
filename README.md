# Rozpoznawanie wzorców

Projekt semestralny, rok akademicki 2026/2027.

**Temat: Lokalne anomalie i maskowanie odstających obiektów w LOF.**

Repozytorium służy do wspólnej pracy nad projektem i udostępniania materiałów prowadzącemu.

## Aktualny zakres

Etap 1: opis publikacji, podstawy metody, mały przykład obliczeniowy, plan badania oraz próba wykonalności. Pełne badanie z wieloma ziarnami i metodą odniesienia pozostaje do wykonania. Zakres adaptacji należy uzgodnić z prowadzącym.

## Materiały etapu 1

- [Prezentacja PDF](materialy/etap-1/LOF_etap_1_prezentacja.pdf)
- [Excel z obliczeniami](materialy/etap-1/LOF_obliczenia.xlsx)
- [Kod próby](eksperyment_lof.py)
- [Podsumowanie wyników CSV](wyniki/etap-1/podsumowanie.csv)
- [Dane i obliczenia dla każdego punktu](wyniki/etap-1/punkty_i_obliczenia.csv)
- [Pełne wyniki i sąsiedztwa JSON](wyniki/etap-1/wyniki_szczegolowe.json)

## Uruchomienie

Wymagania: Python 3.12 i NumPy. Wyniki z prezentacji uzyskano w Pythonie 3.12.14 z NumPy 2.3.5. Nie potrzeba GPU ani pobierania danych.

W PowerShell, w katalogu repozytorium:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe eksperyment_lof.py --out wyniki_lokalne
```

W systemach Linux i macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python eksperyment_lof.py --out wyniki_lokalne
```

Kod implementuje definicję LOF za pomocą NumPy. Nie korzysta z gotowego modelu scikit-learn. Uwzględnia remisy na granicy sąsiedztwa i wyklucza punkt własny. Przechowuje pełną macierz odległości, dlatego jest przeznaczony do małych zbiorów. Identyczne punkty nie są obsługiwane w tej wersji.

## Wyniki próby

Generator `numpy.random.default_rng(42)`: 400 punktów normalnych oraz 30 anomalii w zwartej grupie. Te same dane dla obu wartości k.

| k | Mediana LOF normalnych | Mediana LOF anomalii | Wykryte w top 30 | Recall@30 |
|---|---:|---:|---:|---:|
| 10 | 1.029439 | 1.119902 | 7 / 30 | 23.3% |
| 40 | 1.025712 | 1.993553 | 25 / 30 | 83.3% |

To pojedyncza próba wykonalności, nie końcowy wynik badania. Czas wykonania zależy od komputera. W JSON zapisano czas konkretnego uruchomienia.

W Excelu przykład czterech punktów przelicza się formułami od odległości do LOF. Dla próby 430 punktów sąsiedztwa i średnie pochodzą z Pythona, a dalsze wyniki i podsumowanie obliczają formuły. Zmiana współrzędnych w tej części wymaga ponownego wykonania kodu i odświeżenia wyników.

## Wspólna praca

1. Osoba współpracująca musi otrzymać zaproszenie w **Settings → Collaborators** i je zaakceptować, żeby zapisywać zmiany. Publiczna widoczność zapewnia prowadzącemu dostęp do odczytu.
2. Każde zadanie rozwijamy w osobnej gałęzi, np. `etap2-generator`.
3. Zmiany przesyłamy przez pull request, żeby druga osoba mogła je przejrzeć.
4. W opisach commitów i pull requestów zapisujemy wkład autorów, decyzje badawcze i zmiany protokołu.
5. Surowe wyniki zachowujemy razem z konfiguracją i ziarnami losowania. Wyniki z nowych etapów trafiają do osobnych podkatalogów.

## Kolejne kroki

- Uzgodnienie adaptacji scenariusza z publikacji i eksperymentu własnego.
- Generator scenariusza z grupami o różnych gęstościach.
- Metoda odniesienia: odległość do k-tego sąsiada.
- Badanie liczebności grupy anomalii i parametru k na wielu ziarnach.
- Ocena AP i recall@20 według zamrożonego protokołu.
- Raport końcowy oraz instrukcja odtworzenia wyników.

## Źródła

Breunig M. M., Kriegel H.-P., Ng R. T., Sander J. (2000). *LOF: Identifying Density-Based Local Outliers*. ACM SIGMOD, s. 93–104.

- [DOI](https://doi.org/10.1145/342009.335388)
- [Pełny tekst publikacji](https://cse.hkust.edu.hk/~raywong/comp5331/References/LOFIdentifyingDensityBasedLocalOutliers.pdf)

## Wykorzystanie AI

OpenAI Codex wspierał porównanie tematów, przygotowanie prezentacji, kodu próby, arkusza obliczeń i dokumentacji. Autorzy projektu powinni samodzielnie sprawdzić rozwiązania, rozumieć obliczenia i uzasadniać decyzje badawcze. Przed oddaniem należy uzupełnić informację o AI według uczelnianego formularza 2A.
