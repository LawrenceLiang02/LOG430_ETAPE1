from service_layer.report_service import generate_sales_report_csv, get_store_performance_metrics

def print_sales_report_csv():
    """Method of view layer to print  sales report in csv"""
    print("\n=== Génération du rapport consolidé (CSV) ===")
    filename = generate_sales_report_csv()
    print(f"Rapport généré avec succès : {filename}")

def print_store_dashboard(rupture_qty=10, surstock_qty=100):
    """Prints the dashboard for store data"""
    print("\n=== Tableau de bord des performances des magasins ===")

    revenues, total_sales, top_product, rupture, surstock = get_store_performance_metrics(rupture_qty, surstock_qty)

    print("\n== Chiffre d'affaires par magasin ==")
    for store, revenue in revenues:
        print(f"{store}: {revenue:.2f} $")

    print(f"\n== Nombre total de ventes enregistrées : {total_sales}")

    if top_product:
        name, quantity = top_product
        print(f"== Produit le plus vendu : {name} ({quantity} unités)")
    else:
        print("== Aucun produit vendu pour le moment.")

    print("\n== Alertes de stock ==")
    if rupture:
        print(f"Produits en rupture de stock (< {rupture_qty} unités) :")
        for s in rupture:
            print(f"- {s.product.name} ({s.quantity} unités) à {s.location.name}")
    else:
        print("Aucun produit en rupture.")

    if surstock:
        print(f"\nProduits en surstock (> {surstock_qty} unités) :")
        for s in surstock:
            print(f"- {s.product.name} ({s.quantity} unités) à {s.location.name}")
    else:
        print("Aucun produit en surstock.")
