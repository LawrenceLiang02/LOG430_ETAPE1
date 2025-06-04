"""Product service module for the business layer"""
from service_layer.product_repository import add_product, get_products, search_product_by, update_product


def get_products_view():
    """Method that calls the service layer and formats the products"""
    products = get_products()
    print("=====Les Produits=====")
    for product in products:
        print(f"Nom: {product.name}, Prix: {product.price:.2f}$, Description: {product.description}")

def add_product_view():
    """Prompts user for product info and adds it to the database"""
    print("\n=== Ajouter un produit ===")
    name = input("Nom du produit: ").strip()
    description = input("Descripton du produit: ").strip()

    try:
        price = float(input("Prix du produit: "))
    except ValueError:
        print("Entrée invalide. Assurez-vous que le prix est un nombre décimal et la quantité un entier.")
        return

    add_product(name, price, description)

def search_product_view():
    """Method to display the searching methods in database"""
    print("\n=== Recherche de produit ===")
    print("1: Par identifiant")
    print("2: Par nom")
    # print("3: Par catégorie")

    choice = input("Votre choix: ").strip()
    # type_map = {"1": "id", "2": "name", "3": "category"}
    type_map = {"1": "id", "2": "name"}

    type_ = type_map.get(choice)
    if not type_:
        print("Choix invalide.")
        return

    keyword = input("Entrez le terme de recherche : ").strip()
    try:
        results = search_product_by(type_, keyword)
        if results:
            for p in results:
                print(f"ID: {p.id} | {p.name} | {p.price:.2f}$ | {p.description}")
        else:
            print("Aucun produit trouvé.")
    except ValueError as e:
        print(f"Erreur : {e}")

def update_product_view():
    """Method to update product in db"""
    print("=== Modifier un produit ===")

    products = get_products()
    if not products:
        print("Aucun produit trouvé.")
        return

    print("===== Les Produits =====")
    for product in products:
        print(f"ID: {product.id}, Nom: {product.name}, Prix: {product.price:.2f}$, Description: {product.description}")

    try:
        prod_id = int(input("Entrez l'ID du produit à modifier: ").strip())
    except ValueError:
        print("ID invalide.")
        return

    selected = next((p for p in products if p.id == prod_id), None)
    if not selected:
        print(f"Aucun produit trouvé avec l'ID {prod_id}.")
        return

    print(f"\nProduit sélectionné: {selected.name}")

    new_name = input(f"Nom ({selected.name}): ").strip() or selected.name
    new_price_str = input(f"Prix ({selected.price}): ").strip()
    try:
        new_price = float(new_price_str) if new_price_str else selected.price
    except ValueError:
        print("Prix invalide. Le prix n'a pas été modifié.")
        new_price = selected.price

    new_desc = input(f"Description ({selected.description}): ").strip() or selected.description

    success = update_product(prod_id, new_name, new_price, new_desc)
    if success:
        print("Produit mis à jour avec succès.")
    else:
        print("Échec de la mise à jour (produit introuvable).")
