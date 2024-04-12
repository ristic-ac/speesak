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

## Uputstvo za korišćenje

Neophodno je:
1. Kreirati direktorijum `xls/` u kome će se nalaziti originalni spiskovi studenata
2. Smestiti originalne spiskove studenata u direktorijum `xls/`, dobijene od strane studentske službe (nastavničkog servisa)
    - Imena spiskova je neophodno preimenovati u format:
        - `XX.xls`, gde je XX oznaka smera propisana od strane fakulteta (RA, PSI, IN, ...) za spiskove po grupama
        - `XXK.xls`, gde je XX oznaka smera, za kompletne spiskove studenata
3. Pokrenuti program `convert.sh` kako bi se svi spiskovi prebacili u format .xlsx
4. Za dodatne termine neophodno je u datoteci `classrooms.csv` u okviru `additional-classrooms/` direktorijuma dodati učionice u kojima će se testovi održati sa kolonama:
    - Ucionica
    - Termin
5. Pokrenuti program `main.py`
6. Spiskovi studenata se generišu u direktorijumu `schedules/`, i to:
    - `regular_groups.xlsx` - raspored studenata po već postojećim grupama
    - `additional_groups.xlsx` - raspored studenata po novim grupama    

## Eventualne greške

Ukoliko se pri pokretanju `convert.sh` skripte javi greška:

`Warning: failed to read path from javaldx:`

Neophodno je instalirati `libreoffice-java-common` i `default-jre` pakete komandom:

`sudo apt-get install libreoffice-java-common default-jre`

Ukoliko naravno, koristite Debian-based distribuciju.