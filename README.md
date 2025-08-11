# **speesak**

## 📌 Opis programa

**speesak** je alat namenjen za upravljanje spiskovima studenata na Fakultetu tehničkih nauka.  
Omogućava jednostavno rukovanje podacima o studentima, raspoređivanje u grupe i generisanje rasporeda testova.

### 🔍 Pregled funkcionalnosti

- ✅ Konverzija spiskova studenata iz **.xls** u **.xlsx** format (uz pomoć skripte `convert.sh`)
- ✅ Provera konzistentnosti spiskova studenata
- ✅ Raspoređivanje studenata u postojeće grupe radi izrade rasporeda testova
- ✅ Kreiranje novih grupa za studente koji nisu raspoređeni
- ✅ Generisanje rasporeda testova sa mogućnošću izbora datuma, vremena i učionica

---

## 🛠️ Neophodni alati

- **Python 3**
  - `pandas`
  - `openpyxl`
- **LibreOffice**
- **Docker** i **Docker Compose**

---

## 📖 Uputstvo za korišćenje

### 1️⃣ Priprema ankete

Kreirajte anketu za studente koja sadrži sledeća polja:

- **Ime**
- **Prezime**
- **Smer** *(dropdown lista sa smerovima: RA, PSI, IN, ... propisanim od strane fakulteta)*
- **Broj upisa** *(npr. 1, 101, 240)*
- **Godina upisa** *(npr. 2019, 2020, 2021...)*

---

### 2️⃣ Priprema direktorijuma i spiskova

1. Kreirajte direktorijum `xls/` i u njega smestite originalne spiskove studenata dobijene od studentske službe.
2. Preimenujte fajlove prema formatu:
   - `XX.xls` → spiskovi po grupama  
   - `XXK.xls` → kompletni spiskovi studenata (sa kartice **"Polaganje ispita"** u nastavničkom servisu)  
     > *XX je oznaka smera: RA, PSI, IN...*

---

### 3️⃣ Konverzija fajlova

Konvertovani fajlovi će se nalaziti u direktorijumu `xlsx/`.  
U njemu treba da bude i fajl **`PRIJAVE.xlsx`** sa prijavljenim studentima, u formatu:

- **Ime**
- **Prezime**
- **Smer**
- **Broj upisa**
- **Godina upisa**

---

### 4️⃣ Podešavanje dodatnih termina

U direktorijumu `additional-classrooms/` nalazi se fajl `classrooms.csv` sa učionicama i terminima:  
Kolone:

- **Ucionica**
- **Termin**  

Primer fajla je već dat u projektu.  
> Softver automatski prepoznaje kapacitet:
>
> - Mašinski institut → učionice sa 32 mesta  
> - NTP → učionice sa 16 mesta

---

### 5️⃣ Pokretanje preko Dockera

Neophodno je imati instalirane **Docker** i **Docker Compose**.  
Iz root direktorijuma projekta pokrenite:

```bash
docker compose up --build
```

Ovo će izgraditi i pokrenuti kontejner sa svim potrebnim zavisnostima.  
Program `main.py` će se automatski pokrenuti unutar kontejnera.

---

### 6️⃣ Rezultati obrade

Nakon izvršavanja, rezultati se nalaze u direktorijumu **`schedules/`**:

- **`regular_groups.xlsx`** – raspored studenata po postojećim grupama
- **`additional_groups.xlsx`** – raspored studenata po novim grupama

---

### ⚠️ Rešavanje mogućih grešaka

**Greška:**

```text
Warning: failed to read path from javaldx:
```

**Rešenje:**  

Instalirajte sledeće pakete:

```bash
sudo apt-get install libreoffice-java-common default-jre
```

(važi za Debian-based distribucije)
