"""This is the main module of the application"""

import argparse
from presentation_layer.location_view import store_selection
from presentation_layer.product_view import add_product_to_db, get_products_from_db, search_product_in_db, update_product_in_db
from presentation_layer.sale_view import add_sale_to_db, cancel_sale_from_db, get_sales_from_db
from presentation_layer.stock_view import add_stock_to_db, get_stock_from_db

from service_layer.database import init_db


ACTIONS = {
    "1": ("Voir la liste des produits", get_products_from_db),
    "2": ("Ajouter un produit", add_product_to_db),
    "3": ("Chercher un produit", search_product_in_db),
    "4": ("Enregistrer une vente", add_sale_to_db),
    "5": ("Voir la liste des ventes", get_sales_from_db),
    "6": ("Faire un retour", cancel_sale_from_db),
    "7": ("Add stock", add_stock_to_db),
    "8": ("Voir stock", get_stock_from_db),
    "Q": ("Quitter", None),
    "9": ("Modifier un produit", update_product_in_db),
}

ROLE_PERMISSIONS = {
    "Maison mère": list(ACTIONS.keys()),
    "Centre Logistique": ["1", "2", "3", "7", "8", "Q"],
    "Magasin": ["1", "3", "4", "5", "6", "7", "8", "Q"],
}

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

def run_cli():
    """Main method of the console app."""
    init_db()
    print("Bienvenue au magasin")

    is_done = False
    location = store_selection()

    if "maison mère" in location.name.lower():
        role = "Maison mère"
    elif "centre logistique" in location.name.lower():
        role = "Centre Logistique"
    elif "magasin" in location.name.lower():
        role = "Magasin"
    else:
        print("Emplacement inconnu. Aucun rôle attribué.")
        return

    allowed_actions = ROLE_PERMISSIONS[role]

    while not is_done:
        print("\n=== Menu ===")
        for key in allowed_actions:
            print(f"{key}: {ACTIONS[key][0]}")

        choix = input("Choix : ").strip().upper()

        if choix not in allowed_actions:
            print("Choix invalide ou non autorisé.")
            continue

        if choix == "Q":
            print("Au revoir!")
            is_done = True
        else:
            _, action_fn = ACTIONS[choix]
            if choix in ["4", "5", "6", "7", "8"]:
                action_fn(location)
            else:
                action_fn()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose mode: CLI or API")
    parser.add_argument(
        "--mode",
        choices=["cli", "api"],
        default="cli",
        help="Select the mode to run: cli or api"
    )

    args = parser.parse_args()

    if args.mode == "cli":
        run_cli()
    elif args.mode == "api":
        run_cli()
