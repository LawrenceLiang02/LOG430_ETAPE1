"""Product service module for the business layer"""
from service_layer.product_repository import add_product, get_products, search_product_by


def get_products_from_db():
    """Method that calls the service layer and formats the products"""
    products = get_products()
    print("=====Les Produits=====")
    for product in products:
        print(f"Nom: {product.name}, Prix: {product.price:.2f}$")

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
