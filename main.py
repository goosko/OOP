"""
Repülőjegy Foglalási Rendszer

Fő osztályok
    Járat (absztrakt osztály): Definiálja a járat alapvető attribútumait (járatszám, célállomás, jegyár).
    BelföldiJarat: Belföldi járatokra vonatkozó osztály, amelyek olcsóbbak és rövidebbek.
    NemzetkoziJarat: Nemzetközi járatokra vonatkozó osztály, magasabb jegyárakkal.
    LégiTársaság: Tartalmazza a járatokat és saját attribútumot, mint például a légitársaság neve.
    JegyFoglalás: A járatok foglalásához szükséges osztály, amely egy utazásra szóló jegy foglalását tárolja.

Funkciók
    Jegy foglalása: A járatokra jegyet lehet foglalni, és visszaadja a foglalás árát.
    Foglalás lemondása: A felhasználó lemondhatja a meglévő foglalást.
    Foglalások listázása: Az összes aktuális foglalás listázása.

Adatvalidáció
    Ellenőrzi, hogy a járat elérhető-e foglalásra, és hogy a foglalás időpontja érvényes-e.
    Biztosítja, hogy csak létező foglalásokat lehessen lemondani.

Felhasználói interfész
    Egyszerű felhasználói interfész, amely lehetővé teszi a következő műveleteket:
        Jegy foglalása
        Foglalás lemondása
        Foglalások listázása

Előkészítés
A rendszer indulásakor egy légitársaság, 3 járat és 6 foglalás előre be van töltve a rendszerbe, így a felhasználó azonnal használatba veheti a rendszert

"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import random
import string


class JaratStatusz:
    AKTIV = "AKTÍV"
    INAKTIV = "INAKTÍV"


class Jarat(ABC):

    def __init__(self, jaratszam: str, indulo_repter: str, celallomas: str,
                 jegyar: float, legitarsasag: str, datum: datetime):
        self.jaratszam = jaratszam
        self.indulo_repter = indulo_repter
        self.celallomas = celallomas
        self.jegyar = jegyar
        self.legitarsasag = legitarsasag
        self.datum = datum
        self.statusz = JaratStatusz.AKTIV if datum > datetime.now() else JaratStatusz.INAKTIV

    @abstractmethod
    def get_jarat_tipus(self) -> str:
        pass

    def __str__(self):
        status_str = "[AKTÍV]" if self.statusz == JaratStatusz.AKTIV else "[INAKTÍV]"
        return (f"{status_str} {self.jaratszam} | {self.indulo_repter} -> {self.celallomas}\n"
                f"   Típus: {self.get_jarat_tipus()} | Dátum: {self.datum.strftime('%Y-%m-%d')} | "
                f"Ár: {int(self.jegyar):,} Ft".replace(',', ' '))


class BelfoldiJarat(Jarat):

    def __init__(self, jaratszam: str, indulo: str, cel: str, ar: float,
                 legitarsasag: str, datum: datetime):
        super().__init__(jaratszam, indulo, cel, ar * 0.8, legitarsasag, datum)
        self.repulesi_ido = 2  # hours

    def get_jarat_tipus(self) -> str:
        return "Belföldi"


class NemzetkoziJarat(Jarat):

    def __init__(self, jaratszam: str, indulo: str, cel: str, ar: float,
                 legitarsasag: str, datum: datetime):
        super().__init__(jaratszam, indulo, cel, ar * 1.3, legitarsasag, datum)
        self.repulesi_ido = 8  # hours

    def get_jarat_tipus(self) -> str:
        return "Nemzetközi"


class Legitarsasag:

    def __init__(self, nev: str):
        self.nev = nev
        self.jaratok: List[Jarat] = []

    def jarat_hozzaadasa(self, jarat: Jarat):
        if any(j.jaratszam == jarat.jaratszam for j in self.jaratok):
            raise ValueError(f"A {jarat.jaratszam} járatszám már létezik!")
        self.jaratok.append(jarat)

    def get_jarat_by_jaratszam(self, jaratszam: str) -> Optional[Jarat]:
        for jarat in self.jaratok:
            if jarat.jaratszam == jaratszam:
                return jarat
        return None


class JegyFoglalas:

    def __init__(self, jarat: Jarat, utas_nev: str):
        self.foglalas_id = self._generate_foglalas_id()
        self.jaratszam = jarat.jaratszam
        self.indulo = jarat.indulo_repter
        self.celallomas = jarat.celallomas
        self.datum = jarat.datum
        self.utas_nev = utas_nev
        self.ar = jarat.jegyar
        self.statusz = "Aktív"

    def _generate_foglalas_id(self) -> str:
        betuk = ''.join(random.choices(string.ascii_uppercase, k=2))
        szamok = ''.join(random.choices(string.digits, k=3))
        return betuk + szamok

    def __str__(self):
        return (f"Foglalás: {self.foglalas_id} | Utas: {self.utas_nev}\n"
                f"   Járat: {self.jaratszam} ({self.indulo} -> {self.celallomas})\n"
                f"   Dátum: {self.datum.strftime('%Y-%m-%d')} | Ár: {int(self.ar):,} Ft | Státusz: {self.statusz}".replace(
            ',', ' '))


class RepuloJegyFoglalasiRendszer:

    def __init__(self):
        self.legitarsasag: Optional[Legitarsasag] = None
        self.foglalasok: List[JegyFoglalas] = []
        self.existing_foglalas_ids = set()

    def _init_test_adatok(self):
        self.legitarsasag = Legitarsasag("Wizz Air Hungary")

        # Múltbéli tesztjáratok
        self.legitarsasag.jarat_hozzaadasa(
            BelfoldiJarat("WIZ001", "Budapest", "Debrecen", 15000,
                          "Wizz Air", datetime(2023, 1, 1))
        )

        # Tesztjáratok
        self.legitarsasag.jarat_hozzaadasa(
            BelfoldiJarat("WIZ102", "Budapest", "Szeged", 20000,
                          "Wizz Air", datetime(2025, 6, 10))
        )
        self.legitarsasag.jarat_hozzaadasa(
            NemzetkoziJarat("WIZ201", "Budapest", "London", 50000,
                            "Wizz Air", datetime(2025, 6, 15))
        )

        # Tesztadatok
        jaratok = self.legitarsasag.jaratok
        self.foglalasok.append(JegyFoglalas(jaratok[1], "Nagy János"))
        self.foglalasok.append(JegyFoglalas(jaratok[1], "Kovács Béla"))
        self.foglalasok.append(JegyFoglalas(jaratok[2], "Szabó Éva"))
        self.foglalasok.append(JegyFoglalas(jaratok[2], "Kiss Zoltán"))
        self.foglalasok.append(JegyFoglalas(jaratok[2], "Tóth Mária"))
        self.foglalasok.append(JegyFoglalas(jaratok[2], "Horváth Péter"))

        # Meglévő foglalások nyomonkövetése
        for foglalas in self.foglalasok:
            self.existing_foglalas_ids.add(foglalas.foglalas_id)

    def jegy_foglalas(self):
        if not self.legitarsasag or not self.legitarsasag.jaratok:
            print("Nincs elérhető járat a foglaláshoz!")
            return

        aktiv_jaratok = [j for j in self.legitarsasag.jaratok if j.statusz == JaratStatusz.AKTIV]
        if not aktiv_jaratok:
            print("Nincs aktív járat a foglaláshoz!")
            return

        print("\nElérhető járatok:")
        for i, jarat in enumerate(aktiv_jaratok, 1):
            print(f"{i}. {jarat}")

        try:
            valasztas = int(input("\nVálassz járatot (szám): "))
            if valasztas < 1 or valasztas > len(aktiv_jaratok):
                print("Érvénytelen választás!")
                return

            kivalasztott_jarat = aktiv_jaratok[valasztas - 1]
            print(
                f"\nJárat kiválasztva: {kivalasztott_jarat.jaratszam} - {kivalasztott_jarat.indulo_repter} -> {kivalasztott_jarat.celallomas} ({int(kivalasztott_jarat.jegyar):,} Ft)".replace(
                    ',', ' '))

            # Dátum ellenőrzése
            if kivalasztott_jarat.datum < datetime.now():
                print("A járat dátuma már elmúlt, nem foglalható!")
                return

            print(f"Foglalás dátumának ellenőrzése... OK ({kivalasztott_jarat.datum.strftime('%Y-%m-%d')})")

            utas_nev = input("\nAdd meg az utas nevét: ").strip()
            if len(utas_nev) < 2:
                print("Az utas neve túl rövid!")
                return

            # Foglalás létrehozása
            foglalas = JegyFoglalas(kivalasztott_jarat, utas_nev)

            # Duplikációkat ellenőrizzük
            while foglalas.foglalas_id in self.existing_foglalas_ids:
                foglalas = JegyFoglalas(kivalasztott_jarat, utas_nev)

            self.existing_foglalas_ids.add(foglalas.foglalas_id)
            self.foglalasok.append(foglalas)

            print(f"\nFoglalás sikeresen létrehozva!")
            print(f"Foglalási azonosító: {foglalas.foglalas_id}")
            print(f"Fizetendő összeg: {int(foglalas.ar):,} Ft".replace(',', ' '))

        except ValueError:
            print("Érvénytelen bemenet!")
        except Exception as e:
            print(f"Hiba történt: {e}")

    def foglalas_lemondasa(self):
        """Cancel a booking"""
        if not self.foglalasok:
            print("Nincs aktív foglalás a rendszerben!")
            return

        foglalas_id = input("Add meg a lemondani kívánt foglalás azonosítóját: ").strip().upper()

        for i, foglalas in enumerate(self.foglalasok):
            if foglalas.foglalas_id == foglalas_id and foglalas.statusz == "Aktív":
                print(f"\nFoglalás részletei:")
                print(foglalas)

                megerosites = input("\nBiztosan lemondod ezt a foglalást? (i/n): ").strip().lower()
                if megerosites == 'i':
                    foglalas.statusz = "Lemondva"
                    visszaterites = foglalas.ar * 0.7  # 70% refund
                    print(f"\nFoglalás sikeresen lemondva!")
                    print(f"Visszatérítés összege: {int(visszaterites):,} Ft".replace(',', ' '))
                    return
                else:
                    print("Lemondás megszakítva.")
                    return

        print("Nem található aktív foglalás a megadott azonosítóval!")

    def foglalasok_listazasa(self):
        if not self.foglalasok:
            print("Nincs foglalás a rendszerben!")
            return

        aktiv_foglalasok = [f for f in self.foglalasok if f.statusz == "Aktív"]
        lemondott_foglalasok = [f for f in self.foglalasok if f.statusz == "Lemondva"]

        print(f"\nFoglalások listája ({len(self.foglalasok)} db):")
        print("=" * 50)

        print(f"\nAktív foglalások ({len(aktiv_foglalasok)} db):")
        for foglalas in aktiv_foglalasok:
            print(f"\n{foglalas}")

        if lemondott_foglalasok:
            print(f"\nLemondott foglalások ({len(lemondott_foglalasok)} db):")
            for foglalas in lemondott_foglalasok:
                print(f"\n{foglalas}")

    def jaratok_listazasa(self):
        if not self.legitarsasag or not self.legitarsasag.jaratok:
            print("Nincs járat a rendszerben!")
            return

        print(f"\nJáratok listája ({len(self.legitarsasag.jaratok)} db):")
        print("=" * 50)

        for i, jarat in enumerate(self.legitarsasag.jaratok, 1):
            print(f"{i}. {jarat}")

    def uj_jarat_hozzaadasa(self):
        if not self.legitarsasag:
            print("Nincs légitársaság beállítva!")
            return

        print("\nÚj járat hozzáadása:")
        try:
            jaratszam = input("Járatszám: ").strip().upper()
            indulo = input("Induló repülőtér: ").strip()
            cel = input("Célállomás: ").strip()

            try:
                ar = float(input("Alapjegyár (Ft): "))
                if ar <= 0:
                    print("Az árnak pozitívnak kell lennie!")
                    return
            except ValueError:
                print("Érvénytelen ár formátum!")
                return

            legitarsasag = input("Légitársaság: ").strip()
            datum_str = input("Dátum (ÉÉÉÉ-HH-NN): ").strip()

            try:
                datum = datetime.strptime(datum_str, "%Y-%m-%d")
            except ValueError:
                print("Érvénytelen dátum formátum! Használd az ÉÉÉÉ-HH-NN formátumot.")
                return

            tipus = input("Típus (1 - Belföldi, 2 - Nemzetközi): ").strip()

            if tipus == "1":
                uj_jarat = BelfoldiJarat(jaratszam, indulo, cel, ar, legitarsasag, datum)
            elif tipus == "2":
                uj_jarat = NemzetkoziJarat(jaratszam, indulo, cel, ar, legitarsasag, datum)
            else:
                print("Érvénytelen járattípus!")
                return

            self.legitarsasag.jarat_hozzaadasa(uj_jarat)
            print(f"\nJárat sikeresen hozzáadva: {uj_jarat}")

        except ValueError as e:
            print(f"Hiba: {e}")
        except Exception as e:
            print(f"Váratlan hiba történt: {e}")

    def rendszer_allapota(self):
        print("\nRendszer állapota:")
        print("=" * 50)

        if self.legitarsasag:
            print(f"Légitársaság: {self.legitarsasag.nev}")
            print(f"Járatok száma: {len(self.legitarsasag.jaratok)}")

            aktiv_jaratok = [j for j in self.legitarsasag.jaratok if j.statusz == JaratStatusz.AKTIV]
            print(f"Aktív járatok: {len(aktiv_jaratok)}")

            belfoldiek = [j for j in self.legitarsasag.jaratok if isinstance(j, BelfoldiJarat)]
            print(f"Belföldi járatok: {len(belfoldiek)}")

            nemzetkoziek = [j for j in self.legitarsasag.jaratok if isinstance(j, NemzetkoziJarat)]
            print(f"Nemzetközi járatok: {len(nemzetkoziek)}")
        else:
            print("Nincs légitársaság beállítva!")

        print(f"\nFoglalások száma: {len(self.foglalasok)}")
        aktiv_foglalasok = [f for f in self.foglalasok if f.statusz == "Aktív"]
        print(f"Aktív foglalások: {len(aktiv_foglalasok)}")

        lemondott_foglalasok = [f for f in self.foglalasok if f.statusz == "Lemondva"]
        print(f"Lemondott foglalások: {len(lemondott_foglalasok)}")

    def futtatas(self):
        """Futtassuk a programot"""
        print("Repülőjegy Foglalási Rendszer - Inicializálás...")
        self._init_test_adatok()
        print("Tesztadatok betöltve!")

        while True:
            print("\n" + "=" * 50)
            print("Repülőjegy Foglalási Rendszer")
            print("=" * 50)
            print("1. Jegy foglalása")
            print("2. Foglalás lemondása")
            print("3. Foglalások listázása")
            print("4. Új járat hozzáadása")
            print("5. Járatok listázása")
            print("6. Rendszer állapota")
            print("7. Kilépés")

            valasztas = input("\nVálassz egy műveletet (1-7): ").strip()

            if valasztas == "1":
                self.jegy_foglalas()
            elif valasztas == "2":
                self.foglalas_lemondasa()
            elif valasztas == "3":
                self.foglalasok_listazasa()
            elif valasztas == "4":
                self.uj_jarat_hozzaadasa()
            elif valasztas == "5":
                self.jaratok_listazasa()
            elif valasztas == "6":
                self.rendszer_allapota()
            elif valasztas == "7":
                print("\nKöszönjük, hogy használta a Repülőjegy Foglalási Rendszert!")
                break
            else:
                print("Érvénytelen választás! Kérlek válassz 1-7 között.")


# Futtatás
if __name__ == "__main__":
    rendszer = RepuloJegyFoglalasiRendszer()
    rendszer.futtatas()