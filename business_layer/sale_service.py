"""Sale service module for the business layer"""
from data_access_layer.sale_repository import add_sale, cancel_sale, get_sales_by_location
from data_access_layer.stock_repository import get_stock


def get_sales_from_db(location):
    """Shows a list of sales from specific location."""
    sales = get_sales_by_location(location)
    print("\n===== Les Ventes =====")

    if not sales:
        print("Aucune vente enregistrée.")
        return

    for sale in sales:
        product = sale.product
        location = sale.location.name if sale.location else "Inconnu"
        quantity = sale.quantity
        total = product.price * quantity if product else 0.0
        product_name = product.name if product else "Produit inconnu"
        print(f"#{sale.id}, Magasin: {location}, {product_name} x {quantity}, Total: {total:.2f}$")

def add_sale_to_db(location):
    """Console interaction to record a sale"""
    print("\n=== Enregistrer une vente ===")

    stock_list = get_stock(location)
    if not stock_list:
        print("Aucun produit trouvé.")
        return

    print("Produits disponibles :")
    for stock in stock_list:
        print(f"ID: {stock.product.id} | Name: {stock.product.name} | Quantity: {stock.quantity}")

    try:
        product_id = int(input("Entrez l'ID du produit à vendre : ").strip())
        quantity = int(input("Entrez la quantité vendue : ").strip())
    except ValueError:
        print("Entrée invalide. Assurez-vous de saisir des nombres valides.")
        return

    if quantity <= 0:
        print("La quantité doit être positive.")
        return

    add_sale(product_id, location, quantity)

def cancel_sale_from_db(location):
    """Affiche toutes les ventes et permet à l'utilisateur d'en annuler une."""
    sales = get_sales_by_location(location)

    if not sales:
        print("Aucune vente enregistrée.")
        return

    print("\n===== Liste des Ventes =====")
    for sale in sales:
        product = sale.product
        total = product.price * sale.quantity
        print(f"ID: {sale.id} | Produit: {product.name} | Quantité: {sale.quantity} | Prix: {product.price:.2f}$ | Total: {total:.2f}$")

    try:
        sale_id = int(input("\nEntrez l'ID de la vente que vous voulez annuler (ou 0 pour annuler): "))
        if sale_id == 0:
            print("Annulation de l'opération.")
            return

        cancel_sale(sale_id)

    except ValueError:
        print("Entrée invalide. Veuillez entrer un nombre.")