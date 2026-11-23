import os

from app import create_app
from app.models import Category, Product, User, db

app = create_app()


def seed():
    """Create an admin user and demo catalog:  python run.py seed"""
    with app.app_context():
        if not User.query.filter_by(email="admin@shop.local").first():
            admin = User(name="Admin", email="admin@shop.local", role="admin")
            admin.set_password(os.environ.get("ADMIN_PASSWORD", "Admin12345"))
            db.session.add(admin)
        if not Category.query.count():
            books, tech = Category(name="Books"), Category(name="Electronics")
            db.session.add_all([books, tech])
            db.session.flush()
            db.session.add_all([
                Product(name="Clean Code", description="A handbook of agile software craftsmanship", price_cents=3500, stock=25, category_id=books.id),
                Product(name="Mechanical Keyboard", description="Tactile switches, USB-C", price_cents=8900, stock=10, category_id=tech.id),
                Product(name="USB-C Cable", description="1m braided cable", price_cents=799, stock=100, category_id=tech.id),
            ])
        db.session.commit()
        print("Seeded. Admin: admin@shop.local / (ADMIN_PASSWORD or Admin12345)")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "seed":
        seed()
    else:
        app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)
