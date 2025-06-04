"""Module to generate reports"""
import os
import csv
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from data_class.models import Sale, Product, Stock, Location
from service_layer.database import SessionLocal

def generate_sales_report_csv(filename="rapport_ventes.csv"):
    """Generate sales report method"""
    session = SessionLocal()

    sales_by_location = (
        session.query(Location.name, func.sum(Sale.quantity * Product.price))
        .join(Sale, Sale.location_id == Location.id)
        .join(Product, Product.id == Sale.product_id)
        .group_by(Location.name)
        .all()
    )

    top_products = (
        session.query(Product.name, func.sum(Sale.quantity).label("total_qty"))
        .join(Sale, Sale.product_id == Product.id)
        .group_by(Product.name)
        .order_by(func.sum(Sale.quantity).desc())
        .limit(5)
        .all()
    )

    stock_remaining = (
        session.query(Location.name, Product.name, Stock.quantity)
        .join(Stock, Stock.location_id == Location.id)
        .join(Product, Product.id == Stock.product_id)
        .order_by(Location.name, Product.name)
        .all()
    )

    session.close()

    output_dir = "rapport"
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{output_dir}/rapport_ventes_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(["Rapport consolidé des ventes"])
        writer.writerow(["Date de génération", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])

        writer.writerow(["Ventes par magasin"])
        writer.writerow(["Magasin", "Total ($)"])
        for loc, total in sales_by_location:
            writer.writerow([loc, f"{total:.2f}"])
        writer.writerow([])

        writer.writerow(["Top 5 produits les plus vendus"])
        writer.writerow(["Produit", "Quantité totale"])
        for name, qty in top_products:
            writer.writerow([name, qty])
        writer.writerow([])

        writer.writerow(["Stock restant par magasin"])
        writer.writerow(["Magasin", "Produit", "Quantité"])
        for loc, prod, qty in stock_remaining:
            writer.writerow([loc, prod, qty])

    return filename

def get_store_performance_metrics(rupture_qty=10, surstock_qty=100):
    """Store performance metrics"""
    session = SessionLocal()

    revenue_by_store = (
        session.query(Location.name, func.sum(Sale.quantity * Product.price).label("revenue"))
        .join(Sale, Sale.location_id == Location.id)
        .join(Product, Product.id == Sale.product_id)
        .group_by(Location.name)
        .order_by(Location.name)
        .all()
    )

    # pylint: disable=not-callable
    total_sales = session.query(func.count(Sale.id)).scalar()

    top_product = (
        session.query(Product.name, func.sum(Sale.quantity).label("total"))
        .join(Sale, Sale.product_id == Product.id)
        .group_by(Product.name)
        .order_by(func.sum(Sale.quantity).desc())
        .first()
    )

    stocks = session.query(Stock).options(
        joinedload(Stock.product),
        joinedload(Stock.location)
    ).all()

    rupture = [s for s in stocks if s.quantity < rupture_qty]
    surstock = [s for s in stocks if s.quantity > surstock_qty]

    session.close()
    return revenue_by_store, total_sales, top_product, rupture, surstock
