"""This is the main module of the application"""

from presentation_layer.location_view import store_selection
from presentation_layer.product_view import add_product_to_db, get_products_from_db, search_product_in_db
from presentation_layer.sale_view import add_sale_to_db, cancel_sale_from_db, get_sales_from_db
from presentation_layer.stock_view import add_stock_to_db, get_stock_from_db

from service_layer.database import init_db

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
