"""This is the main module of the application"""

from service_layer.store_service import get_products, add_product, add_sale, search_product_by, get_sales, cancel_sale
from data_access_layer.database import init_db

def print_options():
    """Method to print out the menu options"""
    print("\n=== Menu ===")
    print("1: Voir la liste des produits")
    print("2: Ajouter un produit")
    print("3: Enregistrer une vente")
    print("4: Chercher un produit")
    print("5: Voir la liste des ventes")
    print("6: Faire un retour")
    print("Q: Quitter")

def get_products_from_db():
    """Method that calls the service layer and formats the products"""
    products = get_products()
    print("=====Les Produits=====")
    for product in products:
        print(f"Nom: {product.name}, Prix: {product.price:.2f}$, Quantity: {product.quantity}")

def get_sales_from_db():
    """Method that calls the service layer and formats the sales."""
    sales = get_sales()
    print("\n===== Les Ventes =====")

    if not sales:
        print("Aucune vente enregistrée.")
        return

    for sale in sales:
        product = sale.product
        quantity = sale.quantity
        total = product.price * quantity
        print(f"#{sale.id}, {product.name} x {quantity}, Total: {total:.2f}$")

def add_product_to_db():
    """Prompts user for product info and adds it to the database"""
    print("\n=== Ajouter un produit ===")
    name = input("Nom du produit: ").strip()

    try:
        price = float(input("Prix du produit: "))
        quantity = int(input("Quantité en stock: "))
    except ValueError:
        print("Entrée invalide. Assurez-vous que le prix est un nombre décimal et la quantité un entier.")
        return

    add_product(name, price, quantity)

def add_sale_to_db():
    """Console interaction to record a sale"""
    print("\n=== Enregistrer une vente ===")

    products = get_products()
    if not products:
        print("Aucun produit trouvé.")
        return

    print("Produits disponibles :")
    for p in products:
        print(f"ID: {p.id} | {p.name} - {p.price:.2f}$ | Stock: {p.quantity}")

    try:
        product_id = int(input("Entrez l'ID du produit à vendre : ").strip())
        quantity = int(input("Entrez la quantité vendue : ").strip())
    except ValueError:
        print("Entrée invalide. Assurez-vous de saisir des nombres valides.")
        return

    if quantity <= 0:
        print("La quantité doit être positive.")
        return

    add_sale(product_id, quantity)

def search_product_in_db():
    """Method to display the searching methods in database"""
    print("\n=== Recherche de produit ===")
    print("1: Par identifiant")
    print("2: Par nom")
    print("3: Par catégorie")

    choice = input("Votre choix: ").strip()
    type_map = {"1": "id", "2": "name", "3": "category"}

    type_ = type_map.get(choice)
    if not type_:
        print("Choix invalide.")
        return

    keyword = input("Entrez le terme de recherche : ").strip()
    try:
        results = search_product_by(type_, keyword)
        if results:
            for p in results:
                print(f"ID: {p.id} | {p.name} | {p.price:.2f}$ | Stock: {p.quantity}")
        else:
            print("Aucun produit trouvé.")
    except ValueError as e:
        print(f"Erreur : {e}")

def cancel_sale_from_db():
    """Affiche toutes les ventes et permet à l'utilisateur d'en annuler une."""
    sales = get_sales()

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

def main():
    """Main method of the console app."""
    init_db()
    print("Bienvenue au magasin")

    is_done = False

    while not is_done:
        print_options()
        choix = input("Choix : ").strip().upper()

        match choix:
            case "1":
                get_products_from_db()
            case "2":
                add_product_to_db()
            case "3":
                add_sale_to_db()
            case "4":
                search_product_in_db()
            case "5":
                get_sales_from_db()
            case "6":
                cancel_sale_from_db()
            case "Q":
                print("Au revoir!")
                is_done = True
            case _:
                print("Choix invalide.")

if __name__ == "__main__":
    main()
