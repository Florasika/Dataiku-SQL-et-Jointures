# ============================================================
#  JOUR 2 / 10 — Dataiku : Recette Python simulant SQL + Jointures
#  Ce script reproduit ce qu'on fait dans les recettes visuelles
#  Dataiku (Group, Join, SQL) — utilisable aussi en local
# ============================================================

import dataiku
import pandas as pd

# ── Chargement des datasets (dans Dataiku) ───────────────────
# df_ventes   = dataiku.Dataset("ventes").get_dataframe()
# df_vendeurs = dataiku.Dataset("vendeurs").get_dataframe()
# df_clients  = dataiku.Dataset("clients").get_dataframe()

# ── En local : charger depuis Excel ──────────────────────────
df_ventes   = pd.read_excel("ventes_dataiku_j2.xlsx", sheet_name="Ventes")
df_vendeurs = pd.read_excel("ventes_dataiku_j2.xlsx", sheet_name="Vendeurs")
df_clients  = pd.read_excel("ventes_dataiku_j2.xlsx", sheet_name="Clients")

print(f"Ventes   : {len(df_ventes)} lignes")
print(f"Vendeurs : {len(df_vendeurs)} lignes")
print(f"Clients  : {len(df_clients)} lignes")

# ════════════════════════════════════════════════════════════
#  RECETTE GROUP — Agréger par vendeur
#  Équivalent : Group Recipe dans Dataiku
# ════════════════════════════════════════════════════════════
df_kpis_vendeur = df_ventes.groupby('ID Vendeur').agg(
    CA_Total      = ('Montant',    'sum'),
    Cout_Total    = ('Coût Total', 'sum'),
    Nb_Ventes     = ('ID Vente',   'count'),
    Qte_Totale    = ('Quantité',   'sum'),
    Panier_Moyen  = ('Montant',    'mean'),
).round(2).reset_index()

df_kpis_vendeur['Marge_Totale'] = (
    df_kpis_vendeur['CA_Total'] - df_kpis_vendeur['Cout_Total']
).round(2)
df_kpis_vendeur['Taux_Marge'] = (
    df_kpis_vendeur['Marge_Totale'] / df_kpis_vendeur['CA_Total'] * 100
).round(1)

print("\n=== KPIs par Vendeur ===")
print(df_kpis_vendeur.to_string(index=False))

# ════════════════════════════════════════════════════════════
#  RECETTE JOIN — Enrichir avec les infos vendeurs
#  Équivalent : Join Recipe dans Dataiku
# ════════════════════════════════════════════════════════════
df_joint = df_kpis_vendeur.merge(
    df_vendeurs[['ID Vendeur','Nom','Équipe','Région','Objectif']],
    on='ID Vendeur',
    how='left'
)
df_joint['Atteinte_Obj'] = (
    df_joint['CA_Total'] / df_joint['Objectif'] * 100
).round(1)
df_joint['Statut'] = df_joint['Atteinte_Obj'].apply(
    lambda x: '✓ Atteint' if x >= 100 else '✗ Non atteint'
)

print("\n=== Performance Vendeurs avec Objectifs ===")
print(df_joint[['Nom','CA_Total','Objectif','Atteinte_Obj','Statut']].to_string(index=False))

# ════════════════════════════════════════════════════════════
#  RECETTE SQL — Simulation d'une requête SQL dans Dataiku
#  Équivalent : SQL Script Recipe dans Dataiku
# ════════════════════════════════════════════════════════════
# Dans Dataiku SQL Recipe, on écrirait directement :
# SELECT
#     v.ID_Vendeur,
#     vd.Nom,
#     COUNT(*) AS nb_ventes,
#     SUM(v.Montant) AS ca_total,
#     SUM(v.Montant) / vd.Objectif * 100 AS atteinte_obj
# FROM ventes v
# LEFT JOIN vendeurs vd ON v.ID_Vendeur = vd.ID_Vendeur
# GROUP BY v.ID_Vendeur, vd.Nom, vd.Objectif
# ORDER BY ca_total DESC

# Simulation avec pandas (même logique) :
df_sql_result = (
    df_ventes
    .merge(df_vendeurs[['ID Vendeur','Nom','Objectif']], on='ID Vendeur', how='left')
    .merge(df_clients[['ID Client','Segment']], on='ID Client', how='left')
    .groupby(['ID Vendeur','Nom','Segment'])
    .agg(nb_ventes=('ID Vente','count'), ca_total=('Montant','sum'))
    .reset_index()
    .sort_values('ca_total', ascending=False)
)

print("\n=== Résultat SQL : Ventes par Vendeur × Segment ===")
print(df_sql_result.head(10).to_string(index=False))

# ════════════════════════════════════════════════════════════
#  RECETTE WINDOW — Fonctions fenêtrées
#  Équivalent : Window Recipe dans Dataiku
# ════════════════════════════════════════════════════════════
df_window = df_ventes.copy()

# Rang du vendeur par mois
df_window['Rang_Mensuel'] = df_window.groupby('Mois')['Montant'].rank(
    method='dense', ascending=False
).astype(int)

# CA cumulé par vendeur
df_window = df_window.sort_values(['ID Vendeur','Mois'])
df_window['CA_Cumule'] = df_window.groupby('ID Vendeur')['Montant'].cumsum().round(2)

# Part du vendeur dans le CA du mois
df_window['Part_Mois'] = df_window.groupby('Mois')['Montant'].transform(
    lambda x: (x / x.sum() * 100).round(1)
)

print("\n=== Window Functions : CA Cumulé par Vendeur ===")
sample = df_window[['Mois','ID Vendeur','Montant','CA_Cumule','Part_Mois']].head(15)
print(sample.to_string(index=False))

# ── Écriture des outputs (dans Dataiku) ──────────────────────
# dataiku.Dataset("kpis_vendeurs").write_with_schema(df_joint)
# dataiku.Dataset("ventes_enrichies").write_with_schema(df_window)
print("\n✓ Toutes les transformations terminées")
