#!/usr/bin/env python3
"""
Energy Retail Demo - Unstructured Document Generator
Generates PDF and Markdown documents for RAG and Cortex Search
"""

import os
from fpdf import FPDF

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'demo_data', 'unstructured_data')
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f'{OUTPUT_DIR}/energy', exist_ok=True)
os.makedirs(f'{OUTPUT_DIR}/service', exist_ok=True)
os.makedirs(f'{OUTPUT_DIR}/products', exist_ok=True)

class EnergyPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'EPOWER Energie Deutschland GmbH', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Helvetica', '', 11)
        self.multi_cell(0, 6, body)
        self.ln()

print("Generating Unstructured Documents...")

print("1. Creating EPOWER_Green_Power_TCs_2024.pdf...")
pdf = EnergyPDF()
pdf.add_page()
pdf.chapter_title("Allgemeine Geschaeftsbedingungen - Oekostrom 100%")
pdf.chapter_body("""
Gueltig ab 01.01.2024

1. VERTRAGSGEGENSTAND
Diese Allgemeinen Geschaeftsbedingungen (AGB) regeln die Lieferung von Strom aus 100% erneuerbaren Energiequellen durch die EPOWER Energie Deutschland GmbH.

2. STROMHERKUNFT UND ZERTIFIZIERUNG
Der gelieferte Strom stammt ausschliesslich aus:
- Windkraftanlagen (Onshore und Offshore)
- Photovoltaikanlagen
- Wasserkraftwerken
- Biomassekraftwerken

Die Herkunft wird durch Herkunftsnachweise (HKN) gemaess EU-Richtlinie 2018/2001 zertifiziert.

3. PREISGESTALTUNG
3.1 Der Arbeitspreis betraegt aktuell 32,50 ct/kWh (brutto).
3.2 Der monatliche Grundpreis betraegt 12,95 EUR (brutto).
3.3 Preisaenderungen werden mindestens 6 Wochen vor Inkrafttreten mitgeteilt.

4. VERTRAGSLAUFZEIT
4.1 Die Mindestvertragslaufzeit betraegt 12 Monate.
4.2 Der Vertrag verlaengert sich automatisch um 12 Monate, sofern nicht mit einer Frist von 4 Wochen zum Vertragsende gekuendigt wird.

5. KLIMASCHUTZBEITRAG
Mit jedem verbrauchten kWh unterstuetzen Sie den Ausbau erneuerbarer Energien. Pro 1.000 kWh Verbrauch investieren wir 5 EUR in neue Solar- und Windkraftprojekte in Deutschland.

6. KUENDIGUNG
6.1 Die Kuendigung muss schriftlich erfolgen.
6.2 Bei Preiserhoehungen besteht ein Sonderkuendigungsrecht innerhalb von 14 Tagen nach Bekanntgabe.

7. ZAHLUNGSBEDINGUNGEN
7.1 Die Abrechnung erfolgt monatlich oder jaehrlich nach Wahl des Kunden.
7.2 Abschlaege werden am 15. jeden Monats faellig.
7.3 Bei Zahlungsverzug koennen Mahngebuehren von 5 EUR erhoben werden.

8. HAFTUNG
EPOWER haftet fuer Versorgungsunterbrechungen nur bei Vorsatz oder grober Fahrlaessigkeit.

9. DATENSCHUTZ
Ihre Daten werden gemaess DSGVO verarbeitet. Details finden Sie in unserer Datenschutzerklaerung unter www.eon.de/datenschutz.

10. SCHLUSSBESTIMMUNGEN
Es gilt deutsches Recht. Gerichtsstand ist Muenchen.

EPOWER Energie Deutschland GmbH
Arnulfstrasse 203
80634 Muenchen
""")
pdf.output(f'{OUTPUT_DIR}/energy/EPOWER_Green_Power_TCs_2024.pdf')

print("2. Creating Heat_Pump_Efficiency_Guide.pdf...")
pdf = EnergyPDF()
pdf.add_page()
pdf.chapter_title("Waermepumpen Effizienz-Ratgeber")
pdf.chapter_body("""
TECHNISCHE SPEZIFIKATIONEN UND WARTUNGSHINWEISE

1. WAERMEPUMPEN-TYPEN IM UEBERBLICK

1.1 Luft-Wasser-Waermepumpe (EPOWER Waermepumpe Luft-Wasser)
- Heizleistung: 5-16 kW
- COP (Coefficient of Performance): 3,5-4,8
- Vorlauftemperatur: bis 65 Grad Celsius
- Schallpegel: 35-52 dB(A)
- Empfohlen fuer: Neubau und gut gedaemmte Altbauten

1.2 Sole-Wasser-Waermepumpe (EPOWER Waermepumpe Sole-Wasser)
- Heizleistung: 6-20 kW
- COP: 4,2-5,5
- Vorlauftemperatur: bis 70 Grad Celsius
- Schallpegel: 25-40 dB(A)
- Empfohlen fuer: Grundstuecke mit Platz fuer Erdsonden

2. EFFIZIENZ-OPTIMIERUNG

2.1 Jahresarbeitszahl (JAZ)
Die JAZ gibt an, wie effizient Ihre Waermepumpe ueber das Jahr arbeitet:
- JAZ > 4,0: Sehr gut
- JAZ 3,5-4,0: Gut
- JAZ 3,0-3,5: Befriedigend
- JAZ < 3,0: Optimierungsbedarf

2.2 Optimale Vorlauftemperatur
- Fussbodenheizung: 30-35 Grad (optimal)
- Niedertemperatur-Heizkoerper: 40-45 Grad
- Standard-Heizkoerper: 50-55 Grad (reduzierte Effizienz)

3. WARTUNGSINTERVALLE

Jaehrliche Wartung (empfohlen):
- Kaeltemittelkreislauf pruefen
- Verdampfer und Verfluessiger reinigen
- Steuerung und Regelung kontrollieren
- Heizungsanlage hydraulisch abgleichen

Alle 2 Jahre:
- Solekreislauf pruefen (bei Sole-Wasser)
- Kompressor-Funktion testen
- Sicherheitsventile kontrollieren

Alle 5 Jahre:
- Kaeltemittel-Fuellstand pruefen
- Waermetauscher professionell reinigen

4. FEHLERCODES UND BEHEBUNG

E01: Niederdruckfehler - Kaeltemittel pruefen
E02: Hochdruckfehler - Waermetauscher reinigen
E03: Frostschutz aktiv - Heizkreis pruefen
E04: Durchflussfehler - Pumpe und Filter pruefen
E05: Kommunikationsfehler - Steuerung neu starten

5. FOERDERUNG

Aktuelle BAFA-Foerderung (Stand 2024):
- Basisfoerderung: 30% der Investitionskosten
- Effizienzbonus: +5% bei COP > 4,5
- Heizungstausch-Bonus: +10% beim Austausch fossiler Heizung

Maximale Foerdersumme: 70% bzw. 30.000 EUR

6. KONTAKT FUER STOERUNGEN

EPOWER Technischer Service
Hotline: 0800 - 22 33 555 (kostenlos)
Erreichbar: Mo-Fr 7-20 Uhr, Sa 8-16 Uhr
Notfall 24/7: 0800 - 22 33 666
""")
pdf.output(f'{OUTPUT_DIR}/products/Heat_Pump_Efficiency_Guide.pdf')

print("3. Creating Solar_Battery_Quickstart.md...")
solar_content = """# EPOWER Speicher - Quickstart Guide

## Home Storage System Operations

### 1. Systemuebersicht

Ihr EPOWER Speichersystem besteht aus:
- **Batterieeinheit**: LFP (Lithium-Eisenphosphat) Technologie
- **Hybrid-Wechselrichter**: Verbindet Solar, Batterie und Netz
- **Energy Manager**: Intelligente Steuerung und Monitoring

### 2. Inbetriebnahme

#### Schritt 1: App Installation
1. EPOWER Solar App im App Store / Google Play herunterladen
2. Account erstellen oder mit EPOWER Kundenkonto anmelden
3. QR-Code am Wechselrichter scannen

#### Schritt 2: WLAN-Verbindung
1. Wechselrichter mit Heimnetzwerk verbinden
2. Netzwerkname (SSID) und Passwort eingeben
3. Verbindung in der App bestaetigen

#### Schritt 3: Systemmodus waehlen
- **Eigenverbrauch-Modus**: Maximiert Nutzung des eigenen Solarstroms
- **Backup-Modus**: Haelt Reserve fuer Stromausfaelle
- **Zeit-basiert**: Laden/Entladen nach Zeitplan

### 3. Betriebsmodi

| Modus | Beschreibung | Empfohlen fuer |
|-------|--------------|----------------|
| Auto | KI-optimiert basierend auf Verbrauchsmuster | Die meisten Haushalte |
| Eigenverbrauch | 100% Eigennutzung priorisiert | Hoher Tagesverbrauch |
| Netzoptimiert | Nutzt guenstige Netzstromzeiten | Dynamische Tarife |
| Notstrom | Mindestladung 20% fuer Notfaelle | Kritische Geraete |

### 4. Monitoring

In der EPOWER Solar App sehen Sie:
- **Echtzeit-Erzeugung**: Aktuelle Solarleistung in kW
- **Batteriestand**: Ladezustand in Prozent
- **Eigenverbrauchsquote**: Anteil selbst genutzter Energie
- **CO2-Einsparung**: Vermiedene Emissionen

### 5. Wartung

**Monatlich:**
- App-Updates installieren
- Leistungsdaten pruefen

**Jaehrlich (durch EPOWER Techniker):**
- Batteriezustand (SOH) pruefen
- Wechselrichter-Update durchfuehren
- Sicherheitspruefung

### 6. Haeufige Fragen

**Q: Warum laedt die Batterie nicht?**
A: Pruefen Sie, ob genuegend Solarleistung vorhanden ist (>500W) und der Batteriestand nicht bereits bei 100% liegt.

**Q: Kann ich den Speicher auch ohne Solar nutzen?**
A: Ja, im AC-gekoppelten Modus kann der Speicher auch guenstigen Netzstrom speichern.

**Q: Wie lange haelt die Batterie?**
A: Die EPOWER Speicher sind fuer mindestens 6.000 Vollzyklen ausgelegt, was etwa 15-20 Jahren entspricht.

### 7. Notfall-Kontakte

- **Technischer Support**: 0800 - 22 33 557
- **Stoerungshotline 24/7**: 0800 - 22 33 666
- **E-Mail**: solar-support@eon.de

---
*EPOWER Energie Deutschland GmbH - Version 2.1 - Stand: Januar 2024*
"""
with open(f'{OUTPUT_DIR}/products/Solar_Battery_Quickstart.md', 'w', encoding='utf-8') as f:
    f.write(solar_content)

print("4. Creating Invoice_Explanation_FAQ.pdf...")
pdf = EnergyPDF()
pdf.add_page()
pdf.chapter_title("Ihre Energierechnung verstehen - FAQ")
pdf.chapter_body("""
HAEUFIGE FRAGEN ZUR STROMRECHNUNG

1. AUFBAU DER RECHNUNG

Ihre EPOWER Energierechnung besteht aus folgenden Bereichen:

1.1 Kopfbereich
- Ihre Kundennummer und Vertragskontonummer
- Abrechnungszeitraum
- Zaehlernummer und Zaehlerstand

1.2 Verbrauchsuebersicht
- Verbrauch in kWh fuer den Abrechnungszeitraum
- Vergleich zum Vorjahr
- Durchschnittlicher Monatsverbrauch

1.3 Kostenaufstellung
- Arbeitspreis (ct/kWh x Verbrauch)
- Grundpreis (monatliche Pauschale)
- Steuern und Abgaben

2. PREISBESTANDTEILE IM DETAIL

Der Strompreis setzt sich zusammen aus:
- Energiebeschaffung und Vertrieb: ca. 35%
- Netzentgelte: ca. 25%
- EEG-Umlage: ca. 15%
- Stromsteuer: ca. 6%
- Mehrwertsteuer: 19%
- Sonstige Umlagen und Abgaben: ca. 5%

3. HAEUFIGE FRAGEN

F: Warum ist mein Verbrauch hoeher als letztes Jahr?
A: Moegliche Gruende sind:
- Neue elektrische Geraete (z.B. Waermepumpe, E-Auto)
- Mehr Personen im Haushalt
- Veraendertes Nutzungsverhalten
- Kaelterer/waermerer Winter (bei Heizstrom)

F: Was bedeutet "Abschlag"?
A: Der Abschlag ist eine monatliche Vorauszahlung, die sich nach Ihrem geschaetzten Jahresverbrauch richtet. Bei der Jahresabrechnung wird der tatsaechliche Verbrauch mit den gezahlten Abschlaegen verrechnet.

F: Wie kann ich meinen Verbrauch reduzieren?
A: Tipps zum Energiesparen:
- LED-Beleuchtung nutzen
- Standby-Geraete ausschalten
- Energieeffiziente Geraete (A+++) kaufen
- Heizung optimieren
- Smart Home Steuerung nutzen

F: Was ist die Messstellengebuehr?
A: Die Messstellengebuehr (ca. 20 EUR/Jahr bei analogen Zaehlern, bis 100 EUR bei Smart Metern) deckt die Kosten fuer Installation, Betrieb und Ablesung Ihres Zaehlers.

F: Kann ich die Rechnung in Raten zahlen?
A: Ja, kontaktieren Sie unseren Kundenservice fuer eine individuelle Ratenzahlungsvereinbarung. Bei Zahlungsschwierigkeiten hilft auch die Schuldnerberatung.

4. KONTAKT BEI FRAGEN ZUR RECHNUNG

EPOWER Kundenservice
Telefon: 0800 - 22 33 559
E-Mail: kundenservice@eon.de
Online: www.eon.de/meine-rechnung

Oeffnungszeiten:
Mo-Fr: 7:00 - 20:00 Uhr
Sa: 8:00 - 14:00 Uhr
""")
pdf.output(f'{OUTPUT_DIR}/service/Invoice_Explanation_FAQ.pdf')

print("5. Creating Smart_Meter_Installation_Guide.pdf...")
pdf = EnergyPDF()
pdf.add_page()
pdf.chapter_title("Smart Meter - Installations- und Bedienungsanleitung")
pdf.chapter_body("""
IHRE MODERNE MESSEINRICHTUNG

1. WAS IST EIN SMART METER?

Ein Smart Meter ist ein intelligentes Messsystem, das:
- Ihren Stromverbrauch digital erfasst
- Daten verschluesselt an den Netzbetreiber uebertraegt
- Verbrauchsanalysen in Echtzeit ermoeglicht
- Grundlage fuer dynamische Tarife bildet

2. GESETZLICHER HINTERGRUND

Gemaess Messstellenbetriebsgesetz (MsbG) muessen Smart Meter bei:
- Verbrauch > 6.000 kWh/Jahr installiert werden
- Erzeugungsanlagen > 7 kW
- Waermepumpen und Nachtspeicherheizungen
- Neubauten und Renovierungen

3. INSTALLATION

3.1 Vor der Installation
- Sie erhalten 3 Monate vor Installation eine Ankuendigung
- Der Termin wird 2 Wochen vorher bestaetigt
- Stellen Sie Zugang zum Zaehlerkasten sicher
- Installation dauert ca. 1-2 Stunden

3.2 Waehrend der Installation
- Kurze Stromunterbrechung (ca. 15 Min.)
- Alte Zaehler werden dokumentiert und entfernt
- Smart Meter Gateway wird konfiguriert
- Funktionstest wird durchgefuehrt

4. BEDIENUNG UND DISPLAY

Das Display zeigt:
- Aktueller Zaehlerstand (kWh)
- Aktuelle Leistung (W)
- Historische Verbräuche
- Tarifzeiten (HT/NT)

Tastenfunktionen:
- INFO: Zwischen Anzeigen wechseln
- ENTER: Auswahl bestaetigen
- PIN: Fuer erweiterte Einstellungen

5. ONLINE-PORTAL

Im EPOWER Kundenportal sehen Sie:
- 15-Minuten-genaue Verbrauchswerte
- Tages-, Wochen-, Monatsanalysen
- Vergleich mit Durchschnittshaushalten
- CO2-Fussabdruck

6. DATENSCHUTZ

Ihre Daten sind sicher:
- BSI-zertifiziertes Smart Meter Gateway
- Ende-zu-Ende-Verschluesselung
- Keine Weitergabe an Dritte
- Speicherung gemaess DSGVO

7. HAEUFIGE STOERUNGEN

Problem: Display zeigt nichts
Loesung: Stromversorgung pruefen, ggf. Sicherung

Problem: Keine Datenuebertragung
Loesung: Internetverbindung pruefen, Gateway neu starten

Problem: Unrealistische Werte
Loesung: Zaehlerstand manuell ablesen und melden

8. KONTAKT

Smart Meter Hotline: 0800 - 22 33 556
Stoerung melden: stoerung.eon.de
E-Mail: smartmeter@eon.de
""")
pdf.output(f'{OUTPUT_DIR}/products/Smart_Meter_Installation_Guide.pdf')

print("6. Creating Vendor_Management_Policy.pdf...")
pdf = EnergyPDF()
pdf.add_page()
pdf.chapter_title("Richtlinie fuer Lieferanten- und Partnermnagement")
pdf.chapter_body("""
EPOWER INTERNE RICHTLINIE - VERTRAULICH

1. GELTUNGSBEREICH

Diese Richtlinie gilt fuer alle Beschaffungsvorgaenge der EPOWER Energie Deutschland GmbH, insbesondere fuer:
- Installationspartner (Solar, Waermepumpe, Wallbox)
- Wartungsdienstleister
- IT-Dienstleister
- Marketingagenturen
- Material- und Komponentenlieferanten

2. BESCHAFFUNGSGRUNDSAETZE

2.1 Ausschreibungspflicht
- Ab 10.000 EUR: Mind. 3 Angebote einholen
- Ab 50.000 EUR: Formelle Ausschreibung erforderlich
- Ab 100.000 EUR: EU-weite Ausschreibung pruefen

2.2 Lieferantenauswahl
Bewertungskriterien:
- Preis-Leistungs-Verhaeltnis (40%)
- Qualitaet und Referenzen (25%)
- Nachhaltigkeit und Umweltstandards (20%)
- Zuverlaessigkeit und Lieferfaehigkeit (15%)

3. VERTRAGSGESTALTUNG

3.1 Pflichtklauseln
- Compliance und Anti-Korruption
- Datenschutz (DSGVO)
- Nachhaltigkeitsstandards
- Kuendigungsrechte
- Haftung und Gewaehrleistung

3.2 Zahlungsbedingungen
- Standard: 30 Tage netto
- Bei Skonto: 2% bei Zahlung innerhalb 14 Tagen
- Vorauszahlungen nur in begruendeten Ausnahmefaellen

4. LIEFERANTENBEWERTUNG

Jaehrliche Bewertung nach:
- Termintreue
- Qualitaet der Leistung
- Reklamationsquote
- Kommunikation und Erreichbarkeit
- Preisgestaltung

Bewertungsskala:
A - Bevorzugter Partner
B - Zugelassener Partner
C - Unter Beobachtung
D - Gesperrt

5. NACHHALTIGKEITSANFORDERUNGEN

Lieferanten muessen nachweisen:
- CO2-Reduktionsziele
- Einhaltung von Arbeitsstandards
- Umweltzertifizierung (ISO 14001)
- Kreislaufwirtschaft-Konzepte

6. COMPLIANCE

Nulltoleranz bei:
- Korruption und Bestechung
- Kartellrechtsverstoessen
- Kinderarbeit
- Menschenrechtsverletzungen

Verstaesse fuehren zur sofortigen Vertragsbeendigung.

7. GENEHMIGUNGSEBENEN

- Bis 5.000 EUR: Abteilungsleiter
- Bis 25.000 EUR: Bereichsleiter
- Bis 100.000 EUR: Geschaeftsfuehrung
- Ueber 100.000 EUR: Vorstand

Kontakt: einkauf@eon.de
""")
pdf.output(f'{OUTPUT_DIR}/energy/Vendor_Management_Policy.pdf')

print("7. Creating Energy_Efficiency_Tips.pdf...")
pdf = EnergyPDF()
pdf.add_page()
pdf.chapter_title("Energiespar-Tipps fuer Ihren Haushalt")
pdf.chapter_body("""
SO SENKEN SIE IHRE ENERGIEKOSTEN

1. STROM SPAREN IM HAUSHALT

1.1 Kueche
- Wasserkocher nur mit benoetigter Menge fuellen: Spart 30 EUR/Jahr
- Topfdeckel beim Kochen nutzen: Spart 15 EUR/Jahr
- Kuehlschrank auf 7 Grad einstellen: Spart 10 EUR/Jahr
- Gefrierschrank regelmaessig abtauen: Spart 20 EUR/Jahr

1.2 Wohnzimmer
- LED statt Gluehbirne: Spart 80% Strom
- Standby vermeiden (Steckerleiste): Spart 50 EUR/Jahr
- Fernseher: Kleinere Groesse = weniger Verbrauch
- Laptop statt Desktop-PC: Spart 70% Energie

1.3 Bad
- Warmwasser begrenzen: Duschen statt Baden
- Sparduschkopf installieren: Spart 100 EUR/Jahr
- Waschmaschine voll beladen und 30 Grad waschen

2. HEIZEN UND KUEHLEN

2.1 Optimale Raumtemperaturen
- Wohnzimmer: 20-21 Grad
- Schlafzimmer: 16-18 Grad
- Kueche: 18-19 Grad
- Bad: 22-24 Grad

Jedes Grad weniger spart etwa 6% Heizkosten!

2.2 Richtiges Lueften
- Stosslueeften: 3x taeglich 5-10 Minuten
- Fenster nicht gekippt lassen
- Heizung beim Lueften herunterdrehen

3. SMART HOME NUTZEN

Mit EPOWER Smart Home:
- Intelligente Thermostate: Spart bis 30% Heizkosten
- Automatische Lichtsteuerung: Nie wieder Licht vergessen
- Verbrauchsmonitoring: Energiefresser identifizieren
- Zeitsteuerung: Geraete nur bei Bedarf an

4. GROSSVERBRAUCHER OPTIMIEREN

4.1 Waermepumpe
- Nachtabsenkung aktivieren
- Fussbodenheizung bevorzugen
- Regelmaessige Wartung

4.2 Elektroauto
- Bevorzugt zu Hause laden (guenstiger)
- Solarstrom nutzen
- Ladezeiten optimieren (nachts)

4.3 Solaranlage
- Eigenverbrauch maximieren
- Grossverbraucher mittags betreiben
- Batteriespeicher nutzen

5. FOERDERPROGRAMME

Nutzen Sie Foerderungen fuer:
- Energieberatung (BAFA): 80% Zuschuss
- Heizungstausch: bis 70% Foerderung
- Daemmung: bis 20% Zuschuss
- E-Auto: Umweltbonus

Beratung: www.eon.de/energieberatung

6. VERBRAUCHSRECHNER

Typische Verbräuche pro Jahr:
- 1-Person-Haushalt: 1.500-2.000 kWh
- 2-Person-Haushalt: 2.500-3.500 kWh
- 4-Person-Haushalt: 4.000-5.000 kWh
- Mit Waermepumpe: +3.000-5.000 kWh
- Mit E-Auto: +2.000-3.000 kWh

Ihr persoenlicher Verbrauch: www.eon.de/verbrauchsrechner
""")
pdf.output(f'{OUTPUT_DIR}/service/Energy_Efficiency_Tips.pdf')

print("8. Creating Waermepumpe_Foerderung_2024.md...")
foerder_content = """# Waermepumpen-Foerderung 2024

## Staatliche Foerderprogramme im Ueberblick

### 1. BAFA-Foerderung (Bundesfoerderung fuer effiziente Gebaeude)

#### Basisfoerderung
- **30%** der foerderfaehigen Kosten
- Maximale Investitionskosten: 30.000 EUR (Einfamilienhaus)
- **Maximale Foerderung: 9.000 EUR**

#### Effizienz-Bonus
- **+5%** bei Waermepumpen mit natuerlichem Kaeltemittel
- **+5%** bei Nutzung von Erd- oder Grundwasser
- Kombinierbar mit Basisfoerderung

#### Heizungstausch-Bonus
- **+10%** beim Austausch einer fossilen Heizung
- Gilt fuer: Oel, Gas, Nachtspeicher, Kohle
- Heizung muss mind. 20 Jahre alt sein

#### Einkommensbonus
- **+30%** fuer Haushalte mit Einkommen unter 40.000 EUR/Jahr

### 2. KfW-Kredit (Ergaenzungskredit)

| Merkmal | Details |
|---------|---------|
| Kreditsumme | bis 120.000 EUR |
| Zinssatz | ab 0,01% (einkommensabhaengig) |
| Tilgungszuschuss | bis 20% bei niedrigem Einkommen |
| Laufzeit | 4-30 Jahre |

### 3. Rechenbeispiel

**Beispiel: Luft-Wasser-Waermepumpe im Einfamilienhaus**

| Position | Betrag |
|----------|--------|
| Anschaffungskosten | 35.000 EUR |
| Installation | 8.000 EUR |
| **Gesamtkosten** | **43.000 EUR** |
| Foerderfaehige Kosten (max.) | 30.000 EUR |
| Basisfoerderung (30%) | -9.000 EUR |
| Heizungstausch-Bonus (10%) | -3.000 EUR |
| Effizienz-Bonus (5%) | -1.500 EUR |
| **Gesamtfoerderung** | **-13.500 EUR** |
| **Eigenanteil** | **29.500 EUR** |

### 4. Voraussetzungen

- Gebaeude aelter als 5 Jahre
- Energieeffizienz-Experte einbinden
- Hydraulischer Abgleich erforderlich
- Online-Antrag VOR Beauftragung stellen

### 5. Antragsverfahren

1. **Schritt 1**: Energieberater konsultieren
2. **Schritt 2**: Angebot von EPOWER einholen
3. **Schritt 3**: Online-Antrag bei BAFA stellen
4. **Schritt 4**: Auf Zuwendungsbescheid warten
5. **Schritt 5**: Installation beauftragen
6. **Schritt 6**: Verwendungsnachweis einreichen

### 6. EPOWER Foerderservice

Wir unterstuetzen Sie bei:
- Foerdermittelberatung
- Antragsstellung
- Energieberater-Vermittlung
- Komplettpaket mit Foerdergarantie

**Kontakt**: foerderung@eon.de | 0800 - 22 33 558

---
*Stand: Januar 2024 - Aenderungen vorbehalten*
"""
with open(f'{OUTPUT_DIR}/energy/Waermepumpe_Foerderung_2024.md', 'w', encoding='utf-8') as f:
    f.write(foerder_content)

print("9. Creating E_Mobility_Tarife.md...")
emobility_content = """# EPOWER E-Mobility - Tarifuebersicht

## Wallbox und Ladetarife fuer Elektrofahrzeuge

### 1. Wallbox-Produkte

#### EPOWER Wallbox 11kW
- **Preis**: 899 EUR (inkl. Installation)
- **Leistung**: 11 kW (3-phasig)
- **Ladedauer**: 4-6 Stunden (40-60 kWh Batterie)
- **Features**: App-Steuerung, Ladelog, RFID

#### EPOWER Wallbox 22kW
- **Preis**: 1.499 EUR (inkl. Installation)
- **Leistung**: 22 kW (3-phasig)
- **Ladedauer**: 2-3 Stunden (40-60 kWh Batterie)
- **Features**: Wie 11kW + dynamisches Lastmanagement

### 2. EPOWER Drive Tarif

| Komponente | Preis |
|------------|-------|
| Arbeitspreis (Home) | 29,90 ct/kWh |
| Arbeitspreis (Oeffentlich AC) | 45,00 ct/kWh |
| Arbeitspreis (Oeffentlich DC) | 55,00 ct/kWh |
| Grundpreis | 4,99 EUR/Monat |

#### Vorteile
- Eine Karte fuer Zuhause und unterwegs
- 150.000+ Ladepunkte in Europa
- App mit Ladestatiosfinder
- Monatliche Sammelrechnung

### 3. Kombination mit Solar

**EPOWER Solar + Wallbox Bundle**
- Solar-Ueberschussladen automatisch
- Nur selbst erzeugten Strom nutzen
- Kosten: ca. 5 ct/kWh mit eigener Solaranlage

### 4. THG-Quote

**Verdienen Sie mit Ihrem E-Auto!**
- Jaehrliche Praemie: ca. 300-400 EUR
- Einfache Anmeldung ueber EPOWER
- Auszahlung innerhalb 4 Wochen

### 5. Foerderung

- KfW 440: 900 EUR Zuschuss fuer private Wallbox (ausgelaufen)
- Kommunale Foerderung: Je nach Bundesland
- Arbeitgeber-Zuschuss: Steuerfrei moeglich

### 6. Kontakt

- **Beratung**: 0800 - 22 33 560
- **Stoerung**: 0800 - 22 33 666
- **Web**: www.eon.de/elektromobilitaet

---
*EPOWER Drive - Einfach elektrisch fahren*
"""
with open(f'{OUTPUT_DIR}/products/E_Mobility_Tarife.md', 'w', encoding='utf-8') as f:
    f.write(emobility_content)

print("10. Creating Customer_Service_Handbook.pdf...")
pdf = EnergyPDF()
pdf.add_page()
pdf.chapter_title("EPOWER Kundenservice Handbuch - Intern")
pdf.chapter_body("""
RICHTLINIEN FUER KUNDENSERVICE-MITARBEITER

1. SERVICE-STANDARDS

1.1 Erreichbarkeit
- Telefon: Abnahme innerhalb 30 Sekunden
- E-Mail: Antwort innerhalb 24 Stunden
- Chat: Erste Reaktion innerhalb 60 Sekunden
- Social Media: Antwort innerhalb 4 Stunden

1.2 Gespraechsfuehrung
- Freundliche Begruessung mit Namen
- Aktives Zuhoeren
- Loesungsorientierte Kommunikation
- Zusammenfassung am Ende des Gespraechs
- Klare naechste Schritte kommunizieren

2. ESKALATIONSSTUFEN

Stufe 1 - Erstloesung (Kundenberater)
- Standardanfragen
- Rechnungsfragen
- Tarifauskuenfte
- Abschlagsaenderungen

Stufe 2 - Fachabteilung
- Technische Probleme
- Komplexe Reklamationen
- Vertragsanpassungen

Stufe 3 - Teamleiter
- Ungeloeste Beschwerden
- Kulanzentscheidungen > 100 EUR
- Eskalierte Kunden

Stufe 4 - Abteilungsleiter
- Rechtliche Themen
- Medienanfragen
- VIP-Kunden

3. KULANZREGELUNGEN

3.1 Gutschriften
- Bis 50 EUR: Kundenberater eigenstaendig
- Bis 200 EUR: Teamleiter-Freigabe
- Ueber 200 EUR: Abteilungsleiter

3.2 Typische Kulanzgruende
- Verspaetete Bearbeitung
- Fehlerhafte Abrechnungen
- Technische Probleme durch EPOWER verursacht
- Langjaeahrige Kundentreue

4. DATENSCHUTZ

4.1 Identifikationspflicht
Vor Auskuenften immer verifizieren:
- Kundennummer ODER
- Vertragskontonummer PLUS
- Name und Geburtsdatum ODER
- Letzte Abschlagshoehe

4.2 Verbotene Auskuenfte an Dritte
- Verbräuche
- Zahlungsverhalten
- Kontodaten
- Persoenliche Daten

5. HAEUFIGE THEMEN

5.1 Smart Meter
- Installation: 3 Monate Vorlauf
- Kosten: Max. 100 EUR/Jahr
- Datenschutz: BSI-zertifiziert

5.2 Waermepumpe
- Stoerung: Technikereinsatz innerhalb 48h
- Wartung: Jaehrlich empfohlen
- Foerderung: An BAFA verweisen

5.3 Solar
- Einspeiseverguetung: Aktuell 8,2 ct/kWh
- Monitoring: App-Support anbieten
- Speicher: Garantie 10 Jahre

6. QUALITAETSSICHERUNG

- Gespraeche werden aufgezeichnet
- Monatliche Coaching-Gespraeche
- Mystery Calls zur Qualitaetskontrolle
- Kundenzufriedenheitsbefragung nach Kontakt

Kontakt Teamleitung: teamleitung.service@eon.de
""")
pdf.output(f'{OUTPUT_DIR}/service/Customer_Service_Handbook.pdf')

print("\n✅ All unstructured documents generated!")
print(f"Output directory: {OUTPUT_DIR}")
for root, dirs, files in os.walk(OUTPUT_DIR):
    level = root.replace(OUTPUT_DIR, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 2 * (level + 1)
    for file in files:
        print(f'{subindent}{file}')
