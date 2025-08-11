# speesak

## TODO

- Objediniti sa spiskovima iz kartice "Polaganje ispita" u okviru nastavničkog servisa, kako bi se dobio spisak gde su informacije o plaćanju i načinu slušanja.
- Saznati koje vrednosti polja označavaju da student nema pravo na polaganje preko kolokvijuma, kako bi se isključili iz spiska.

## Opis programa

Ovaj program je namenjen za upravljanje spiskovima studenata na Fakultetu tehničkih nauka.

Program omogućava:

- Prebacivanje spiskova studenata iz formata .xls u .xlsx, uz pomoć `convert.sh` skripte
- Proveru konzistentnosti spiskova studenata
- Raspoređivanje studenata u već postojeće grupe, radi izrade rasporeda za testove
- Kreiranje novih grupa studenata, od onih koji nisu raspoređeni u već postojeće grupe
- Generisanje rasporeda za testove, uz mogućnost izbora datuma i vremena, kao i učionice u kojima će se testovi održati

## Neophodni alati

- Python 3
  - pandas
  - openpyxl
- LibreOffice

## Uputstvo za korišćenje

Neophodno je:

1. Kreirati anketu za studente, tako da sadrži polja:
    - Ime
    - Prezime
    - Smer (dropdown lista sa smerovima propisanim od strane fakulteta, RA, PSI, IN)
    - Broj upisa (Broj, 1, 101, 240)
    - Godina upisa (Broj, 2019, 2020, 2021, ...)

2. Kreirati direktorijum `xls/` u kome će se nalaziti originalni spiskovi studenata
3. Smestiti originalne spiskove studenata u direktorijum `xls/`, dobijene od strane studentske službe (nastavničkog servisa)
    - Imena spiskova je neophodno preimenovati u format:
        - `XX.xls`, gde je XX oznaka smera propisana od strane fakulteta (RA, PSI, IN, ...) za spiskove po grupama
        - `XXK.xls`, gde je XX oznaka smera, za kompletne spiskove studenata, to jest spiskove iz kartice "Polaganje ispita" u okviru nastavničkog servisa
4. Pokrenuti program `convert.sh` kako bi se svi spiskovi prebacili u format .xlsx
5. U folderu `xlsx/` će se nalaziti konvertovani spiskovi studenata u formatu .xlsx, koji su potrebni za dalju obradu. Neophodno je i smestiti datoteku:
    - `PRIJAVE.xlsx` - spisak studenata koji su se prijavili za kolokvijum na formi, sa kolonama:
        - Ime
        - Prezime
        - Smer
        - Broj upisa
        - Godina upisa
6. Za dodatne termine neophodno je u datoteci `classrooms.csv` u okviru `additional-classrooms/` direktorijuma dodati učionice u kojima će se testovi održati sa kolonama:
    - Ucionica
    - Termin
7. Kreirati Python virtuelno okruženje i instalirati potrebne biblioteke:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

7. Pokrenuti program `main.py`
8. Spiskovi studenata se generišu u direktorijumu `schedules/`, i to:
    - `regular_groups.xlsx` - raspored studenata po već postojećim grupama
    - `additional_groups.xlsx` - raspored studenata po novim grupama

## Eventualne greške

Ukoliko se pri pokretanju `convert.sh` skripte javi greška:

`Warning: failed to read path from javaldx:`

Neophodno je instalirati `libreoffice-java-common` i `default-jre` pakete komandom:

`sudo apt-get install libreoffice-java-common default-jre`

Ukoliko naravno, koristite Debian-based distribuciju.
