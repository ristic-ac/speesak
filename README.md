# speesak

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
- Docker i Docker Compose (za pokretanje u kontejneru)

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
        - `XXK.xls`, gde je XX oznaka smera, za kompletne spiskove studenata, to jest, spiskove iz kartice "Polaganje ispita" u okviru nastavničkog servisa
4. U folderu `xlsx/` će se nalaziti konvertovani spiskovi studenata u formatu .xlsx, koji su potrebni za dalju obradu. Neophodno je kreirati direktorijum i smestiti datoteku:
    - `PRIJAVE.xlsx` - spisak studenata koji su se prijavili za kolokvijum na formi, sa kolonama:
        - Ime
        - Prezime
        - Smer
        - Broj upisa
        - Godina upisa
5. Za dodatne termine neophodno je u datoteci `classrooms.csv` u okviru `additional-classrooms/` direktorijuma dodati učionice u kojima će se testovi održati sa kolonama:
    - Ucionica
    - Termin
    Postoji primer datoteke `classrooms.csv` u okviru `additional-classrooms/` direktorijuma. Softver automatski zna da se u Mašinskom institutu testovi održavaju u učionicama od 32, a u NTP-u u učionicama od 16 mesta.
6. Potrebno je da imate instaliran Docker i Docker Compose. Pokrenite sledeću komandu iz root direktorijuma projekta:

    ```bash
    docker compose up --build
    ```

    Ova komanda će izgraditi i pokrenuti kontejner sa svim potrebnim zavisnostima.

7. Program `main.py` se pokreće automatski unutar Docker kontejnera.
8. Rezultati obrade (spiskovi studenata) se nalaze u direktorijumu `schedules/`:
    - `regular_groups.xlsx` – raspored studenata po postojećim grupama
    - `additional_groups.xlsx` – raspored studenata po novim grupama

## Eventualne greške

Ukoliko se pri pokretanju `convert.sh` skripte javi greška:

`Warning: failed to read path from javaldx:`

Neophodno je instalirati `libreoffice-java-common` i `default-jre` pakete komandom:

`sudo apt-get install libreoffice-java-common default-jre`

Ukoliko naravno, koristite Debian-based distribuciju.
