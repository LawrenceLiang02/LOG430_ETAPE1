"""This is the main module of the application"""

from service_layer.store_service import(get_sales_by_location,
                                        get_stock,
                                        add_stock,
                                        get_all_locations,
                                        get_products,
                                        add_product,
                                        add_sale,
                                        search_product_by,
                                        get_all_sales,
                                        cancel_sale)
    
from data_access_layer.database import init_db

def print_action_options():
    """Method to print out the menu options"""
    print("\n=== Menu ===")
    print("1: Voir la liste des produits")
    print("2: Ajouter un produit")
    print("3: Chercher un produit")
    print("4: Enregistrer une vente")
    print("5: Voir la liste des ventes")
    print("6: Faire un retour")
    print("7: Add stock")
    print("8: Voir stock")
    print("Q: Quitter")

def store_selection():
    """Shows a list of store and returns the selected store."""
    locations = get_all_locations()
    if not locations:
        print("Aucun magasin trouvé.")
        return None

    print("=== Veuillez choisir votre magasin ===")
    for i, loc in enumerate(locations, 1):
        print(f"{i}. {loc.name}")

    while True:
        choix = input("Choix: ").strip()
        if choix.isdigit():
            idx = int(choix) - 1
            if 0 <= idx < len(locations):
                return locations[idx]
        print("Choix invalide. Veuillez réessayer.")

def get_products_from_db():
    """Method that calls the service layer and formats the products"""
    products = get_products()
    print("=====Les Produits=====")
    for product in products:
        print(f"Nom: {product.name}, Prix: {product.price:.2f}$")

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

def add_product_to_db():
    """Prompts user for product info and adds it to the database"""
    print("\n=== Ajouter un produit ===")
    name = input("Nom du produit: ").strip()

    try:
        price = float(input("Prix du produit: "))
    except ValueError:
        print("Entrée invalide. Assurez-vous que le prix est un nombre décimal et la quantité un entier.")
        return

    add_product(name, price)

def add_stock_to_db(location):
    """Adds stock to a location"""
    print("\n=== Ajouter un stock ===")
    products = get_products()
    if not products:
        print("Aucun produit trouvé.")
        return

    print("\n=== Produits disponibles ===")
    for product in products:
        print(f"[{product.id}] {product.name} - {product.price:.2f} $")

    selected_product = None
    while not selected_product:
        try:
            product_id = int(input("Entrez l'ID du produit à ajouter en stock : ").strip())
            selected_product = next((p for p in products if p.id == product_id), None)
            if not selected_product:
                print("Produit introuvable.")
        except ValueError:
            print("Veuillez entrer un ID valide.")

    while True:
        try:
            quantity = int(input("Entrez la quantité à ajouter : ").strip())
            if quantity < 0:
                raise ValueError
            break
        except ValueError:
            print("Veuillez entrer une quantité valide.")

    add_stock(selected_product.id, location, quantity)
  
def get_stock_from_db(location):
    """Get stock from db"""
    stock_list = get_stock(location)

    print(f"\nStock pour '{location.name}':")
    for stock in stock_list:
        print(f"ID: {stock.product.id} | Nom: {stock.product.name} | Quantity:{stock.quantity}")

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
                print(f"ID: {p.id} | {p.name} | {p.price:.2f}$")
        else:
            print("Aucun produit trouvé.")
    except ValueError as e:
        print(f"Erreur : {e}")

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

def main():
    """Main method of the console app."""
    init_db()
    print("Bienvenue au magasin")

    is_done = False

    location = store_selection()

    while not is_done:
        print_action_options()
        choix = input("Choix : ").strip().upper()

        match choix:
            case "1":
                get_products_from_db()
            case "2":
                add_product_to_db()
            case "3":
                search_product_in_db()
            case "4":
                add_sale_to_db(location)
            case "5":
                get_sales_from_db(location)
            case "6":
                cancel_sale_from_db(location)
            case "7":
                add_stock_to_db(location)
            case "8":
                get_stock_from_db(location)
            case "Q":
                print("Au revoir!")
                is_done = True
            case _:
                print("Choix invalide.")

if __name__ == "__main__":
    main()
