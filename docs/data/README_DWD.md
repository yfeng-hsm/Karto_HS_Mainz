# DWD-Winddaten für die Fälle 2–4

Echte stündliche Stationswerte vom **28.10.2026, 12:00 UTC (13:00 MEZ)**. Abgerufen am 30.10.2026. Keine Live-Daten und keine Vorhersage.

- Quelle: DWD Climate Data Center, *Hourly mean value from station observations of wind speed and wind direction for Germany*, Version v24.03.
- [Originalarchive je Station](https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/wind/recent/)
- [Stationsmetadaten](https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/wind/recent/FF_Stundenwerte_Beschreibung_Stationen.txt)
- [DWD-Dokumentation mit Lizenz und Qualitätshinweisen](https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/hourly/wind/DESCRIPTION_obsgermany_climate_hourly_wind_en.pdf)
- Lizenz gemäß dieser Dokumentation: **CC BY 4.0**, © Deutscher Wetterdienst. Kein Anspruch auf Vollständigkeit der Qualitätssicherung: `recent` enthält vorläufige Daten. QN_3 ist in JSON/CSV erhalten.

Auswahl: die 26 nächstgelegenen, bis mindestens 28.10.2026 aktiven Windstationen innerhalb von 155 km um Mainz (Referenz 50.00° N, 8.27° E). Stationspositionen und IDs sind in `wind_stations.json` archiviert. Nur identische Beobachtungsstunden mit gültiger Richtung und positiver Geschwindigkeit werden verwendet. Keine Interpolation zwischen Stationen; Gelände, Messhöhe und Standortbedingungen können die Vergleichbarkeit beeinflussen.

Originalfelder: F = Windgeschwindigkeit in m/s; D = meteorologische Windherkunft, Grad im Uhrzeigersinn ab Nord; QN_3 = Qualitätskennzahl. D=360 bezeichnet Nord. -999 wird nicht gezeichnet; Windstille erhält keinen Richtungspfeil. Der Kartenpfeil zeigt die Zielrichtung der Luft: **(D + 180) mod 360**. Beispiel: Wind aus 330° → Luft strömt nach 150°.

Fall 2 verwendet abgeleitete ordinale Stufen: I <2, II 2–<4, III 4–<6, IV ≥6 m/s. Dies ist eine **didaktische Einteilung, keine DWD-Warnstufe und keine Beaufort-Skala**. Fall 3 verwendet die ursprünglichen Zahlenwerte. Die Fläche proportionaler Symbole ist proportional zu F. Fall 4 verwendet die Richtungsinformation; optional kann F zusätzlich die Fläche eines Pfeils steuern.

Die Daten sind für den Unterricht auf diesen Zeitpunkt eingefroren. `dwd_wind_snapshot.csv` enthält die verwendeten Zahlen; `wind.json` enthält zusätzlich Kartengeometrien und Quellenlinks. `tools/build_wind_data.py` reproduziert den Snapshot, solange die Stunde noch im rollierenden recent-Archiv vorhanden ist. Benötigt: `pyshp`, `shapely`.

Hintergrund: Natural Earth, Public Domain; [Bundesländer 1:10 Mio.](https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_1_states_provinces.zip), [Flüsse 1:50 Mio.](https://naturalearth.s3.amazonaws.com/50m_physical/ne_50m_rivers_lake_centerlines.zip). Für diese Übersicht vereinfacht, keine lokalen Vermessungsdaten.
