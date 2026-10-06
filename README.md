# 📊 Jour 2 / 10 — Dataiku : SQL et Jointures

> **Série : 10 Days of Dataiku** · Jour 2/10  
> Concepts : Group Recipe · Join Recipe · SQL Recipe · Window Recipe · Flow multi-datasets

---

## 📁 Fichiers du projet

```
day-02-sql-jointures/
│
├── ventes_dataiku_j2.xlsx       ← 3 feuilles : Ventes + Vendeurs + Clients
│   ├── Ventes                   ← 284 transactions avec IDs
│   ├── Vendeurs                 ← 5 vendeurs avec objectifs
│   └── Clients                  ← 20 clients avec segments
├── recipe_sql_j2.py             ← Script Python reproduisant les recettes
└── README.md
```

---

## 🚀 ÉTAPE 1 — Importer les 3 datasets

```
Dans le projet Dataiku du Jour 1 (ou créer un nouveau) :

1. Menu gauche → Datasets → + Dataset → Upload
2. Importer ventes_dataiku_j2.xlsx
3. Dataiku détecte les 3 feuilles — créer 3 datasets séparés :
   → Choisir la feuille "Ventes"   → nommer "ventes"
   → Répéter pour "Vendeurs"       → nommer "vendeurs"
   → Répéter pour "Clients"        → nommer "clients"
4. Vérifier le schema de chaque dataset dans "Explore"
```

---

## 🔑 ÉTAPE 2 — Group Recipe (agréger)

```
Flow → cliquer sur "ventes" → Recipes → Visual → Group

Configuration :
→ Group by : ID Vendeur
→ Aggrégations à ajouter :
   Montant    → SUM  → renommer "CA_Total"
   Coût Total → SUM  → renommer "Cout_Total"
   ID Vente   → COUNT→ renommer "Nb_Ventes"
   Quantité   → SUM  → renommer "Qte_Totale"
   Montant    → AVG  → renommer "Panier_Moyen"

→ Output dataset : "kpis_par_vendeur"
→ Cliquer "Run"
```

---

## 🔑 ÉTAPE 3 — Join Recipe (joindre)

```
Flow → "+ Recipe" → Visual → Join

Inputs :
→ Dataset gauche  : kpis_par_vendeur
→ Dataset droite  : vendeurs

Configuration de la jointure :
→ Type : Left join
→ Condition : kpis_par_vendeur.ID Vendeur = vendeurs.ID Vendeur
→ Colonnes à garder depuis "vendeurs" :
   Nom, Équipe, Région, Objectif

→ Output dataset : "performance_vendeurs"
→ Cliquer "Run"

Ajouter une colonne calculée dans Prepare :
→ Atteinte_Obj = CA_Total / Objectif * 100
→ Statut = if(Atteinte_Obj >= 100, "Atteint", "Non atteint")
```

---

## 🔑 ÉTAPE 4 — SQL Recipe

```
Flow → "+ Recipe" → Code → SQL

Input : ventes (+ vendeurs en JOIN)
Output : ventes_avec_vendeurs (nouveau dataset)

Coller dans l'éditeur SQL :

SELECT
    v.ID_Vendeur        AS id_vendeur,
    vd.Nom              AS nom_vendeur,
    v.Mois              AS mois,
    v.Trimestre         AS trimestre,
    COUNT(*)            AS nb_ventes,
    SUM(v.Montant)      AS ca_total,
    SUM(v.Coût_Total)   AS cout_total,
    SUM(v.Montant) - SUM(v.Coût_Total) AS marge_totale,
    ROUND(
        (SUM(v.Montant) - SUM(v.Coût_Total))
        / SUM(v.Montant) * 100, 1
    )                   AS taux_marge,
    vd.Objectif         AS objectif,
    ROUND(
        SUM(v.Montant) / vd.Objectif * 100, 1
    )                   AS atteinte_objectif_pct
FROM ventes v
LEFT JOIN vendeurs vd ON v.ID_Vendeur = vd.ID_Vendeur
GROUP BY
    v.ID_Vendeur, vd.Nom, v.Mois, v.Trimestre, vd.Objectif
ORDER BY
    v.Mois, ca_total DESC

→ Cliquer "Run"
→ Explorer le résultat dans "Explore"
```

---

## 🔑 ÉTAPE 5 — Window Recipe (fonctions fenêtrées)

```
Flow → cliquer sur "ventes" → Recipes → Visual → Window

Configuration :
→ Partition by : ID Vendeur
→ Order by     : Mois ASC

Ajouter les colonnes fenêtrées :
1. Montant → Cumulative SUM → renommer "CA_Cumulé"
2. Montant → Rank (DENSE_RANK) dans la partition Mois → "Rang_Mensuel"
3. Montant → % of total dans Mois → "Part_Mois_Pct"

→ Output dataset : "ventes_window"
→ Cliquer "Run"
```

---

## 🔑 ÉTAPE 6 — Utiliser le script Python (recipe_sql_j2.py)

```
Option A — Dans Dataiku :
→ Flow → "+ Recipe" → Code → Python
→ Coller le contenu de recipe_sql_j2.py
→ Remplacer les pd.read_excel() par dataiku.Dataset().get_dataframe()
→ Décommenter les lignes dataiku.Dataset(...).write_with_schema(df)
→ Run

Option B — En local :
→ pip install pandas openpyxl
→ python recipe_sql_j2.py
→ Voir les résultats dans le terminal
```

---

## 🔑 ÉTAPE 7 — Visualiser le Flow

```
Après toutes ces recettes, le Flow ressemble à :

[ventes]  ──────────────────────────────────────────────┐
   ├── (Group)  → [kpis_par_vendeur]                    │
   │                    │                               │
   │             (Join) + [vendeurs] → [performance]    │
   │                                                    │
   ├── (SQL)    ← [vendeurs] → [ventes_avec_vendeurs]   │
   │                                                    │
   └── (Window) → [ventes_window] ←─────────────────────┘

[vendeurs] ──┤
[clients]  ──┘
```

---

## 💡 Comparaison des recettes Dataiku

| Recette | Usage | Équivalent |
|---------|-------|------------|
| **Group** | Agréger (SUM, COUNT, AVG) | SQL GROUP BY |
| **Join** | Joindre deux datasets | SQL LEFT/INNER JOIN |
| **SQL** | Requêtes SQL complexes | SQL complet |
| **Window** | Rang, cumul, décalage | SQL OVER PARTITION BY |
| **Prepare** | Nettoyage visuel | Python/pandas |
| **Python** | Logique complexe | Script Python |

---

---

⭐ **Si ce projet t'aide, mets une étoile !**
