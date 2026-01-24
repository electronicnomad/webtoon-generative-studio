
from google.genai import types
from models.image_models import ImagenModelSetup
import inspect

client = ImagenModelSetup.init(project_id="test-project", location="us-central1") # Dummy init to get client/method
try:
    print("Signature of client.models.generate_images:")
    print(inspect.signature(client.models.generate_images))
    
    print("\nDocstring:")
    print(client.models.generate_images.__doc__)
except Exception as e:
    print(f"Error: {e}")
