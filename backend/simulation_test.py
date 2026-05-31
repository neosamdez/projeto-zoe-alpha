import os
import uuid
import unittest
from unittest.mock import MagicMock, patch

# Set dummy environment variables for Pydantic Settings
os.environ["DB_URL"] = "sqlite:///:memory:"
os.environ["X_TENANT_ID"] = str(uuid.uuid4())
os.environ["SECRET_KEY"] = "dummy-secret-key"
os.environ["SMTP_SERVER"] = "localhost"
os.environ["SMTP_PORT"] = "1025"
os.environ["SMTP_USER"] = "user@example.com"
os.environ["SMTP_PASSWORD"] = "password"
os.environ["ADMIN_EMAIL"] = "admin@example.com"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Product, MovementType
from app.services.email_service import EmailService
from app.services.alert_service import AlertService
from app.services.inventory_service import InventoryService

class TestInventoryAlertSimulation(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for simulation
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self.tenant_id = uuid.uuid4()
        self.user_id = uuid.uuid4()

        # Mock EmailService to verify calls
        self.mock_email_service = MagicMock(spec=EmailService)
        
        # Initialize Services
        self.alert_service = AlertService(db=self.db, email_service=self.mock_email_service)
        self.inventory_service = InventoryService(
            db=self.db, 
            tenant_id=self.tenant_id, 
            alert_service=self.alert_service
        )

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_low_stock_triggers_email(self):
        # 1. Seed a product
        product_id = uuid.uuid4()
        product = Product(
            id=product_id,
            tenant_id=self.tenant_id,
            name="Test Product",
            sku="TEST-SKU",
            current_stock=15,
            min_stock=10,
            cost_price=10.0,
            selling_price=20.0
        )
        self.db.add(product)
        self.db.commit()

        # 2. Create a movement that drops stock below min_stock
        from app.schemas.inventory import InventoryMovementCreate
        movement_data = InventoryMovementCreate(
            product_id=product_id,
            movement_type=MovementType.OUT,
            quantity=10,
            reference_id="SIM-001",
            notes="Simulated reduction"
        )

        # Since we can't easily use FastAPI BackgroundTasks here without the full app context,
        # we will simulate the BackgroundTask call manually to verify the logic.
        # In the real app, the router would do: background_tasks.add_task(alert_service.check_and_notify_low_stock, product.id)
        
        # Perform movement
        self.inventory_service.create_movement(user_id=self.user_id, data=movement_data)
        
        # MANUALLY trigger the alert as the BackgroundTask would
        self.alert_service.check_and_notify_low_stock(product.id)

        # 3. Verifications
        # Check stock level
        updated_product = self.db.query(Product).get(product_id)
        self.assertEqual(updated_product.current_stock, 5)

        # Check if email was "sent"
        self.assertTrue(self.mock_email_service.send_alert.called)
        args, kwargs = self.mock_email_service.send_alert.call_args
        self.assertIn("ALERTA: Estoque Baixo", args[1])
        self.assertIn("Test Product", args[1])

if __name__ == "__main__":
    unittest.main()


