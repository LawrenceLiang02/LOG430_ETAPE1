"""Stock service module for the business layer"""
from data_access_layer.product_repository import get_products
from data_access_layer.stock_repository import add_stock, get_stock


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
