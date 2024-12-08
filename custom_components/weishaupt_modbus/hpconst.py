"""Heatpump constants."""

import copy

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)

from .const import DEVICES, FORMATS, TYPES
from .items import ModbusItem, StatusItem, WebItem

reverse_device_list: dict[str, str] = {
    "dev_system": "SYS",
    "dev_waermepumpe": "WP",
    "dev_warmwasser": "WW",
    "dev_heizkreis": "HZ",
    "dev_heizkreis2": "HZ2",
    "dev_heizkreis3": "HZ3",
    "dev_heizkreis4": "HZ4",
    "dev_heizkreis5": "HZ5",
    "dev_waermeerzeuger2": "W2",
    "dev_statistik": "ST",
    "dev_unknown": "UK",
    "dev_ein_aus": "IO",
}

################################################################################
# Listen mit Fehlermeldungen, Warnmeldungen und Statustexte
# Beschreibungstext ist ebenfalls möglich
# class StatusItem(): def __init__(self, number, text, description = None):
################################################################################

# fmt: off
SYS_FEHLER: list[StatusItem] = [
    StatusItem(number=65535,text='kein Fehler', translation_key="sys_fehler_65535"),
    StatusItem(number=1,text='Kältemittelfühler Expansionsventil Eintritt (T1)', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_1"),
    StatusItem(number=2,text='Luftansaugfühler (T2)', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_2"),
    StatusItem(number=3,text='Wärmetauscherfühler AG Austritt (T3)', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_3"),
    StatusItem(number=4,text='Verdichtersauggasfühler (T4)', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_4"),
    StatusItem(number=5,text='EVI-Sauggasfühler (T5)', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_5"),
    StatusItem(number=6,text='Kältemittelfühler IG Austritt (T6)', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_6"),
    StatusItem(number=7,text='Ölsumpffühler (T7)', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_7"),
    StatusItem(number=8,text='Expansionsventil EVI', description='Leitung prüfen, ggf. austauschen. Ggf. defektes Expansionsventil austauschen.', translation_key="sys_fehler_8"),
    StatusItem(number=9,text='Niederdrucksensor (P1)', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_9"),
    StatusItem(number=10,text='Hochdrucksensor (P2)', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_10"),
    StatusItem(number=11,text='Mitteldrucksensor (P3)', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_11"),
    StatusItem(number=12,text='Expansionsventil Kühlen defekt', description='Leitung prüfen, ggf. austauschen. Expansionsventil austauschen.', translation_key="sys_fehler_12"),
    StatusItem(number=13,text='keine Kommunikation zum Inverter', description='Lastspannung am Verdichter und Inverter prüfen. & Verbindungsleitung Steuerplatine Kältesatz zu Inverter prüfen. & Ggf. defekte Steuerplatine Kältesatz austauschen.', translation_key="sys_fehler_13"),
    StatusItem(number=14,text='keine Kommunikation zum Außengerät', description='Verbindungsleitung zum Außengerät prüfen.', translation_key="sys_fehler_14"),
    StatusItem(number=15,text='Hochdruckschalter hat ausgelöst', description='Drücke im Kältekreis kontrollieren. Volumenstrom prüfen. & Verdrahtung prüfen. & Sicherstellen, dass die Einsatzgrenzen der Wärmepumpe eingehalten werden. & Kältekreis prüfen.', translation_key="sys_fehler_15"),
    StatusItem(number=16,text='Inverter gesperrt, da in den letzten 10 Stunden 10 Fehler aufgetreten sind', description='Spannungsversorgung mindestens 10 Minuten unterbrechen. Bei wiederholtem Auftreten Weishaupt-Kundendienst benachrichtigen.', translation_key="sys_fehler_16"),
    StatusItem(number=17,text='EEPROM Speicher-Fehler', description='Spannungsversorgung mindestens 10 Minuten unterbrechen.', translation_key="sys_fehler_17"),
    StatusItem(number=18,text='keine Modbus-Kommunikation zwischen Regler EC und Steuerplatine Kältesatz', description='Modbus-Verbindung prüfen.', translation_key="sys_fehler_18"),
    StatusItem(number=19,text='durch Inverter-Alarm Wärmepumpe abgeschaltet', description='Bei wiederholtem Auftreten Weishaupt-Kundendienst benachrichtigen.', translation_key="sys_fehler_19"),
    StatusItem(number=20,text='Verdichter passt nicht zur Konfiguration', description='Verdichtertyp prüfen. & Spannungsversorgung mindestens 10 Minuten unterbrechen.', translation_key="sys_fehler_20"),
    StatusItem(number=21,text='Niederdruck-Störung', description='Verdampfer auf Eisfreiheit prüfen. Funktion Ventilator prüfen. & Niederdrucksensor (P1) prüfen. Kältekreis prüfen.', translation_key="sys_fehler_21"),
    StatusItem(number=22,text='zu geringe Überhitzung', description='Wenn der Fehler wiederholt auftritt: Überhitzung prüfen. & Verdichtersauggasfühler (T4) prüfen. Niederdrucksensor (P1) prüfen. & Antrieb Expansionsventil prüfen. Kältekreis prüfen.', translation_key="sys_fehler_22"),
    StatusItem(number=23,text='zu hohe Überhitzung', description='Wenn der Fehler wiederholt auftritt: Überhitzung prüfen. & Verdichtersauggasfühler (T4) prüfen. Niederdrucksensor (P1) prüfen. & Antrieb Expansionsventil prüfen. Kältekreis prüfen.', translation_key="sys_fehler_23"),
    StatusItem(number=24,text='EVI zu hohe Überhitzung', description='Wenn der Fehler wiederholt auftritt: Kältekreis prüfen. & Lecksuche durchführen.', translation_key="sys_fehler_24"),
    StatusItem(number=25,text='Kältemittelmenge zu niedrig', description='Wenn der Fehler wiederholt auftritt: Kältekreis prüfen. & Lecksuche durchführen.', translation_key="sys_fehler_25"),
    StatusItem(number=26,text='Hochdruck-Störung', description='Wärmeabnahme prüfen. & Hohe Warmwasser-Solltemperaturen vermeiden. & Sicherstellen, dass die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird. & Einstellung Überströmventil prüfen.', translation_key="sys_fehler_26"),
    StatusItem(number=27,text='Kondensationstemperatur zu niedrig', description='Der erwartete Betriebszustand wird bei hoher Außentemperatur und geringer Vorlauftemperatur nicht erreichen. & Anlage mit 2. Wärmeerzeuger hochheizen.', translation_key="sys_fehler_27"),
    StatusItem(number=28,text='Kondensationstemperatur zu hoch', description='Wärmeabnahme prüfen. Einstellung Überströmventil prüfen. Heizwasser-Volumenstrom prüfen.', translation_key="sys_fehler_28"),
    StatusItem(number=29,text='Verdampfungstemperatur zu niedrig', description='Verdampfer auf Eisfreiheit prüfen. Funktion Ventilator prüfen. & Kältekreis prüfen.', translation_key="sys_fehler_29"),
    StatusItem(number=30,text='Verdampfungstemperatur zu hoch', description='Die Einsatzgrenze der Wärmepumpe wurde überschritten. & Sicherstellen, dass die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird.', translation_key="sys_fehler_30"),
    StatusItem(number=32,text='Wärmepumpe nicht kompatibel', description='Spannungsversorgung Verdichter prüfen. Spannungsversorgung von den Klemmen zum Kältesatz prüfen. & Weishaupt-Kundendienst benachrichtigen.', translation_key="sys_fehler_32"),
    StatusItem(number=33,text='Regler EC hat keine Verbindung zum Erweiterungsmodul EM-HK', description='Verbindungsleitung zwischen Regler und Erweiterungsmodul prüfen.', translation_key="sys_fehler_33"),
    StatusItem(number=40,text='Volumenstrom zu gering', description='Mindestvolumenstrom beachten [Kap. 3.4.6]. Volumenstrom prüfen, ggf. erhöhen. & Leitung Volumenstromsensor (B10) prüfen. Volumenstromsensor (B10) prüfen, ggf. austauschen.', translation_key="sys_fehler_40"),
    StatusItem(number=41,text='Spreizung LWT/Rücklauf negativ / Vierwegeventil schaltet nach dem Abtauen nicht zurück; nach 3 Warnungen verriegelt die Anlage)', description='Volumenstrom anpassen. Pumpenleistung reduzieren. Vierwegeventil prüfen. & Ggf. Funktion deaktivieren.', translation_key="sys_fehler_41"),
    StatusItem(number=43,text='Ventilator blockiert', description='Verdampfer auf Eisfreiheit prüfen. Funktion Ventilator prüfen.', translation_key="sys_fehler_43"),
    StatusItem(number=44,text='Drehzahl Ventilator zu niedrig', description='Verdampfer auf Eisfreiheit prüfen. Funktion Ventilator prüfen.', translation_key="sys_fehler_44"),
    StatusItem(number=47,text='Kommunikation Regler EC zu Steuerplatine Kältesatz fehlerhaft', description='Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_47"),
    StatusItem(number=50,text='Außenfühler (B1) unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_50"),
    StatusItem(number=51,text='Außenfühler (B1) kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_51"),
    StatusItem(number=52,text='Weichenfühler (B2) unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_52"),
    StatusItem(number=53,text='Weichenfühler (B2) kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_53"),
    StatusItem(number=54,text='Warmwasserfühler (B3) unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_54"),
    StatusItem(number=55,text='Warmwasserfühler (B3) kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_55"),
    StatusItem(number=56,text='Vorlauffühler Verflüssiger (B4) unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_56"),
    StatusItem(number=57,text='Vorlauffühler Verflüssiger (B4) kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_57"),
    StatusItem(number=58,text='Vorlauffühler (B7) unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_58"),
    StatusItem(number=59,text='Vorlauffühler (B7) kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_59"),
    StatusItem(number=60,text='Rücklauffühler (B9) unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_60"),
    StatusItem(number=61,text='Rücklauffühler (B9) kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_61"),
    StatusItem(number=64,text='Pufferfühler (B11) unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_64"),
    StatusItem(number=65,text='Pufferfühler (B11) kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_65"),
    StatusItem(number=66,text='Mischerfühler regenerativ (B2.1) unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_66"),
    StatusItem(number=67,text='Mischerfühler regenerativ (B2.1) kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_67"),
    StatusItem(number=70,text='Vorlauffühler Zweiter Heizkreis (B6.2) unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_70"),
    StatusItem(number=71,text='Vorlauffühler Zweiter Heizkreis (B6.2) kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_71"),
    StatusItem(number=72,text='Fühler (T1.2) unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_72"),
    StatusItem(number=73,text='Fühler (T1.2) kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_73"),
    StatusItem(number=74,text='Fühler (T2.2) unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_74"),
    StatusItem(number=75,text='Fühler (T2.2) kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_75"),
    StatusItem(number=90,text='Analogeingang AE1 unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_90"),
    StatusItem(number=91,text='Analogeingang AE1 kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_91"),
    StatusItem(number=92,text='Analogeingang AE2 unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_92"),
    StatusItem(number=93,text='Analogeingang AE2 kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_93"),
    StatusItem(number=94,text='Analogeingang AE3 unterbrochen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_94"),
    StatusItem(number=95,text='Analogeingang AE3 kurzgeschlossen', description='Fühler und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_95"),
    StatusItem(number=101,text='Wärmepumpe wird außerhalb der Einsatzgrenzen betrieben', description='Sicherstellen, dass die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird, siehe W 26 bis W 30.', translation_key="sys_fehler_101"),
    StatusItem(number=102,text='maximale Abtauzeit überschritten', description='Bei exponiertem Aufstellungsort kann starker Wind zu dieser Warnung führen. Nach der Abtauung Verdampfer auf Eisfreiheit prüfen.', translation_key="sys_fehler_102"),
    StatusItem(number=103,text='Kommunikation Kältekreis fehlerhaft', description='Spannungsversorgung mindestens 10 Minuten unterbrechen. Bei wiederholtem Auftreten Weishaupt-Kundendienst benachrichtigen.', translation_key="sys_fehler_103"),
    StatusItem(number=104,text='Druckgastemperatur zu hoch', description='Wärmeabnahme prüfen. Kältekreis prüfen.', translation_key="sys_fehler_104"),
    StatusItem(number=105,text='Stromaufnahme vom Inverter zu hoch', description='Sicherstellen, dass die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird. & Verdichteranschluss am Inverter prüfen.', translation_key="sys_fehler_105"),
    StatusItem(number=106,text='Stromaufnahme zu hoch', description='Sicherstellen, dass die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird. & Spannungsversorgung prüfen (Netzspannung zu gering). & Drosselspulen in der 400 V Zuleitung zum Inverter prüfen.', translation_key="sys_fehler_106"),
    StatusItem(number=107,text='Gleichspannung am Inverter zu hoch', description='Sicherstellen, dass die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird. & Spannungsversorgung prüfen.', translation_key="sys_fehler_107"),
    StatusItem(number=108,text='Gleichspannung am Inverter zu niedrig', description='Sicherstellen, dass die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird. & Spannungsversorgung prüfen.', translation_key="sys_fehler_108"),
    StatusItem(number=109,text='Wärmepumpe wird außerhalb vom zulässigen Spannungsbereich betrieben', description='Spannungsversorgung prüfen.', translation_key="sys_fehler_109"),
    StatusItem(number=110,text='Wärmepumpe wird außerhalb vom zulässigen Spannungsbereich betrieben', description='Spannungsversorgung prüfen.', translation_key="sys_fehler_110"),
    StatusItem(number=111,text='Hochdruckschalter hat ausgelöst', description='Wärmeabnahme prüfen. & Einstellung vom Überströmventil prüfen. Stellung der Kugelhähne am Innenund Außengerät prüfen. & Drücke im Kältekreis kontrollieren. Volumenstrom kontrollieren. & Verdrahtung prüfen. & Sicherstellen, dass die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird. & Kältekreis prüfen.', translation_key="sys_fehler_111"),
    StatusItem(number=112,text='Inverter ist überhitzt', description='Sicherstellen, dass: die Montagebedingungen für das Innengerät eingehalten werden & die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird & Weishaupt-Kundendienst benachrichtigen (Version der Steuerplatine Kältesatz RCC Modbus prüfen).', translation_key="sys_fehler_112"),
    StatusItem(number=113,text='Inverter ist überhitzt', description='Sicherstellen, dass: die Montagebedingungen für das Innengerät eingehalten werden & die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird & Weishaupt-Kundendienst benachrichtigen (Version der Steuerplatine Kältesatz RCC Modbus prüfen).', translation_key="sys_fehler_113"),
    StatusItem(number=114,text='Stellung vom Verdichtermotor kann nicht bestimmt werden', description='Sicherstellen, dass die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird. & Verdichteranschluss am Inverter prüfen.', translation_key="sys_fehler_114"),
    StatusItem(number=117,text='Gleichspannung am Inverter zu niedrig', description='Sicherstellen, dass die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird. & Spannungsversorgung prüfen.', translation_key="sys_fehler_117"),
    StatusItem(number=118,text='Strom zwischen Inverter und Verdichter ist zu hoch', description='Sicherstellen, dass die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird. & Verdichteranschluss am Inverter prüfen. Verdichter-Wicklungswiderstände messen.', translation_key="sys_fehler_118"),
    StatusItem(number=119,text='Stromaufnahme vom Verdichter zu hoch Zeitüberschreitung', description='Sicherstellen, dass die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird. & Verdichteranschluss am Inverter prüfen. Verdichter-Wicklungswiderstände messen.', translation_key="sys_fehler_119"),
    StatusItem(number=120,text='Invertertemperatur zu hoch', description='Sicherstellen, dass: die Montagebedingungen für das Innengerät eingehalten werden & die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird', translation_key="sys_fehler_120"),
    StatusItem(number=121,text='Spannung am Inverter zu gering', description='Spannung nach den Drosselspulen messen.', translation_key="sys_fehler_121"),
    StatusItem(number=122,text='Modbus-Konfigurationsfehler', description='Spannungsversorgung mindestens 10 Minuten unterbrechen.', translation_key="sys_fehler_122"),
    StatusItem(number=123,text='keine Modbus-Verbindung', description='Modbus-Verbindung (Leitung und Stecker) zwischen Inverter und Steuerplatine Kältesatz prüfen. & Spannungsversorgung mindestens 10 Minuten unterbrechen.', translation_key="sys_fehler_123"),
    StatusItem(number=124,text='Druckgastemperatur zu hoch', description='Wärmeabnahme prüfen. Kältekreis prüfen.', translation_key="sys_fehler_124"),
    StatusItem(number=127,text='Invertertemperatur zu hoch', description='Sicherstellen, dass: die Montagebedingungen für das Innengerät eingehalten werden & die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird', translation_key="sys_fehler_127"),
    StatusItem(number=128,text='Inverter ist überhitzt', description='Sicherstellen, dass: die Montagebedingungen für das Innengerät eingehalten werden & die Wärmepumpe innerhalb der Einsatzgrenzen betrieben wird & Weishaupt-Kundendienst benachrichtigen (Version der Steuerplatine Kältesatz RCC Modbus prüfen).', translation_key="sys_fehler_128"),
    StatusItem(number=129,text='Modbus-Kommunikation fehlerhaft', description='Modbus-Verbindung zwischen Inverter und Steuerplatine Kältesatz prüfen (Leitung und Stecker). & Spannungsversorgung mindestens 10 Minuten unterbrechen.', translation_key="sys_fehler_129"),
    StatusItem(number=130,text='Modbus-Kommunikation fehlerhaft', description='Modbus-Verbindung zwischen Inverter und Steuerplatine Kältesatz prüfen (Leitung und Stecker). & Spannungsversorgung mindestens 10 Minuten unterbrechen.', translation_key="sys_fehler_130"),
    StatusItem(number=133,text='Elektronikfehler', description='Spannungsversorgung mindestens 10 Minuten unterbrechen.', translation_key="sys_fehler_133"),
    StatusItem(number=135,text='Hochdruckschalter defekt', description='Hochdruckschalter-Anschluss prüfen.', translation_key="sys_fehler_135"),
    StatusItem(number=136,text='Verdichter passt nicht zur Konfiguration', description='Verdichtertyp prüfen. & Spannungsversorgung mindestens 10 Minuten unterbrechen.', translation_key="sys_fehler_136"),
    StatusItem(number=137,text='Hochdruckschalter passt nicht zur Konfiguration', description='Hochdruckschalter prüfen. Spannungsversorgung mindestens 10 Minuten unterbrechen.', translation_key="sys_fehler_137"),
    StatusItem(number=140,text='Druckgastemperatur zu niedrig', description='Druckgasfühler (DT) und Leitung prüfen, ggf. austauschen.', translation_key="sys_fehler_140"),
    StatusItem(number=143,text='Invertertemperatur zu niedrig', description='Kühlung am Inverter prüfen. Gerät neu starten.', translation_key="sys_fehler_143"),
    StatusItem(number=144,text='Drosselspulentemperatur zu niedrig', description='Sicherstellen, dass die Montagebedingungen für das Innengerät eingehalten werden.', translation_key="sys_fehler_144"),
    StatusItem(number=150,text="Verdichter Stromsensor Phase U Fehler", translation_key="sys_fehler_150"),
    StatusItem(number=151,text="Verdichter Stromsensor Phase V Fehler", translation_key="sys_fehler_151"),
    StatusItem(number=152,text="Verdichter Stromsensor Phase W Fehler Spannungsversorgung von Eingangsklemme", translation_key="sys_fehler_152"),
    StatusItem(number=153,text="Stromsensor Fehler", translation_key="sys_fehler_153"),
    StatusItem(number=154,text="Inverter Temperatursensor Fehler", translation_key="sys_fehler_154"),
    StatusItem(number=155,text="Temperatursensor Fehler", translation_key="sys_fehler_155"),
    StatusItem(number=156,text="Druckgasfühler (DT)", translation_key="sys_fehler_156"),
    StatusItem(number=157,text="keine Kommunikation zur Steuerplatine Kältesatz", translation_key="sys_fehler_157"),
    StatusItem(number=158,text="EEPROM-Speicher-Fehler", translation_key="sys_fehler_158"),
    StatusItem(number=159,text="Stromaufnahme zu hoch", translation_key="sys_fehler_159"),
    StatusItem(number=160,text="Wärmepumpe wird außerhalb vom zulässigen Spannungsbereich betrieben", translation_key="sys_fehler_160"),
    StatusItem(number=161,text="Wärmepumpe wird außerhalb vom zulässigen Spannungsbereich betriebe", translation_key="sys_fehler_161"),
    StatusItem(number=162,text="Gleichspannung am Inverter zu hoch", translation_key="sys_fehler_162"),
    StatusItem(number=163,text="Gleichspannung am Inverter zu niedrig", translation_key="sys_fehler_163"),
    StatusItem(number=164,text="Hochdruckschalter hat ausgelöst", translation_key="sys_fehler_164"),
    StatusItem(number=165,text="Phase zwischen Eingang und Verdichter unterbrochen", translation_key="sys_fehler_165"),
    StatusItem(number=166,text="Inverter überhitzt", translation_key="sys_fehler_166"),
    StatusItem(number=167,text="Inverter überhitzt", translation_key="sys_fehler_167"),
    StatusItem(number=168,text="Konfigurationsfehler Verdichter", translation_key="sys_fehler_168"),
    StatusItem(number=169,text="Stromaufnahme vom Verdichter zu hoch", translation_key="sys_fehler_169"),
    StatusItem(number=170,text="Verdichter Phase U Überspannung", translation_key="sys_fehler_170"),
    StatusItem(number=171,text="Verdichter Phase V Überspannung", translation_key="sys_fehler_171"),
    StatusItem(number=172,text="Verdichter Phase W Überspannung", translation_key="sys_fehler_172"),
    StatusItem(number=173,text="Phasenausfall am Verdichter", translation_key="sys_fehler_173"),
    StatusItem(number=174,text="Verdichter blockiert", translation_key="sys_fehler_174"),
    StatusItem(number=175,text="Verdichter startet nicht", translation_key="sys_fehler_175"),
    StatusItem(number=176,text="Unregelmäßige Spannungsversorgung vom Inverter", translation_key="sys_fehler_176"),
    StatusItem(number=177,text="Verdichter überlastet", translation_key="sys_fehler_177"),
    StatusItem(number=178,text="Temperatur am Druckgasfühler (DT) zu hoch", translation_key="sys_fehler_178"),
    StatusItem(number=179,text="Temperatur am Inverter", translation_key="sys_fehler_179"),
    StatusItem(number=180,text="Verdichter blockiert", translation_key="sys_fehler_180"),
    StatusItem(number=181,text="Verdichter blockiert", translation_key="sys_fehler_181"),
    StatusItem(number=182,text="Stromaufnahme zu hoch", translation_key="sys_fehler_182"),
    StatusItem(number=183,text="Stromaufnahme zu hoch", translation_key="sys_fehler_183"),
    StatusItem(number=184,text="Spannung zu hoch", translation_key="sys_fehler_184"),
]  # noqa: E501

# fmt: on

SYS_FEHLERFREI: list[StatusItem] = [
    StatusItem(number=0, text="Fehler aktiv", translation_key="fehler_aktiv"),
    StatusItem(
        number=1,
        text="Störungsfreier Betrieb",
        translation_key="stoerungsfreier_betrieb",
    ),
]

SYS_BETRIEBSANZEIGE: list[StatusItem] = [
    StatusItem(
        number=0, text="undefiniert", translation_key="system_operationmode_undefined"
    ),
    StatusItem(
        number=1, text="Relaistest", translation_key="system_operationmode_relaistest"
    ),
    StatusItem(
        number=2, text="Notaus", translation_key="system_operationmode_emergencystop"
    ),
    StatusItem(
        number=3, text="Diagnose", translation_key="system_operationmode_diagnosis"
    ),
    StatusItem(
        number=4, text="Handbetrieb", translation_key="system_operationmode_manual"
    ),
    StatusItem(
        number=5,
        text="Handbetrieb Heizen",
        translation_key="system_operationmode_manualheating",
    ),
    StatusItem(
        number=6,
        text="Handbetrieb Kühlen",
        translation_key="system_operationmode_manualcooling",
    ),
    StatusItem(
        number=7,
        text="Manueller Abtaubetrieb",
        translation_key="system_operationmode_manualdefrost",
    ),
    StatusItem(
        number=8, text="Abtauen", translation_key="system_operationmode_defrost"
    ),
    StatusItem(
        number=9,
        text="2. WEZ",
        translation_key="system_operationmode_manual2ndheatsource",
    ),
    StatusItem(
        number=10, text="EVU_SPERRE", translation_key="system_operationmode_sgtariff"
    ),
    StatusItem(
        number=11, text="SG Tarif", translation_key="system_operationmode_sgtariff"
    ),
    StatusItem(
        number=12, text="SG Maximal", translation_key="system_operationmode_sgmax"
    ),
    StatusItem(
        number=13, text="Tarifladung", translation_key="system_operationmode_tariffload"
    ),
    StatusItem(
        number=14,
        text="Erhöhter Betrieb",
        translation_key="system_operationmode_elevatedoperation",
    ),
    StatusItem(
        number=15, text="Standzeit", translation_key="system_operationmode_standbytime"
    ),
    StatusItem(
        number=16, text="Standby", translation_key="system_operationmode_standby"
    ),
    StatusItem(number=17, text="Spülen", translation_key="system_operationmode_rinse"),
    StatusItem(
        number=18,
        text="Frostschutz",
        translation_key="system_operationmode_frosprotection",
    ),
    StatusItem(
        number=19, text="Heizbetrieb", translation_key="system_operationmode_heating"
    ),
    StatusItem(
        number=20,
        text="Warmwasserbetrieb",
        translation_key="system_operationmode_hotwater",
    ),
    StatusItem(
        number=21,
        text="Legionellenschutz",
        translation_key="system_operationmode_legionellaprotection",
    ),
    StatusItem(
        number=22,
        text="Umschaltung HZ KU",
        translation_key="system_operationmode_switchheatingcooling",
    ),
    StatusItem(
        number=23, text="Kühlbetrieb", translation_key="system_operationmode_cooling"
    ),
    StatusItem(
        number=24,
        text="Passive Kühlung",
        translation_key="system_operationmode_passivecooling",
    ),
    StatusItem(
        number=25, text="Sommerbetrieb", translation_key="system_operationmode_summer"
    ),
    StatusItem(
        number=26,
        text="Schwimmbadbetrieb",
        translation_key="system_operationmode_swimmingpool",
    ),
    StatusItem(
        number=27, text="Urlaub", translation_key="system_operationmode_vacation"
    ),
    StatusItem(
        number=28,
        text="Estrichprogramm",
        translation_key="system_operationmode_screedprogram",
    ),
    StatusItem(
        number=29, text="Gesperrt", translation_key="system_operationmode_locked"
    ),
    StatusItem(
        number=30, text="Sperre AT", translation_key="system_operationmode_lockedat"
    ),
    StatusItem(
        number=31,
        text="Sperre Sommer",
        translation_key="system_operationmode_lockedsummer",
    ),
    StatusItem(
        number=32,
        text="Sperre Winter",
        translation_key="system_operationmode_lockedwinter",
    ),
    StatusItem(
        number=33,
        text="Einsatzgrenze",
        translation_key="system_operationmode_applicationlimit",
    ),
    StatusItem(
        number=34, text="HK Sperre", translation_key="system_operationmode_lockedcv"
    ),
    StatusItem(
        number=35, text="Absenkbetrieb", translation_key="system_operationmode_lowering"
    ),
    StatusItem(
        number=36,
        text="Vorlauf regenerativ",
        translation_key="system_operationmode_regenerativeflow",
    ),
    StatusItem(
        number=43,
        text="Ölrückführung",
        translation_key="system_operationmode_oilrecirculation",
    ),
]

SYS_BETRIEBSART: list[StatusItem] = [
    StatusItem(
        number=0, text="Automatik", translation_key="sys_operationmode_automatic"
    ),
    StatusItem(number=1, text="Heizen", translation_key="sys_operationmode_heating"),
    StatusItem(number=2, text="Kühlen", translation_key="sys_operationmode_cooling"),
    StatusItem(number=3, text="Sommer", translation_key="sys_operationmode_summer"),
    StatusItem(number=4, text="Standby", translation_key="sys_operationmode_standby"),
    StatusItem(
        number=5, text="2.WEZ", translation_key="sys_operationmode_2ndheatsource"
    ),
]

HP_BETRIEB: list[StatusItem] = [
    StatusItem(
        number=0, text="Undefiniert", translation_key="heatpump_operationmode_undefined"
    ),
    StatusItem(
        number=1, text="Relaistest", translation_key="heatpump_operationmode_relaistest"
    ),
    StatusItem(
        number=2, text="Notaus", translation_key="heatpump_operationmode_emergencystop"
    ),
    StatusItem(
        number=3, text="Diagnose", translation_key="heatpump_operationmode_diagnosis"
    ),
    StatusItem(
        number=4, text="Handbetrieb", translation_key="heatpump_operationmode_manual"
    ),
    StatusItem(
        number=5,
        text="Handbetrieb Heizen",
        translation_key="heatpump_operationmode_manualheating",
    ),
    StatusItem(
        number=6,
        text="Handbetrieb Kühlen",
        translation_key="heatpump_operationmode_manualcooling",
    ),
    StatusItem(
        number=7,
        text="Manueller Abtaubetrieb",
        translation_key="heatpump_operationmode_manualdefrost",
    ),
    StatusItem(
        number=8, text="Abtauen", translation_key="heatpump_operationmode_defrost"
    ),
    StatusItem(
        number=9,
        text="WEZ2",
        translation_key="heatpump_operationmode_manual2ndheatsource",
    ),
    StatusItem(
        number=10, text="EVU_SPERRE", translation_key="heatpump_operationmode_evu"
    ),
    StatusItem(
        number=11, text="SG Tarif", translation_key="heatpump_operationmode_sgtariff"
    ),
    StatusItem(
        number=12, text="SG Maximal", translation_key="heatpump_operationmode_sgmax"
    ),
    StatusItem(
        number=13,
        text="Tarifladung",
        translation_key="heatpump_operationmode_tariffload",
    ),
    StatusItem(
        number=14,
        text="Erhöhter Betrieb",
        translation_key="heatpump_operationmode_elevatedoperation",
    ),
    StatusItem(
        number=15,
        text="Standzeit",
        translation_key="heatpump_operationmode_standbytime",
    ),
    StatusItem(
        number=16,
        text="Standbybetrieb",
        translation_key="heatpump_operationmode_standby",
    ),
    StatusItem(
        number=17, text="Spülbetrieb", translation_key="heatpump_operationmode_rinse"
    ),
    StatusItem(
        number=18,
        text="Frostschutz",
        translation_key="heatpump_operationmode_frosprotection",
    ),
    StatusItem(
        number=19, text="Heizbetrieb", translation_key="heatpump_operationmode_heating"
    ),
    StatusItem(
        number=20,
        text="Warmwasserbetrieb",
        translation_key="heatpump_operationmode_hotwater",
    ),
    StatusItem(
        number=21,
        text="Legionellenschutz",
        translation_key="heatpump_operationmode_legionellaprotection",
    ),
    StatusItem(
        number=22,
        text="Umschaltung HZ KU",
        translation_key="heatpump_operationmode_switchheatingcooling",
    ),
    StatusItem(
        number=23, text="Kühlbetrieb", translation_key="heatpump_operationmode_cooling"
    ),
    StatusItem(
        number=24,
        text="Passive Kühlung",
        translation_key="heatpump_operationmode_passivecooling",
    ),
    StatusItem(
        number=25, text="Sommerbetrieb", translation_key="heatpump_operationmode_summer"
    ),
    StatusItem(
        number=26,
        text="Schwimmbad",
        translation_key="heatpump_operationmode_swimmingpool",
    ),
    StatusItem(
        number=27, text="Urlaub", translation_key="heatpump_operationmode_vacation"
    ),
    StatusItem(
        number=28,
        text="Estrich",
        translation_key="heatpump_operationmode_screedprogram",
    ),
    StatusItem(
        number=29, text="Gesperrt", translation_key="heatpump_operationmode_locked"
    ),
    StatusItem(
        number=30, text="Sperre AT", translation_key="heatpump_operationmode_lockedat"
    ),
    StatusItem(
        number=31,
        text="Sperre Sommer",
        translation_key="heatpump_operationmode_lockedsummer",
    ),
    StatusItem(
        number=32,
        text="Sperre Winter",
        translation_key="heatpump_operationmode_lockedwinter",
    ),
    StatusItem(
        number=33,
        text="Einsatzgrenze",
        translation_key="heatpump_operationmode_applicationlimit",
    ),
    StatusItem(
        number=34, text="HK Sperre", translation_key="heatpump_operationmode_lockedcv"
    ),
    StatusItem(
        number=35, text="Absenk", translation_key="heatpump_operationmode_lowering"
    ),
    StatusItem(
        number=43,
        text="Ölrückführung",
        translation_key="heatpump_operationmode_oilrecirculation",
    ),
]

HP_STOERMELDUNG: list[StatusItem] = [
    StatusItem(number=0, text="Störung", translation_key="hp_stoerung"),
    StatusItem(number=1, text="Störungsfrei", translation_key="hp_stoerungsfrei"),
]

HP_RUHEMODUS: list[StatusItem] = [
    StatusItem(number=0, text="aus", translation_key="hp_ruhemodus_0"),
    StatusItem(number=1, text="80 %", translation_key="hp_ruhemodus_1"),
    StatusItem(number=2, text="60 %", translation_key="hp_ruhemodus_2"),
    StatusItem(number=3, text="40 %", translation_key="hp_ruhemodus_3"),
]

HZ_KONFIGURATION: list[StatusItem] = [
    StatusItem(number=0, text="aus", translation_key="hp_konf_aus"),
    StatusItem(number=1, text="Pumpenkreis", translation_key="hp_konf_pumpenkreis"),
    StatusItem(number=2, text="Mischkreis", translation_key="hp_konf_mischkreis"),
    StatusItem(
        number=3,
        text="Sollwert (Pumpe M1)",
        translation_key="hp_konf_sollwert_pumpe_m1",
    ),
]

HZ_ANFORDERUNG: list[StatusItem] = [
    StatusItem(number=0, text="aus", translation_key="hz_anforderung_aus"),
    StatusItem(
        number=1,
        text="witterungsgeführt",
        translation_key="hz_anforderung_witterungsgefuehrt",
    ),
    StatusItem(number=2, text="konstant", translation_key="hz_anforderung_konstant"),
]

HZ_BETRIEBSART: list[StatusItem] = [
    StatusItem(
        number=0, text="Automatik", translation_key="hz_operationmode_automatic"
    ),
    StatusItem(number=1, text="Komfort", translation_key="hz_operationmode_comfort"),
    StatusItem(number=2, text="Normal", translation_key="hz_operationmode_normal"),
    StatusItem(
        number=3, text="Absenkbetrieb", translation_key="hz_operationmode_lowering"
    ),
    StatusItem(number=4, text="Standby", translation_key="hz_operationmode_standby"),
]

HZ_PARTY_PAUSE: list[StatusItem] = [
    StatusItem(number=1, text="Pause 12.0h", translation_key="hz_pause_12"),
    StatusItem(number=2, text="Pause 11.5h", translation_key="hz_pause_11_5"),
    StatusItem(number=3, text="Pause 11.0h", translation_key="hz_pause_11"),
    StatusItem(number=4, text="Pause 10.5h", translation_key="hz_pause_10_5"),
    StatusItem(number=5, text="Pause 10.0h", translation_key="hz_pause_10"),
    StatusItem(number=6, text="Pause 9.5h", translation_key="hz_pause_9_5"),
    StatusItem(number=7, text="Pause 9.0h", translation_key="hz_pause_9"),
    StatusItem(number=8, text="Pause 8.5h", translation_key="hz_pause_8_5"),
    StatusItem(number=9, text="Pause 8.0h", translation_key="hz_pause_8"),
    StatusItem(number=10, text="Pause 7.5h", translation_key="hz_pause_7_5"),
    StatusItem(number=11, text="Pause 7.0h", translation_key="hz_pause_7"),
    StatusItem(number=12, text="Pause 6.5h", translation_key="hz_pause_6_5"),
    StatusItem(number=13, text="Pause 6.0h", translation_key="hz_pause_6"),
    StatusItem(number=14, text="Pause 5.5h", translation_key="hz_pause_5_5"),
    StatusItem(number=15, text="Pause 5.0h", translation_key="hz_pause_5"),
    StatusItem(number=16, text="Pause 4.5h", translation_key="hz_pause_4_5"),
    StatusItem(number=17, text="Pause 4.0h", translation_key="hz_pause_4"),
    StatusItem(number=18, text="Pause 3.5h", translation_key="hz_pause_3_5"),
    StatusItem(number=19, text="Pause 3.0h", translation_key="hz_pause_3"),
    StatusItem(number=20, text="Pause 2.5h", translation_key="hz_pause_2_5"),
    StatusItem(number=21, text="Pause 2.0h", translation_key="hz_pause_2"),
    StatusItem(number=22, text="Pause 1.5h", translation_key="hz_pause_1_5"),
    StatusItem(number=23, text="Pause 1.0h", translation_key="hz_pause_1"),
    StatusItem(number=24, text="Pause 0.5h", translation_key="hz_pause_0_5"),
    StatusItem(number=25, text="Automatik", translation_key="hz_party_pause_auto"),
    StatusItem(number=26, text="Party 0.5h", translation_key="hz_party_0_5"),
    StatusItem(number=27, text="Party 1.0h", translation_key="hz_party_1"),
    StatusItem(number=28, text="Party 1.5h", translation_key="hz_party_1_5"),
    StatusItem(number=29, text="Party 2.0h", translation_key="hz_party_2"),
    StatusItem(number=30, text="Party 2.5h", translation_key="hz_party_2_5"),
    StatusItem(number=31, text="Party 3.0h", translation_key="hz_party_3"),
    StatusItem(number=32, text="Party 3.5h", translation_key="hz_party_3_5"),
    StatusItem(number=33, text="Party 4.0h", translation_key="hz_party_4"),
    StatusItem(number=34, text="Party 4.5h", translation_key="hz_party_4_5"),
    StatusItem(number=35, text="Party 5.0h", translation_key="hz_party_5"),
    StatusItem(number=36, text="Party 5.5h", translation_key="hz_party_5_5"),
    StatusItem(number=37, text="Party 6.0h", translation_key="hz_party_6"),
    StatusItem(number=38, text="Party 6.5h", translation_key="hz_party_6_5"),
    StatusItem(number=39, text="Party 7.0h", translation_key="hz_party_7"),
    StatusItem(number=40, text="Party 7.5h", translation_key="hz_party_7_5"),
    StatusItem(number=41, text="Party 8.0h", translation_key="hz_party_8"),
    StatusItem(number=42, text="Party 8.5h", translation_key="hz_party_8_5"),
    StatusItem(number=43, text="Party 9.0h", translation_key="hz_party_9"),
    StatusItem(number=44, text="Party 9.5h", translation_key="hz_party_9_5"),
    StatusItem(number=45, text="Party 10.0h", translation_key="hz_party_10"),
    StatusItem(number=46, text="Party 10.5h", translation_key="hz_party_10_5"),
    StatusItem(number=47, text="Party 11.0h", translation_key="hz_party_11"),
    StatusItem(number=48, text="Party 11.5h", translation_key="hz_party_11_5"),
    StatusItem(number=49, text="Party 12.0h", translation_key="hz_party_12"),
]

WW_KONFIGURATION: list[StatusItem] = [
    StatusItem(number=0, text="aus", translation_key="ww_konf_aus"),
    StatusItem(number=1, text="Umlenkventil", translation_key="ww_konf_umlenkventil"),
    StatusItem(number=2, text="Pumpe", translation_key="ww_konf_pumpe"),
]

HP_KONFIGURATION: list[StatusItem] = [
    StatusItem(number=0, text="Nicht konfiguriert", translation_key="hp_konf_0"),
    StatusItem(number=1, text="Heizen", translation_key="hp_conf_1"),
    StatusItem(number=2, text="Heizen, Kühlen", translation_key="hp_conf_2"),
    StatusItem(number=3, text="Heizen, Kühlen", translation_key="hp_conf_3"),
    StatusItem(number=4, text="Heizen, Warmwasser", translation_key="hp_conf_4"),
]

WW_PUSH: list[StatusItem] = [
    StatusItem(number=0, text="AUS", translation_key="ww_push_aus"),
]
# Fill WW_PUSH with values for every 5 Minutes
for i in range(5, 240, 5):
    WW_PUSH.append(  # noqa: PERF401
        StatusItem(
            number=i,
            text=str(object=i) + " " + UnitOfTime.MINUTES,
            translation_key="ww_push_" + str(object=i),
        ),
    )


W2_STATUS: list[StatusItem] = [
    StatusItem(number=0, text="aus", translation_key="w2_status_aus"),
    StatusItem(number=1, text="ein", translation_key="w2_status_ein"),
]

W2_KONFIG: list[StatusItem] = [
    StatusItem(number=0, text="0", translation_key="w2_konf_0"),
    StatusItem(number=1, text="1", translation_key="w2_konf_1"),
]

EP1_KONFIG: list[StatusItem] = [
    StatusItem(number=5, text="aktiviert", translation_key="w2_konf_0"),
    StatusItem(number=255, text="AUS", translation_key="w2_konf_1"),
]

EP2_KONFIG: list[StatusItem] = [
    StatusItem(number=6, text="aktiviert", translation_key="w2_konf_0"),
    StatusItem(number=255, text="AUS", translation_key="w2_konf_1"),
]


IO_KONFIG: list[StatusItem] = [
    StatusItem(number=0, text="0", translation_key="io_konf_0"),
    StatusItem(number=1, text="1", translation_key="io_konf_1"),
    StatusItem(number=2, text="2", translation_key="io_konf_2"),
    StatusItem(number=3, text="3", translation_key="io_konf_3"),
    StatusItem(number=4, text="4", translation_key="io_konf_4"),
    StatusItem(number=5, text="5", translation_key="io_konf_5"),
    StatusItem(number=6, text="6", translation_key="io_konf_6"),
    StatusItem(number=7, text="7", translation_key="io_konf_7"),
    StatusItem(number=65535, text="65535", translation_key="io_konf_65535"),
]

IO_KONFIG_IN: list[StatusItem] = [
    StatusItem(
        number=0,
        text="SG Ready",
        description="Siehe Smart-Grid-Funktion [Kap. 6.7.7.2]. Funktion kann nur in SGR1 gewählt werden und wird automatisch auf SGR2 übertragen, in SGR2 sind dann die anderen Funktionen gesperrt.",
        translation_key="io_konf_in_0",
    ),
    StatusItem(
        number=1,
        text="EVU-Sperre",
        description="Heiz- und Kühlbetrieb und Warmwasserladung gesperrt, Frostschutz ist sichergestellt.",
        translation_key="io_konf_in_1",
    ),
    StatusItem(
        number=2,
        text="Erhöhter Betrieb",
        description="Zu der Vorlaufsolltemperatur im Heizbetrieb und der Warmwasser-Solltemperatur wird die eingestellte ",
        translation_key="io_konf_in_2",
    ),
    StatusItem(
        number=3,
        text="HK-Sperre",
        description="Heiz- und Kühlbetrieb gesperrt, Frostschutz ist sichergestellt, Warmwasserladung weiterhin betriebsbereit. ",
        translation_key="io_konf_in_3",
    ),
    StatusItem(
        number=4,
        text="Umschaltung Hz/Kü",
        description="Wärmeanforderungen werden ignoriert, nur Kühlanforderungen wirken auf die Wärmepumpe. Die Funktion Umschaltung Hz/Kü hat Vorrang vor Erhöhter Betrieb.",
        translation_key="io_konf_in_4",
    ),
    StatusItem(
        number=5,
        text="Ruhemodus",
        description="Manueller Ruhemodus, externer Kontakt [Kap. 6.7.5.2].",
        translation_key="io_konf_in_5",
    ),
    StatusItem(
        number=6,
        text="Not-Aus",
        description="Wärmepumpe, Elektroheizung und Pumpe aus.",
        translation_key="io_konf_in_6",
    ),
    StatusItem(
        number=7,
        text="System Standby",
        description="Standby",
        translation_key="io_konf_in_7",
    ),
    StatusItem(
        number=8,
        text="Erzeugersperre HZ",
        description="Heizkreis durch Wärmepumpe gesperrt.",
        translation_key="io_konf_in_8",
    ),
    StatusItem(
        number=9,
        text="Erzeugersperre WW",
        description="Warmwasserladung durch Wärmepumpe gesperrt.",
        translation_key="io_konf_in_9",
    ),
    StatusItem(
        number=10,
        text="Erzeugersperre HZ und WW",
        description="Heizkreis und Warmwasserladung durch Wärmepumpe gesperrt",
        translation_key="io_konf_in_10",
    ),
    StatusItem(
        number=11,
        text="Warmwasser Standby",
        description="Warmwasserladung Standby.",
        translation_key="io_konf_in_11",
    ),
    StatusItem(
        number=12,
        text="Warmwasser Absenk",
        description="Warmwasserladung im Absenkbetrieb.",
        translation_key="io_konf_in_12",
    ),
    StatusItem(
        number=13,
        text="Warmwasser Normal",
        description="Warmwasserladung im Normalbetrieb.",
        translation_key="io_konf_in_13",
    ),
    StatusItem(
        number=14,
        text="Warmwasser PUSH",
        description="Vom Zeitprogramm abweichender Warmwasserbedarf. Der Trinkwasserspeicher wird auf Normaltemperatur aufgeheizt und gehalten.",
        translation_key="io_konf_in_14",
    ),
    StatusItem(
        number=15,
        text="Taupunktwächter",
        description="Kühlbetrieb für Heizkreise gesperrt.",
        translation_key="io_konf_in_15",
    ),
    StatusItem(
        number=16,
        text="Heizkreis … Standby",
        description="Heizkreis im Standby.",
        translation_key="io_konf_in_16",
    ),
    StatusItem(
        number=17,
        text="Heizkreis … Absenk",
        description="Heizkreis im Absenkbetrieb",
        translation_key="io_konf_in_17",
    ),
    StatusItem(
        number=18,
        text="Heizkreis … Normal",
        description="Heizkreis im Normalbetrieb.",
        translation_key="io_konf_in_18",
    ),
    StatusItem(
        number=19,
        text="Heizkreis … Komfort",
        description="Heizkreis im Komfortbetrieb",
        translation_key="io_konf_in_19",
    ),
    StatusItem(
        number=20,
        text="2.WEZ",
        description="2. Wärmeerzeuger über Eingang aktivieren.",
        translation_key="io_konf_in_20",
    ),
    StatusItem(
        number=21,
        text="Sperre Verdichter",
        description="Externe Vorgabe zur Sperre vom Verdichter.ng für Digitaleingang DE",
        translation_key="io_konf_in_21",
    ),
    StatusItem(
        number=65535,
        text="AUS",
        description="Keine Funktion, wird nicht angesteuert.",
        translation_key="io_konf_in_65535",
    ),
]

IO_KONFIG_OUT: list[StatusItem] = [
    StatusItem(
        number=0, text="AUS", description="Keine Funktion, wird nicht angesteuert."
    ),
    StatusItem(
        number=1,
        text="Zirkulationspumpe",
        description="Ausgang wird periodisch während dem Warmwasserprogramm angesteuert.",
        translation_key="io_config_out_1",
    ),
    StatusItem(
        number=2,
        text="ext. Heizkreispumpe",
        description="Ausgang wird im Heizbetrieb der Wärmepumpe angesteuert.",
        translation_key="io_config_out_2",
    ),
    StatusItem(
        number=3,
        text="Schaltuhr",
        description="Ausgang wird nach Zeitprogramm angesteuert.",
        translation_key="io_config_out_3",
    ),
    StatusItem(
        number=4,
        text="Störmeldung",
        description="Ausgang wird im Fehlerfall der Wärmepumpe angesteuert.",
        translation_key="io_config_out_4",
    ),
    StatusItem(
        number=5,
        text="Kühlbetrieb",
        description="Ausgang wird im Kühlbetrieb der Wärmepumpe angesteuert.",
        translation_key="io_config_out_5",
    ),
    StatusItem(
        number=6,
        text="Verdichterbetrieb",
        description="Ausgang wird bei Verdichterbetrieb der Wärmepumpe angesteuert.",
        translation_key="io_config_out_6",
    ),
    StatusItem(
        number=7,
        text="Warmwasserbetrieb",
        description="Ausgang wird bei Warmwasserladung angesteuert.",
        translation_key="io_config_out_7",
    ),
    StatusItem(
        number=8,
        text="Dauerspannung",
        description="Ausgang wird bei eingeschaltetem Innengerät angesteuert.",
        translation_key="io_config_out_8",
    ),
    StatusItem(
        number=9,
        text="Betriebsweitermeldung",
        description="Ausgang wird bei Verdichterbetrieb angesteuert.",
        translation_key="io_config_out_9",
    ),
    StatusItem(
        number=10,
        text="Hz- WW-Betrieb",
        description="Ausgang wird im Heizbetrieb oder bei Warmwasserladung angesteuert.",
        translation_key="io_config_out_10",
    ),
    StatusItem(
        number=11,
        text="Düsenringheizung",
        description="Ausgang wird bei zusätzlicher Heizung am Düsenring im Außengerät angesteuert.",
        translation_key="io_config_out_11",
    ),
    StatusItem(
        number=12,
        text="Kondensatwannenheizung",
        description="Ausgang wird bei zusätzlicher Heizung in der Kondensatwanne im Außengerät angesteuert",
        translation_key="io_config_out_12",
    ),
    StatusItem(
        number=13,
        text="Pumpe HK1",
        description="Ausgang wird bei Pumpenbetrieb für einen direkten Heizkreis angesteuert.",
        translation_key="io_config_out_13",
    ),
    StatusItem(
        number=14,
        text="Umlenkventil Heizen",
        description="Ausgang wird angesteuert, wenn das Dreiwegeventil auf Heizbetrieb steht.",
        translation_key="io_config_out_14",
    ),
    StatusItem(
        number=15,
        text="Umlenkventil Warmwasser",
        description="Ausgang wird angesteuert, wenn das Dreiwegeventil auf Warmwasserladung steht.",
        translation_key="io_config_out_15",
    ),
    StatusItem(
        number=65535,
        text="Umlenkventil Kühlen",
        description="Ausgang wird angesteuert, wenn das Dreiwegeventil auf Kühlbetrieb steht.",
        translation_key="io_config_out_65535",
    ),
    StatusItem(
        number=65535,
        text="65535",
        description="Keine Funktion, wird nicht angesteuert.",
        translation_key="io_config_out_65535",
    ),
]

IO_KONFIG_SGR: list[StatusItem] = [
    StatusItem(number=0, text="0", translation_key="io_conf_sgr_0"),
    StatusItem(number=1, text="1", translation_key="io_conf_sgr_1"),
    StatusItem(number=2, text="2", translation_key="io_conf_sgr_2"),
    StatusItem(number=3, text="3", translation_key="io_conf_sgr_3"),
    StatusItem(number=4, text="4", translation_key="io_conf_sgr_4"),
    StatusItem(number=5, text="5", translation_key="io_conf_sgr_5"),
    StatusItem(number=6, text="6", translation_key="io_conf_sgr_6"),
    StatusItem(number=7, text="7", translation_key="io_conf_sgr_7"),
    StatusItem(number=65535, text="65535", translation_key="65535"),
]

IO_STATUS: list[StatusItem] = [
    StatusItem(number=0, text="aus", translation_key="io_aus"),
    StatusItem(number=1, text="ein", translation_key="io_ein"),
]


#####################################################
# Description of physical units via the status list #
#####################################################

PARAMS_PERCENTAGE: dict = {"min": 0, "max": 100, "precision": 0, "unit": PERCENTAGE}

PARAMS_ROOMTEMP: dict = {
    "min": 16,
    "max": 28,
    "step": 0.5,
    "divider": 10,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "precision": 1,
    "unit": UnitOfTemperature.CELSIUS,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_ROOMTEMP_LOW: dict = {
    "min": 16,
    "max": 28,
    "step": 0.5,
    "divider": 10,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "dynamic_max": "raum_soll_temp_normal",
    "precision": 1,
    "icon": "mdi:thermometer-low",
    "unit": UnitOfTemperature.CELSIUS,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_ROOMTEMP_MID: dict = {
    "min": 16,
    "max": 28,
    "step": 0.5,
    "divider": 10,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "dynamic_min": "raum_soll_temp_absenk",
    "dynamic_max": "raum_soll_temp_komf",
    "precision": 1,
    "unit": UnitOfTemperature.CELSIUS,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_ROOMTEMP_HIGH: dict = {
    "min": 16,
    "max": 28,
    "step": 0.5,
    "divider": 10,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "dynamic_min": "raum_soll_temp_normal",
    "precision": 1,
    "icon": "mdi:thermometer-high",
    "unit": UnitOfTemperature.CELSIUS,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_WATERTEMP: dict = {
    "min": 5.5,
    "max": 60,
    "step": 0.5,
    "divider": 10,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "precision": 1,
    "icon": "mdi:thermometer-water",
    "unit": UnitOfTemperature.CELSIUS,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_WATERTEMP_LOW: dict = {
    "min": 5.5,
    "max": 60,
    "step": 0.5,
    "divider": 10,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "dynamic_max": "ww_normal",
    "precision": 1,
    "icon": "mdi:thermometer-water",
    "unit": UnitOfTemperature.CELSIUS,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_WATERTEMP_HIGH: dict = {
    "min": 5.5,
    "max": 60,
    "step": 0.5,
    "divider": 10,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "dynamic_min": "ww_absenk",
    "precision": 1,
    "icon": "mdi:thermometer-water",
    "unit": UnitOfTemperature.CELSIUS,
    "stateclass": SensorStateClass.MEASUREMENT,
}


PARAMS_SGREADYTEMP: dict = {
    "min": 0,
    "max": 30,
    "step": 0.5,
    "divider": 10,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "precision": 1,
    "unit": UnitOfTemperature.CELSIUS,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_BIVALENZTEMP: dict = {
    "min": -20,
    "max": 40,
    "step": 0.5,
    "divider": 10,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "precision": 1,
    "unit": UnitOfTemperature.CELSIUS,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_STDTEMP: dict = {
    "min": -60,
    "max": 100,
    "step": 0.5,
    "divider": 10,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "precision": 1,
    "unit": UnitOfTemperature.CELSIUS,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_DELTA_T: dict = {
    "min": -60,
    "max": 100,
    "step": 0.5,
    "divider": 10,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "precision": 1,
    "unit": UnitOfTemperature.KELVIN,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_STDPRESSURE: dict = {
    "min": 0,
    "max": 100,
    "step": 0.5,
    "divider": 1,
    "deviceclass": SensorDeviceClass.PRESSURE,
    "precision": 1,
    "unit": UnitOfPressure.BAR,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_STDPRPM: dict = {
    "min": 0,
    "max": 10000,
    "step": 0.5,
    "divider": 1,
    # "deviceclass": SensorDeviceClass.,
    "precision": 1,
    "unit": REVOLUTIONS_PER_MINUTE,
    "stateclass": SensorStateClass.MEASUREMENT,
}


PARAMS_HZKENNLINIE: dict = {
    "min": 0.05,
    "max": 1.5,
    "step": 0.05,
    "divider": 100,
    "precision": 2,
    "icon": "mdi:chart-line",
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_FLOWRATE: dict = {
    "min": 0,
    "max": 5,
    "step": 0.1,
    "divider": 100,
    "precision": 2,
    "unit": UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_ENERGY: dict = {
    "min": 0,
    "max": 999999999999,
    "deviceclass": SensorDeviceClass.ENERGY,
    "precision": 0,
    "unit": UnitOfEnergy.KILO_WATT_HOUR,
    "stateclass": SensorStateClass.TOTAL_INCREASING,
}

PARAMS_ENERGY_WEBIF: dict = {
    "min": 0,
    "max": 999999999999,
    "deviceclass": SensorDeviceClass.ENERGY,
    "precision": 3,
    "unit": UnitOfEnergy.KILO_WATT_HOUR,
    "stateclass": SensorStateClass.TOTAL_INCREASING,
}

PARAMS_CALCPOWER: dict = {
    "min": 0,
    "max": 50000,
    "val_1": "luftansautgemp",  # 30002,
    "val_2": "vl_temp",  # 33104,
    "val_3": "aussentemp",  # 30001,
    "deviceclass": SensorDeviceClass.POWER,
    "precision": 0,
    "unit": UnitOfPower.WATT,
    "stateclass": SensorStateClass.MEASUREMENT,
    "calculation": "(val_0 / 100) * power.map(val_1, val_2)",
}

PARAMS_CALCSPREIZUNG: dict = {
    "min": 0,
    "max": 50,
    "divider": 10,
    "val_1": "rl_temp",  # 30001,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "precision": 1,
    "unit": UnitOfTemperature.CELSIUS,
    "stateclass": SensorStateClass.MEASUREMENT,
    "calculation": "val_0 - val_1/10",
}


PARAMS_CALCTAZ: dict = {
    "min": 0,
    "max": 50,
    "val_1": "el_energie_heute",
    "precision": 2,
    "stateclass": SensorStateClass.MEASUREMENT,
    "icon": "mdi:sigma",
    "calculation": "val_0 / val_1",
}

PARAMS_CALCTAZ2: dict = {
    "min": 0,
    "max": 50,
    "val_1": "el_energie_gestern",
    "precision": 2,
    "icon": "mdi:sigma",
    "calculation": "val_0 / val_1",
}

PARAMS_CALCMAZ: dict = {
    "min": 0,
    "max": 50,
    "val_1": "el_energie_monat",
    "precision": 2,
    "stateclass": SensorStateClass.MEASUREMENT,
    "icon": "mdi:sigma",
    "calculation": "val_0 / val_1",
}

PARAMS_CALCJAZ: dict = {
    "min": 0,
    "max": 50,
    "denominator": "el_energie_jahr",
    "precision": 2,
    "stateclass": SensorStateClass.MEASUREMENT,
    "icon": "mdi:sigma",
}

PARAMS_ALERT: dict = {"icon": "mdi:alert"}

PARAMS_OPMODE: dict = {"icon": "mdi:heat-pump"}

PARAMS_PARTY: dict = {"icon": "mdi:glass-cocktail"}

PARAMS_TIME_H: dict = {"icon": "mdi:clock-time-eight", "unit": UnitOfTime.HOURS}


# pylint: disable=line-too-long

##############################################################################################################################
# Modbus Register List:                                                                                                      #
# https://docs.google.com/spreadsheets/d/1EZ3QgyB41xaXo4B5CfZe0Pi8KPwzIGzK/edit?gid=1730751621#gid=1730751621                #
##############################################################################################################################

# fmt: off
MODBUS_SYS_ITEMS: list[ModbusItem] = [
    ModbusItem( address=30001, name="Aussentemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_STDTEMP, translation_key="aussentemp"),
    ModbusItem( address=30002, name="Luftansaugtemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.SYS, params=PARAMS_STDTEMP, translation_key="luftansautgemp"),
    ModbusItem( address=30003, name="Fehler", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.SYS, resultlist=SYS_FEHLER, params=PARAMS_ALERT, translation_key="fehler"),
    ModbusItem( address=30004, name="Warnung", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.SYS, resultlist=SYS_FEHLER, params=PARAMS_ALERT, translation_key="warnung"), # same codes as for warnings
    ModbusItem( address=30005, name="Fehlerfrei", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.SYS, resultlist=SYS_FEHLERFREI, params=PARAMS_ALERT, translation_key="fehlerfrei"),
    ModbusItem( address=30006, name="Betriebsanzeige", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.SYS, resultlist=SYS_BETRIEBSANZEIGE, params = PARAMS_OPMODE, translation_key="betriebsanzeige"),
    ModbusItem( address=40001,  name="Systembetriebsart", mformat=FORMATS.STATUS, mtype=TYPES.SELECT, device=DEVICES.SYS, resultlist=SYS_BETRIEBSART, params = PARAMS_OPMODE, translation_key="sys_operationmode"),
]

MODBUS_WP_ITEMS: list[ModbusItem] = [
    ModbusItem( address=33101, name="Betrieb", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.WP, resultlist=HP_BETRIEB, params = PARAMS_OPMODE, translation_key="wp_betrieb"),
    ModbusItem( address=33102, name="Störmeldung", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.WP, resultlist=HP_STOERMELDUNG, params=PARAMS_ALERT, translation_key="wp_stoermeldung"),
    ModbusItem( address=33103, name="Leistungsanforderung", mformat=FORMATS.PERCENTAGE, mtype=TYPES.SENSOR, device=DEVICES.WP, params=PARAMS_PERCENTAGE,translation_key="leistungsanforderung"),
    ModbusItem( address=33103, name="Wärmeleistung", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR_CALC, device=DEVICES.WP, params=PARAMS_CALCPOWER, translation_key="waermeleistung"),
    ModbusItem( address=33104, name="Vorlauftemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WP, params=PARAMS_STDTEMP, translation_key="vl_temp"),
    ModbusItem( address=33105, name="Rücklauftemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR,  device=DEVICES.WP, params=PARAMS_STDTEMP, translation_key="rl_temp"),
    ModbusItem( address=33106, name="Verdampfungstemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WP, params=PARAMS_STDTEMP, translation_key="verdampfungs_temp"),
    ModbusItem( address=33107, name="Verdichtersauggastemp", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WP, params=PARAMS_STDTEMP, translation_key="verdichter_ansaug_gas_temp"),
    ModbusItem( address=33108, name="Weichentemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WP, params=PARAMS_STDTEMP, translation_key="weichen_temp"),
    ModbusItem( address=33109, name="Anforderung(Vorlauf regenerativ)", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WP, params=PARAMS_STDTEMP, translation_key="anforderung_vl_regenerativ"),
    ModbusItem( address=33110, name="Puffertemperatur?", mformat=FORMATS.UNKNOWN, mtype=TYPES.SENSOR, device=DEVICES.WP, params=PARAMS_STDTEMP, translation_key="puffer_temp"),
    ModbusItem( address=33111, name="Vorlauftemperatur präzise(Summenvorlauf(B7))", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WP, params=PARAMS_STDTEMP, translation_key="vl_praeziese_summenvorlauf_b7"),
    ModbusItem( address=33111, name="Spreizung", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR_CALC, device=DEVICES.WP, params=PARAMS_CALCSPREIZUNG, translation_key="spreizung"),

    ModbusItem( address=43101, name="Konfiguration", mformat=FORMATS.STATUS, mtype=TYPES.NUMBER_RO, device=DEVICES.WP, resultlist=HP_KONFIGURATION, params = PARAMS_OPMODE, translation_key="wp_konf"),
    ModbusItem( address=43102, name="Ruhemodus", mformat=FORMATS.STATUS, mtype=TYPES.NUMBER_RO, device=DEVICES.WP, resultlist=HP_RUHEMODUS, translation_key="ruhemodus"),
    ModbusItem( address=43103, name="Pumpe Einschaltart", mformat=FORMATS.NUMBER, mtype=TYPES.NUMBER_RO, device=DEVICES.WP, translation_key="pumpe_einschaltart"),
    ModbusItem( address=43104, name="Sollwert Pumpe Leistung Heizen", mformat=FORMATS.PERCENTAGE, mtype=TYPES.NUMBER_RO, device=DEVICES.WP, params=PARAMS_PERCENTAGE, translation_key="sollwert_pumpe_leistung_heizen"),
    ModbusItem( address=43105, name="Sollwert Pumpe Leistung Kühlen", mformat=FORMATS.PERCENTAGE, mtype=TYPES.NUMBER_RO, device=DEVICES.WP, params=PARAMS_PERCENTAGE, translation_key="sollwert_pumpe_leistung_kuehlen"),
    ModbusItem( address=43106, name="Sollwert Pumpe Leistung Warmwasser", mformat=FORMATS.PERCENTAGE, mtype=TYPES.NUMBER_RO, device=DEVICES.WP, params=PARAMS_PERCENTAGE, translation_key="sollwert_pumpe_leitung_ww"),
    ModbusItem( address=43107, name="Sollwert Pumpe Leistung Abtaubetrieb", mformat=FORMATS.PERCENTAGE, mtype=TYPES.NUMBER_RO, device=DEVICES.WP, params=PARAMS_PERCENTAGE, translation_key="sollwert_pumpe_leistung_abtau"),
    ModbusItem( address=43108, name="Sollwert Volumenstrom Heizen", mformat=FORMATS.NUMBER, mtype=TYPES.NUMBER_RO, device=DEVICES.WP, params=PARAMS_FLOWRATE, translation_key="soll_volumenstrom_heizen"),
    ModbusItem( address=43109, name="Sollwert Volumenstrom Kühlen", mformat=FORMATS.NUMBER, mtype=TYPES.NUMBER_RO,  device=DEVICES.WP, params=PARAMS_FLOWRATE, translation_key="soll_volumenstrom_kuehlen"),
    ModbusItem( address=43110, name="Sollwert Volumenstrom Warmwasser", mformat=FORMATS.NUMBER, mtype=TYPES.NUMBER_RO, device=DEVICES.WP, params=PARAMS_FLOWRATE, translation_key="soll_volumenstrom_ww"),
] # noqa: E501

MODBUS_HZ_ITEMS = [
    ModbusItem( address=31101, name="Raumsolltemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.HZ, params=PARAMS_ROOMTEMP, translation_key="raum_soll_temp"),
    ModbusItem( address=31102, name="Raumtemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.HZ, params=PARAMS_ROOMTEMP, translation_key="raum_temp"),
    ModbusItem( address=31103, name="Raumfeuchte", mformat=FORMATS.PERCENTAGE, mtype=TYPES.SENSOR, device=DEVICES.HZ, params=PARAMS_PERCENTAGE, translation_key="raum_feuchte"),
    ModbusItem( address=31104, name="Vorlaufsolltemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.HZ, params=PARAMS_STDTEMP, translation_key="hz_vl_solltemp"),
    ModbusItem( address=31105, name="HZ_Vorlauftemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.HZ, params=PARAMS_STDTEMP, translation_key="hz_vl_temp"),
    ModbusItem( address=31106, name="Adr. 31106", mformat=FORMATS.UNKNOWN, mtype=TYPES.SENSOR, device=DEVICES.HZ, translation_key="adr31106"),
    ModbusItem( address=41101, name="HZ_Konfiguration", mformat=FORMATS.STATUS, mtype=TYPES.NUMBER_RO, device=DEVICES.HZ, resultlist=HZ_KONFIGURATION, translation_key="hz_konf"),
    ModbusItem( address=41102, name="Anforderung Typ", mformat=FORMATS.STATUS, mtype=TYPES.NUMBER_RO, device=DEVICES.HZ, resultlist=HZ_ANFORDERUNG, translation_key="anf_typ"),
    ModbusItem( address=41103, name="Betriebsart", mformat=FORMATS.STATUS, mtype=TYPES.SELECT, device=DEVICES.HZ, resultlist=HZ_BETRIEBSART, translation_key="hz_operationmode"),
    ModbusItem( address=41104, name="Pause / Party", mformat=FORMATS.STATUS, mtype=TYPES.SELECT, device=DEVICES.HZ, resultlist=HZ_PARTY_PAUSE, params = PARAMS_PARTY, translation_key="party_pause"),
    ModbusItem( address=41105, name="Raumsolltemperatur Komfort", mformat=FORMATS.TEMPERATUR, mtype=TYPES.NUMBER, device=DEVICES.HZ, params=PARAMS_ROOMTEMP_HIGH, translation_key="raum_soll_temp_komf"),
    ModbusItem( address=41106, name="Raumsolltemperatur Normal", mformat=FORMATS.TEMPERATUR, mtype=TYPES.NUMBER, device=DEVICES.HZ, params=PARAMS_ROOMTEMP_MID, translation_key="raum_soll_temp_normal"),
    ModbusItem( address=41107, name="Raumsolltemperatur Absenk", mformat=FORMATS.TEMPERATUR, mtype=TYPES.NUMBER, device=DEVICES.HZ, params=PARAMS_ROOMTEMP_LOW, translation_key="raum_soll_temp_absenk"),
    ModbusItem( address=41108, name="Heizkennlinie", mformat=FORMATS.NUMBER, mtype=TYPES.NUMBER, device=DEVICES.HZ, params=PARAMS_HZKENNLINIE, translation_key="heizkennlinie"),
    ModbusItem( address=41109, name="Sommer Winter Umschaltung", mformat=FORMATS.TEMPERATUR, mtype=TYPES.NUMBER, device=DEVICES.HZ, params=PARAMS_ROOMTEMP, translation_key="so_wi_umschalt"),
    ModbusItem( address=41110, name="Heizen Konstanttemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.NUMBER_RO, device=DEVICES.HZ, params=PARAMS_ROOMTEMP, translation_key="heiz_konstanttemp"),
    ModbusItem( address=41111, name="Heizen Konstanttemp Absenk", mformat=FORMATS.TEMPERATUR, mtype=TYPES.NUMBER_RO, device=DEVICES.HZ, params=PARAMS_ROOMTEMP, translation_key="heiz_konstanttemp_absenk"),
    ModbusItem( address=41112, name="Kühlen Konstanttemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.NUMBER_RO, device=DEVICES.HZ, params=PARAMS_ROOMTEMP, translation_key="kuehl_konstanttemp"),
] # noqa: E501

# buils other Heizkreis Itemlists
MODBUS_HZ2_ITEMS: list = []
for item in MODBUS_HZ_ITEMS:
    mbi = copy.deepcopy(x=item)
    mbi.address = item.address+100
    mbi.name = item.name + "2"
    mbi.translation_key = item.translation_key + "2"
    mbi.device = DEVICES.HZ2
    MODBUS_HZ2_ITEMS.append(mbi)  # noqa: PERF401

# buils other Heizkreis Itemlists
MODBUS_HZ3_ITEMS: list = []
for item in MODBUS_HZ_ITEMS:
    mbi = copy.deepcopy(x=item)
    mbi.address = item.address+200
    mbi.name = item.name + "3"
    mbi.translation_key = item.translation_key + "3"
    mbi.device = DEVICES.HZ3
    MODBUS_HZ3_ITEMS.append(mbi)  # noqa: PERF401

# buils other Heizkreis Itemlists
MODBUS_HZ4_ITEMS: list = []
for item in MODBUS_HZ_ITEMS:
    mbi = copy.deepcopy(x=item)
    mbi.address = item.address+300
    mbi.name = item.name + "4"
    mbi.translation_key = item.translation_key + "4"
    mbi.device = DEVICES.HZ4
    MODBUS_HZ4_ITEMS.append(mbi)  # noqa: PERF401

# buils other Heizkreis Itemlists
MODBUS_HZ5_ITEMS: list = []
for item in MODBUS_HZ_ITEMS:
    mbi: ModbusItem = copy.deepcopy(x=item)
    mbi.address = item.address+400
    mbi.name = item.name + "5"
    mbi.translation_key = item.translation_key + "5"
    mbi.device = DEVICES.HZ5
    MODBUS_HZ5_ITEMS.append(mbi)  # noqa: PERF401

MODBUS_WW_ITEMS: list[ModbusItem] = [
    ModbusItem( address=32101, name="Warmwassersolltemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WW, params=PARAMS_WATERTEMP, translation_key="ww_soll_temp"),
    ModbusItem( address=32102, name="Warmwassertemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WW, params=PARAMS_WATERTEMP, translation_key="ww_temp"),
    ModbusItem( address=42101, name="WW_Konfiguration", mformat=FORMATS.STATUS, mtype=TYPES.NUMBER_RO, device=DEVICES.WW, resultlist=WW_KONFIGURATION, translation_key="ww_konf"),
    ModbusItem( address=42102, name="Warmwasser Push", mformat=FORMATS.STATUS, mtype=TYPES.SELECT, device=DEVICES.WW, resultlist=WW_PUSH, translation_key="ww_push"),
    ModbusItem( address=42103, name="Warmwasser Normal", mformat=FORMATS.TEMPERATUR, mtype=TYPES.NUMBER, device=DEVICES.WW, params=PARAMS_WATERTEMP_HIGH, translation_key="ww_normal"),
    ModbusItem( address=42104, name="Warmwasser Absenk", mformat=FORMATS.TEMPERATUR, mtype=TYPES.NUMBER, device=DEVICES.WW, params=PARAMS_WATERTEMP_LOW, translation_key="ww_absenk"),
    ModbusItem( address=42105, name="SG Ready Anhebung", mformat=FORMATS.TEMPERATUR, mtype=TYPES.NUMBER, device=DEVICES.WW, params=PARAMS_SGREADYTEMP, translation_key="sgr_anhebung"),
] # noqa: E501

MODBUS_W2_ITEMS: list[ModbusItem] = [
    ModbusItem( address=34101, name="Status 2. WEZ", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.W2, resultlist=W2_STATUS, translation_key="status_2_wez"),
    ModbusItem( address=34102, name="Schaltspiele E-Heizung 1", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.W2, translation_key="schaltsp_e1"),
    ModbusItem( address=34103, name="Betriebsstunden E1", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.W2,params = PARAMS_TIME_H, translation_key="betriebss_e1"),
    ModbusItem( address=34104, name="Status E-Heizung 1", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.W2, resultlist=W2_STATUS, translation_key="status_e1"),
    ModbusItem( address=34105, name="Status E-Heizung 2", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.W2, resultlist=W2_STATUS, translation_key="status_e2"),
    ModbusItem( address=34106, name="Schaltspiele E-Heizung 2", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.W2, translation_key="schaltsp_e2"),
    ModbusItem( address=34107, name="Betriebsstunden E2", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.W2, params = PARAMS_TIME_H, translation_key="betriebss_e2"),
    ModbusItem( address=44101, name="W2_Konfiguration", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.W2, resultlist=W2_KONFIG, translation_key="w2_konf"),
    ModbusItem( address=44102, name="Konfiguration EP1", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.W2, resultlist=EP1_KONFIG, translation_key="adr44102"),
    ModbusItem( address=44103, name="Konfiguration EP2", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.W2, resultlist=EP2_KONFIG, translation_key="adr44103"),
    ModbusItem( address=44104, name="Grenztemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.NUMBER, device=DEVICES.W2, params=PARAMS_BIVALENZTEMP, translation_key="grenztemp"),
    ModbusItem( address=44105, name="Bivalenztemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.NUMBER, device=DEVICES.W2, params=PARAMS_BIVALENZTEMP, translation_key="bivalenztemp"),
    ModbusItem( address=44106, name="Bivalenztemperatur WW", mformat=FORMATS.TEMPERATUR, mtype=TYPES.NUMBER, device=DEVICES.W2, params=PARAMS_BIVALENZTEMP, translation_key="bivalenztemp_ww"),
] # noqa: E501

MODBUS_ST_ITEMS: list[ModbusItem] = [
    ModbusItem( address=36101, name="Gesamt Energie heute", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="ges_energie_heute"),
    ModbusItem( address=36101, name="Tagesarbeitszahl heute", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR_CALC, device=DEVICES.ST, params=PARAMS_CALCTAZ, translation_key="tagesarbeitszahl_heute"),
    ModbusItem( address=36102, name="Gesamt Energie gestern", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="ges_energie_yesterday"),
    ModbusItem( address=36102, name="Tagesarbeitszahl gestern", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR_CALC, device=DEVICES.ST, params=PARAMS_CALCTAZ2, translation_key="tagesarbeitszahl_gestern"),
    ModbusItem( address=36103, name="Gesamt Energie Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="ges_energie_monat"),
    ModbusItem( address=36103, name="Monatsarbeitszahl", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR_CALC, device=DEVICES.ST, params=PARAMS_CALCMAZ, translation_key="monatsarbeitszahl"),
    ModbusItem( address=36104, name="Gesamt Energie Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="ges_energie_jahr"),
    ModbusItem( address=36104, name="Jahresarbeitszahl", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR_CALC, device=DEVICES.ST, params=PARAMS_CALCJAZ, translation_key="jahresarbeitszahl"),
    ModbusItem( address=36201, name="Heizen Energie heute", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="heiz_energie_heute"),
    ModbusItem( address=36202, name="Heizen Energie gestern", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="heiz_energie_getern"),
    ModbusItem( address=36203, name="Heizen Energie Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="heiz_energie_monat"),
    ModbusItem( address=36204, name="Heizen Energie Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="heiz_energie_jahr"),
    ModbusItem( address=36301, name="Warmwasser Energie heute", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="ww_energie_heute"),
    ModbusItem( address=36302, name="Warmwasser Energie gestern", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="ww_energie_gestern"),
    ModbusItem( address=36303, name="Warmwasser Energie Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="ww_energie_monat"),
    ModbusItem( address=36304, name="Warmwasser Energie Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="ww_energie_jahr"),
    ModbusItem( address=36401, name="Kühlen Energie heute", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="kuehl_energie_heute"),
    ModbusItem( address=36402, name="Kühlen Energie gestern", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="kuehl_energie_gestern"),
    ModbusItem( address=36403, name="Kühlen Energie Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="kuehl_energie_monat"),
    ModbusItem( address=36404, name="Kühlen Energie Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="kuehl_energie_jahr"),
    ModbusItem( address=36501, name="Abtauen Energie heute", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="abtau_energie_heute"),
    ModbusItem( address=36502, name="Abtauen Energie gestern", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY,translation_key="abtau_energie_gester"),
    ModbusItem( address=36503, name="Abtauen Energie Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="abtau_energie_monat"),
    ModbusItem( address=36504, name="Abtauen Energie Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="abtau_energie_jahr"),
    ModbusItem( address=36601, name="Gesamt Energie II heute", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="ges_energie_today"),
    ModbusItem( address=36602, name="Gesamt Energie II gestern", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="ges_energie_2_yesterday"),
    ModbusItem( address=36603, name="Gesamt Energie II Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="ges_energie_2_monat"),
    ModbusItem( address=36604, name="Gesamt Energie II Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="ges_energie_year"),
    ModbusItem( address=36701, name="Elektr. Energie heute", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="el_energie_heute"),
    ModbusItem( address=36702, name="Elektr. Energie gestern", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="el_energie_gestern"),
    ModbusItem( address=36703, name="Elektr. Energie Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="el_energie_monat"),
    ModbusItem( address=36704, name="Elektr. Energie Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.ST, params=PARAMS_ENERGY, translation_key="el_energie_jahr"),
    ModbusItem( address=36801, name="Adr. 36801", mformat=FORMATS.UNKNOWN, mtype=TYPES.SENSOR, device=DEVICES.ST, translation_key="adr36801"),
]


MODBUS_IO_ITEMS: list[ModbusItem] = [
    ModbusItem( address=35101, name="SG-Ready 1", mformat=FORMATS.UNKNOWN, mtype=TYPES.SENSOR, device=DEVICES.IO, translation_key="sgr1"),
    ModbusItem( address=35102, name="SG-Ready 2", mformat=FORMATS.UNKNOWN, mtype=TYPES.SENSOR, device=DEVICES.IO, translation_key="sgr2"),
    ModbusItem( address=35103, name="Ausgang H1.2", mformat=FORMATS.UNKNOWN, mtype=TYPES.SENSOR, device=DEVICES.IO, translation_key="ausg_h12"),
    ModbusItem( address=35104, name="Ausgang H1.3", mformat=FORMATS.UNKNOWN, mtype=TYPES.SENSOR, device=DEVICES.IO, translation_key="ausg_h13"),
    ModbusItem( address=35105, name="Ausgang H1.4", mformat=FORMATS.UNKNOWN, mtype=TYPES.SENSOR, device=DEVICES.IO, translation_key="ausg_h14"),
    ModbusItem( address=35106, name="Ausgang H1.5", mformat=FORMATS.UNKNOWN, mtype=TYPES.SENSOR, device=DEVICES.IO, translation_key="ausg_h15"),
    ModbusItem( address=35107, name="Eingang DE1", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.IO, resultlist=W2_STATUS, translation_key="eing_de1"),
    ModbusItem( address=35108, name="Eingang DE2", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.IO, resultlist=W2_STATUS, translation_key="eing_de2"),

    ModbusItem( address=45101, name="Konf. Eingang SGR1", mformat=FORMATS.STATUS, mtype=TYPES.NUMBER_RO, device=DEVICES.IO, resultlist=IO_KONFIG_IN, translation_key="konf_eing_sgr1"),
    ModbusItem( address=45102, name="Konf. Eingang SGR2", mformat=FORMATS.STATUS, mtype=TYPES.NUMBER_RO, device=DEVICES.IO, resultlist=IO_KONFIG_IN, translation_key="konf_eing_sgr2"),
    ModbusItem( address=45103, name="Konf. Ausgang H1.2", mformat=FORMATS.STATUS, mtype=TYPES.NUMBER_RO, device=DEVICES.IO, resultlist=IO_KONFIG, translation_key="konf_ausg_h12"),
    ModbusItem( address=45104, name="Konf. Ausgang  H1.3", mformat=FORMATS.STATUS, mtype=TYPES.NUMBER_RO, device=DEVICES.IO, resultlist=IO_KONFIG, translation_key="konf_ausg_h13"),
    ModbusItem( address=45105, name="Konf. Ausgang  H1.4", mformat=FORMATS.STATUS, mtype=TYPES.NUMBER_RO, device=DEVICES.IO, resultlist=IO_KONFIG, translation_key="konf_ausg_h14"),
    ModbusItem( address=45106, name="Konf. Ausgang  H1.5", mformat=FORMATS.STATUS, mtype=TYPES.NUMBER_RO, device=DEVICES.IO, resultlist=IO_KONFIG, translation_key="konf_ausg_h15"),
    ModbusItem( address=45107, name="Konf. Eingang DE1", mformat=FORMATS.STATUS, mtype=TYPES.NUMBER_RO, device=DEVICES.IO, resultlist=IO_KONFIG_IN, translation_key="konf_eing_de1"),
    ModbusItem( address=45108, name="Konf. Eingang DE2", mformat=FORMATS.STATUS, mtype=TYPES.NUMBER_RO, device=DEVICES.IO, resultlist=IO_KONFIG_IN, translation_key="konf_eing_de2"),
]


WEBIF_INFO_HEIZKREIS1: list[WebItem] = [
    WebItem(name="Außentemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIH, params=PARAMS_STDTEMP, webif_group="WIH", translation_key="webif_info_heizkreis1_aussentemperatur"),
    WebItem(name="AT Mittelwert", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIH, params=PARAMS_STDTEMP, webif_group="WIH", translation_key="webif_info_heizkreis1_at_mittelwert"),
    WebItem(name="AT Langzeitwert", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIH, params=PARAMS_STDTEMP, webif_group="WIH", translation_key="webif_info_heizkreis1_at_langzeitwert"),
    WebItem(name="Raumsolltemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIH, params=PARAMS_STDTEMP, webif_group="WIH", translation_key="webif_info_heizkreis1_raumsolltemperatur"),
    WebItem(name="Vorlaufsolltemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIH, params=PARAMS_STDTEMP, webif_group="WIH", translation_key="webif_info_heizkreis1_vorlaufsolltemperatur"),
    WebItem(name="Vorlauftemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIH, params=PARAMS_STDTEMP, webif_group="WIH", translation_key="webif_info_heizkreis1_vorlauftemperatur"),
]

WEBIF_INFO_WAERMEPUMPE: list[WebItem] = [
    WebItem(name="Betrieb", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_betrieb"),
    WebItem(name="Störmeldung", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_stoermeldung"),
    WebItem(name="Warmwassertemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_warmwassertemperatur"),
    WebItem(name="Leistungsanforderung", mformat=FORMATS.PERCENTAGE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_PERCENTAGE, webif_group="WIW", translation_key="webif_info_waermepumpe_leistungsanforderung"),
    WebItem(name="Solltemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_solltemperatur"),
    WebItem(name="Schaltdifferenz dynamisch", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_DELTA_T, webif_group="WIW", translation_key="webif_info_waermepumpe_schaltdifferenz_dynamisch"),
    WebItem(name="Vorlauftemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_vorlauftemperatur"),
    WebItem(name="Rücklauftemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_ruecklauftemperatur"),
    WebItem(name="Drehzahl Pumpe M1", mformat=FORMATS.PERCENTAGE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_PERCENTAGE, webif_group="WIW", translation_key="webif_info_waermepumpe_drehzahl_pumpe_m1"),
    WebItem(name="Volumenstrom", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_FLOWRATE, webif_group="WIW", translation_key="webif_info_waermepumpe_volumenstrom"),
    WebItem(name="Stellung Umschaltventil", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_stellung_umschaltventil"),
    WebItem(name="Version WWP-SG", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_version_wwpsg"),
    WebItem(name="Version WWP-EC WBB", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_version_wwpecwbb"),
    WebItem(name="Soll Leistung", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_ENERGY_WEBIF, webif_group="WIW", translation_key="webif_info_waermepumpe_soll_leistung"),
    WebItem(name="Ist Leistung", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_ENERGY_WEBIF, webif_group="WIW", translation_key="webif_info_waermepumpe_ist_leistung"),
    WebItem(name="Expansionsventil AG Eintr", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_expansionsventil_ag_eintr"),
    WebItem(name="Luftansaugtemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_luftansaugtemperatur"),
    WebItem(name="Wärmetauscher AG Austrit", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_waermetauscher_ag_austritt"),
    WebItem(name="Verdichtersauggastemp.", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_verdichter_ansauggasstemp"),
    WebItem(name="EVI Sauggastemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_evi_sauggastemperatur"),
    WebItem(name="Kältemittel IG Austritt", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_kaeltemittel_ig_austritt"),
    WebItem(name="Ölsumpftemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_oelsumpftemperatur"),
    WebItem(name="Druckgastemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_druckgastemperatur"),
    WebItem(name="Niederdruck", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDPRESSURE, webif_group="WIW", translation_key="webif_info_waermepumpe_niederdruck"),
    WebItem(name="Verdampfungstemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_verdampfungs_temp"),
    WebItem(name="Hochdruck", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDPRESSURE, webif_group="WIW", translation_key="webif_info_waermepumpe_hochdruck"),
    WebItem(name="Kondensationstemperatur", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_kondensationstemperatur"),
    WebItem(name="Mitteldruck", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDPRESSURE, webif_group="WIW", translation_key="webif_info_waermepumpe_mitteldruck"),
    WebItem(name="Sättigungstemperatur EVI", mformat=FORMATS.TEMPERATUR, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_saettigungstemp_evi"),
    WebItem(name="Überhitzung Heizen", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_DELTA_T, webif_group="WIW", translation_key="webif_info_waermepumpe_ueberhitzung_heizen"),
    WebItem(name="Öffnungsgrad EXV Heizen", mformat=FORMATS.PERCENTAGE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_PERCENTAGE, webif_group="WIW", translation_key="webif_info_waermepumpe_oeffnungsgrad_exv_heizen"),
    WebItem(name="Überhitzung Verdichter", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_DELTA_T, webif_group="WIW", translation_key="webif_info_waermepumpe_ueberhitzung_verdichter"),
    WebItem(name="Öffnungsgrad EXV Kühlen", mformat=FORMATS.PERCENTAGE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_PERCENTAGE, webif_group="WIW", translation_key="webif_info_waermepumpe_oeffnungsgrad_exv_kuehlen"),
    WebItem(name="Überhitzung EVI", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_DELTA_T, webif_group="WIW", translation_key="webif_info_waermepumpe_ueberhitzung_evi"),
    WebItem(name="Öffnungsgrad EVI", mformat=FORMATS.PERCENTAGE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_PERCENTAGE, webif_group="WIW", translation_key="webif_info_waermepumpe_oeffnungsgrad_evi"),
    WebItem(name="Betriebsstd. Verdichter", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_TIME_H, webif_group="WIW", translation_key="webif_info_waermepumpe_betriebsstund_verdichter"),
    WebItem(name="Schaltspiele Verdichter", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_schaltspiele_verdichter"),
    WebItem(name="Schaltspiele Abtauen", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_schaltspiele_abtauen"),
    WebItem(name="Verdichter", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDPRPM, webif_group="WIW", translation_key="webif_info_waermepumpe_verdichter"),
    WebItem(name="Außengerät Variante", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_aussengeraet_variante"),

 ]

WEBIF_INFO_2WEZ = [
        WebItem(name="Status", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.WI2, webif_group="WI2", translation_key="webif_info_2wez_status"),
        WebItem(name="Status E-Heizung 1", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.WI2, webif_group="WI2", translation_key="webif_info_2wez_status_eheizung"),
        WebItem(name="Status E-Heizung 2", mformat=FORMATS.STATUS, mtype=TYPES.SENSOR, device=DEVICES.WI2, webif_group="WI2", translation_key="webif_info_2wez_status_eheizung2"),
        WebItem(name="Betriebsstunden E1", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WI2,params = PARAMS_TIME_H, webif_group="WI2", translation_key="webif_info_2wez_betriebsstunden_e1"),
        WebItem(name="Betriebsstunden E2", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WI2,params = PARAMS_TIME_H, webif_group="WI2", translation_key="webif_info_2wez_betriebsstunden_e2"),
        WebItem(name="Schaltspiele E1", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WI2, webif_group="WI2", translation_key="webif_info_2wez_schaltspiele_e1"),
        WebItem(name="Schaltspiele E2", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WI2, webif_group="WI2", translation_key="webif_info_2wez_schaltspiele_e2"),
]

WEBIF_INFO_STATISTIK = [
            WebItem(name="th. Energie Heizen Tag", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_heizen_tag"),
            WebItem(name="th. Energie WW Tag", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_ww_tag"),
            WebItem(name="th. Energie gesamt Tag", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_gesamt_tag"),
            WebItem(name="elektrische Energie Tag", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_elektrische_energie_tag"),
            WebItem(name="th. Energie Heizen Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_heizen_monat"),
            WebItem(name="th. Energie WW Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_ww_monat"),
            WebItem(name="th. Energie gesamt Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_gesamt_monat"),
            WebItem(name="elektrische Energie Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_elektrische_energie_monat"),
            WebItem(name="th. Energie Heizen Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_heizen_jahr"),
            WebItem(name="th. Energie WW Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_ww_jahr"),
            WebItem(name="th. Energie gesamt Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_ges_jahr"),
            WebItem(name="elektrische Energie Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_elektrische_energie_jahr"),

]

WEBIF_ITEMS = WEBIF_INFO_HEIZKREIS1 + WEBIF_INFO_WAERMEPUMPE + WEBIF_INFO_2WEZ + WEBIF_INFO_STATISTIK

DEVICELISTS: list = [
    MODBUS_SYS_ITEMS,
    MODBUS_WP_ITEMS,
    MODBUS_WW_ITEMS,
    MODBUS_HZ_ITEMS,
    MODBUS_HZ2_ITEMS,
    MODBUS_HZ3_ITEMS,
    MODBUS_HZ4_ITEMS,
    MODBUS_HZ5_ITEMS,
    MODBUS_W2_ITEMS,
    MODBUS_ST_ITEMS,
    MODBUS_IO_ITEMS
]

# fmt: on
