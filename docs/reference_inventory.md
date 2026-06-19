# IRISv2 Reference Workbook Inventory

Generated at: 2026-06-17T10:11:41
Reference directory: `data\reference`

This report profiles the official reference workbooks only. It does not write to PostgreSQL or change warehouse tables.

## fichierStagiaire.xlsx / GRNTSINI 

- file_name: `fichierStagiaire.xlsx`
- sheet_name: `GRNTSINI `
- row_count: `1838`
- column_count: `5`

### Columns

- `CODPROD`
- `CODFORMU`
- `GRNTSINI`
- `CODGRNT`
- `LIBGRNSIN`

### First 5 Rows

```text
CODPROD CODFORMU GRNTSINI CODGRNT                 LIBGRNSIN
    521        1      ASR     CAS        Avance sur recours
    521        1       BG      BG             BRIS DE GLACE
    521        1      CAS     CAS Contre assurance spéciale
    521        1      CAT     CAT           CATAS.NATURELLE
    521        1     CONS      RC              CONSIGNATION
```

### Null Counts For Key-Like Columns

- CODPROD: 0
- CODFORMU: 0
- GRNTSINI: 0
- CODGRNT: 0

### Candidate Key Duplicate Checks

- CODPROD + CODFORMU + GRNTSINI: complete_key_rows=1838, incomplete_key_rows=0, duplicate_row_count=0, duplicate_group_count=0

## fichierStagiaire.xlsx / CODPROD 

- file_name: `fichierStagiaire.xlsx`
- sheet_name: `CODPROD `
- row_count: `103`
- column_count: `3`

### Columns

- `CODPROD`
- `CODFORMU`
- `LIBFORMU`

### First 5 Rows

```text
CODPROD CODFORMU                              LIBFORMU
    521        1                AFFAIRES ET PROMENADES
    521        2                        PERSONNELS AMI
    521        3          PROMENADES ET AFFAIRES (Eve)
    521        4         AFFAIRES ET PROMENADE BASIQUE
    521        5 CONVENTION VERMEG SOPHRA ET UMA (AM1)
```

### Null Counts For Key-Like Columns

- CODPROD: 0
- CODFORMU: 0

### Candidate Key Duplicate Checks

- CODPROD + CODFORMU: complete_key_rows=103, incomplete_key_rows=0, duplicate_row_count=0, duplicate_group_count=0

## fichierStagiaire.xlsx / CODFAM

- file_name: `fichierStagiaire.xlsx`
- sheet_name: `CODFAM`
- row_count: `7`
- column_count: `2`

### Columns

- `CODFAM`
- `LIBFAMIL`

### First 5 Rows

```text
CODFAM         LIBFAMIL
     1         INCENDIE
     2        TRANSPORT
     3   RISQUES DIVERS
     4 RISQUES SPECIAUX
     5       AUTOMOBILE
```

### Null Counts For Key-Like Columns

- CODFAM: 0

### Candidate Key Duplicate Checks

- CODFAM: complete_key_rows=7, incomplete_key_rows=0, duplicate_row_count=0, duplicate_group_count=0

## fichierStagiaire.xlsx / SOUSNATSIN

- file_name: `fichierStagiaire.xlsx`
- sheet_name: `SOUSNATSIN`
- row_count: `31`
- column_count: `4`

### Columns

- `CODFAM`
- `CAUSESINI`
- `SOUNATSIN`
- `LIBSOUNAT`

### First 5 Rows

```text
CODFAM CAUSESINI SOUNATSIN          LIBSOUNAT
     5         2         1 DOMMAGE AVEC TIERS
     5         2         2 DOMMAGE SANS TIERS
     5        11         0                   
     5        15         1               STEG
     5        15         2              SONED
```

### Null Counts For Key-Like Columns

- CODFAM: 0
- CAUSESINI: 0
- SOUNATSIN: 0

### Candidate Key Duplicate Checks

- CODFAM + CAUSESINI + SOUNATSIN: complete_key_rows=31, incomplete_key_rows=0, duplicate_row_count=0, duplicate_group_count=0

## fichierStagiaire.xlsx / Délégation 

- file_name: `fichierStagiaire.xlsx`
- sheet_name: `Délégation `
- row_count: `5`
- column_count: `2`

### Columns

- `CODDELEGA`
- `LIBDELEGA`

### First 5 Rows

```text
CODDELEGA LIBDELEGA
        1          
        2          
        3          
        4          
        5          
```

### Null Counts For Key-Like Columns

- CODDELEGA: 0

### Candidate Key Duplicate Checks

- CODDELEGA: complete_key_rows=5, incomplete_key_rows=0, duplicate_row_count=0, duplicate_group_count=0

## PR01.xlsx / Sheet1

- file_name: `PR01.xlsx`
- sheet_name: `Sheet1`
- row_count: `300`
- column_count: `4`

### Columns

- `NATINT`
- `IDINT`
- `LOCAL`
- `UPDATE_IDENT`

### First 5 Rows

```text
NATINT IDINT   LOCAL UPDATE_IDENT
    AG    10  NABEUL            0
    AG   100   TUNIS            0
    AG   101   TUNIS            0
    AG   103 EL FAHS            0
    AG   106   TUNIS            0
```

### Null Counts For Key-Like Columns

- NATINT: 0
- IDINT: 0

### Candidate Key Duplicate Checks

- NATINT + IDINT: complete_key_rows=300, incomplete_key_rows=0, duplicate_row_count=0, duplicate_group_count=0

## PE033.xlsx / Sheet1

- file_name: `PE033.xlsx`
- sheet_name: `Sheet1`
- row_count: `44`
- column_count: `4`

### Columns

- `CNAT`
- `CLASSPERS`
- `LIBELLE`
- `UPDATE_IDENT`

### First 5 Rows

```text
CNAT CLASSPERS                                 LIBELLE UPDATE_IDENT
  AG        IN                                   Agent            0
  AP        IN                    Apporteur d'affaires            0
  AS        AS                                  ASSURE            0
  AV        AV                                  AVOCAT            0
  BK        OF Banque Ordonnancement Chèque AMI Assur.            0
```

### Null Counts For Key-Like Columns

- CNAT: 1
- CLASSPERS: 1

### Candidate Key Duplicate Checks

- CNAT: complete_key_rows=43, incomplete_key_rows=1, duplicate_row_count=0, duplicate_group_count=0

## PE02.xlsx / Sheet1

- file_name: `PE02.xlsx`
- sheet_name: `Sheet1`
- row_count: `24`
- column_count: `10`

### Columns

- `CLASSPERS`
- `LIBELLE`
- `TYPENUM`
- `EXISTE`
- `FNCTAJT`
- `FNCTMDF`
- `FNCTCST`
- `NATCLASS`
- `NATCPTE`
- `UPDATE_IDENT`

### First 5 Rows

```text
CLASSPERS               LIBELLE TYPENUM EXISTE FNCTAJT FNCTMDF FNCTCST NATCLASS NATCPTE UPDATE_IDENT
       AS                ASSURE       A      N                                D       F            1
       CA CAMPAGNIE D'ASSURANCE       M      N                                M       F            0
       CL          SOUSCRIPTEUR       A      N                                D       F            1
       CN            CONVENTION       M      Y AJTCONV MODCONV CLTCONV        M       F            5
       DL            DELEGATION       M      N  AJTINT                        M       F            0
```

### Null Counts For Key-Like Columns

- CLASSPERS: 0
- NATCLASS: 1
- NATCPTE: 1

### Candidate Key Duplicate Checks

- CLASSPERS: complete_key_rows=24, incomplete_key_rows=0, duplicate_row_count=0, duplicate_group_count=0

## PE01.xlsx / Sheet1

- file_name: `PE01.xlsx`
- sheet_name: `Sheet1`
- row_count: `349`
- column_count: `4`

### Columns

- `TABLE`
- `CODE`
- `LIBELLE`
- `UPDATE_IDENT`

### First 5 Rows

```text
    TABLE CODE                        LIBELLE UPDATE_IDENT
CATEGORIE    1                      SUCCURSAL            0
CATEGORIE    4                          AGENT            0
   ETATIN    A                       ACTIVITE            0
   ETATIN    S                       SUSPENDU            0
 FORMJURI  GIE groupement d'intérêt économiqu            0
```

### Null Counts For Key-Like Columns

- TABLE: 0
- CODE: 1

### Candidate Key Duplicate Checks

- TABLE + CODE: complete_key_rows=348, incomplete_key_rows=1, duplicate_row_count=0, duplicate_group_count=0

## SI001.xlsx / Sheet1

- file_name: `SI001.xlsx`
- sheet_name: `Sheet1`
- row_count: `46`
- column_count: `11`

### Columns

- `CODFAM`
- `CAUSESINI`
- `LIBCAUSE`
- `NATSINI`
- `RESPONSA`
- `INFOTIER`
- `RESPXY`
- `OBGSOUNAT`
- `GRNTSINI`
- `GENREEVAL`
- `UPDATE_IDENT`

### First 5 Rows

```text
CODFAM CAUSESINI LIBCAUSE NATSINI RESPONSA INFOTIER RESPXY OBGSOUNAT GRNTSINI GENREEVAL UPDATE_IDENT
     1        01 CORPOREL       D        N        N      X                BAS         R            2
     1        02 MATERIEL       D        N        N      N         N      BAS         R            5
     3        01 MATERIEL       D        N        N      N         N      BAS         R            7
     5        01 CORPOREL       C        N        N      N         Y      RCC         M            4
     5        02 DOMMAGES       M        N        O      N         Y       TR         L            5
```

### Null Counts For Key-Like Columns

- CODFAM: 0
- CAUSESINI: 0
- NATSINI: 0
- GRNTSINI: 0

### Candidate Key Duplicate Checks

- CODFAM + CAUSESINI: complete_key_rows=46, incomplete_key_rows=0, duplicate_row_count=0, duplicate_group_count=0

## correspondance garantie.xlsx / Feuil1

- file_name: `correspondance garantie.xlsx`
- sheet_name: `Feuil1`
- row_count: `1839`
- column_count: `6`

### Columns

- `CODPROD`
- `CODFORMU`
- `GRNTSINI`
- `CODGRNT`
- `LIBGRNSIN`
- `COLUMN_6`

### First 5 Rows

```text
CODPROD CODFORMU GRNTSINI CODGRNT                  LIBGRNSIN COLUMN_6
    521        1       BG      BG              BRIS DE GLACE        0
    521        1      CAS     CAS  Contre assurance spéciale        0
    521        1      ASR     CAS         Avance sur recours        0
    521        1      IDA     CAS Indem. directe des assurés        0
    521        1     GCOM     CAS           Geste Commercial        0
```

### Null Counts For Key-Like Columns

- CODPROD: 0
- CODFORMU: 0
- GRNTSINI: 0
- CODGRNT: 0

### Candidate Key Duplicate Checks

- CODPROD + CODFORMU + GRNTSINI: complete_key_rows=1839, incomplete_key_rows=0, duplicate_row_count=0, duplicate_group_count=0
