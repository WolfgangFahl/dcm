# 
# Portofolio Plus Dynamic Competence Map
# 
# https://github.com/WolfgangFahl/dcm
# 
name: PortfolioPlus
id: portfolio_plus
lookup_url: http://dcm.bitplan.com
url: https://www.greta-die.de/webpages/projektergebnisse/portfolioplus
description: Online-Tool, mit dem Lehrende ihre oftmals informell und non-formal
  erworbenen pädagogischen Kompetenzen strukturiert identifizieren, dokumentieren
  und von dafür geschulten GRETA-Gutachterinnen und GRETA-Gutachtern begutachten
  lassen können.
element_names:
  tree: Kompetenzbilanz
  aspect: Kompetenzaspekt
  facet: Kompetenzfacette
  level: Lernfortschritt
aspects:
- id: BPWK
  name: Berufspraktisches Wissen und Können
  color_code: '#B5B0A8'
  areas:
    - name: Didaktik und Methodik
      facets:
        - name: Lerninhalte und -ziele
          id: learning_content_and_goals
          description: |
              **Kompetenzanforderungen**:
        
                - Festlegung und Formulierung von Lerninhalten und -zielen
                - Kritische Prüfung und Bewertung von Lerninhalten
                - Kritische Prüfung und Bewertung der (digitalen) Informationskanäle und -quellen bei der Erschließung von Lerninhalten
                - Ausrichtung der Lerninhalte und -ziele an den Teilnehmenden
                - Dialogische Erarbeitung von Lerninhalten und -zielen mit den Teilnehmenden
        - name: Methoden, Medien und Lernmaterialien
          id: methods_media_and_learn_materials
          description: |
             **Kompetenzanforderungen**:
             
                - Reflektierte und kritische Auswahl, Nutzung und Gestaltung geeigneter Methoden, (digitaler) Medien und Lernmaterialien
                - Ausrichtung der Methoden, (digitaler) Medien und Lernmaterialien an Lernzielen, Lerninhalten, Teilnehmenden und Lernsettings
                - Berücksichtigung urheber-, datenschutzrechtlicher sowie medienethischer Aspekte bei der Auswahl, Nutzung und Gestaltung von Methoden, (digitalen) Medien und Lernmaterialien
                - Evaluation der im Lehr-Lern-Angebot eingesetzten Methoden, (digitalen) Medien und Lernmaterialien
                - Nutzung von (digitalen) Tools/Werkzeugen zur Evaluation des Lehr-Lern-Angebots
             
        - name: Rahmenbedingungen und Lernumgebungen
        - name: Outcomeorientierung
    - name: Beratung/Individualisierte Lernunterstützung
      facets:
        - name: Teilnehmendenorientierung
        - name: Diagnostik und Lernberatung
        - name: Moderation und Steuerung von Gruppen
        - name: Professionelle Kommunikation
        - name: Kooperation mit den Auftraggebenden/Arbeitgebenden
          id: cooperation_with_client
        - name: Kollegiale Zusammenarbeit/Netzwerken
          id: cooperation_and_networking'
- id: FFW
  name: Fach- und feldspezifisches Wissen
  color_code: '#D1CFC7'
  areas:
    -name: Feldbezug
    facets:
        - name: Adressatinnen und Adressaten
        - name: Feldspezifisches Wissen
        - name: Curriculare und institutionelle Rahmenbedingungen'
- id: PWAU
  name: Professionelle Werthaltungen und Überzeugungen
  color_code: '#EBE8E5'
  areas:
    - name: Berufsethos
      facets:
        - name: Menschenbilder
        - name: Wertvorstellungen
    - name: Berufsbezogene Überzeugungen
      facets:
        - name: Eigenes Rollenbewusstsein
        - name: Subjektive Annahmen über das Lehren und Lernen
- id: PSS
  name: Professionelle Selbststeuerung
  color_code: '#918F82'
  areas:
    - name: Motivationale Orientierungen
      facets:
        - name: Selbstwirksamkeitsüberzeugungen
        - name: Enthusiasmus
          id: enthusiasm
          description: |
            **Kompetenzanforderungen**:
            
              - Freude an der Ausübung der eigenen Tätigkeit und dem Fach.
              - Bewusstsein über die Bedeutung des persönlichen 
                Engagements und der Begeisterungsfähigkeit für 
                das eigene professionelle Lehrhandeln.
           
    - name: Berufspraktische Erfahrung
      facets:
        - name: Reflexion des eigenen Lehrhandelns
        - name: Berufliche Weiterenticklung
    - name: Selbstregulation
      facets:
        - name: Umgang mit Feedback und Kritik
          description: |
            **Kompetenzanforderungen**:
            
              - Professionelle und konstruktive Reaktion auf Kritik und Feedback.
              - Ermöglichung von Zeiträumen und Orten zum Lösen von Problemen und Konflikten.
              - Berücksichtigung des Mediums, durch welches Feedback kommuniziert wird.
        - name: Engagement und Distanz
levels:
- name: Basisstufe
  level: 1
  color_code: '#9FB429'
- name: Ausbaustufe
  level: 2
  color_code: '#0079C3'
- name: Nicht erfasst
  level: 3
  color_code: '#C3E3F2'
