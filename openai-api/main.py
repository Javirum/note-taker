import os
import json
import random
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
from product_listing_prompt import create_product_listing_prompt
from product_data import products_df, get_base64_data_url


class ProductListing(BaseModel):
    """Structure for the AI-generated listing content."""
    title: str
    description: str
    features: List[str]
    keywords: str


class Product(BaseModel):
    """Structure for a product with its generated listing."""
    id: int
    product_name: str
    category: str
    price: float
    listing: Optional[ProductListing] = None
    error: Optional[str] = None


def parse_listing_response(content: str) -> ProductListing:
    """Parse the AI response (JSON in markdown) into a ProductListing."""
    # Strip markdown code block if present
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]

    data = json.loads(content.strip())
    return ProductListing(**data)


load_dotenv()

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set randm prices for products (since the dataset doesn't include prices)
products_df["price"] = [round(random.uniform(10, 100), 2) for _ in range(len(products_df))]


results: List[Product] = []
for idx, row in products_df.iterrows():
    try:
        prompt = create_product_listing_prompt(
            product_name=row["productDisplayName"],
            price=row["price"],
            category=row["masterCategory"],
            additional_info="High-quality material, available in multiple colors"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": get_base64_data_url(row["image"])}
                        }
                    ]
                }
            ]
        )

        listing_content = response.choices[0].message.content
        listing = parse_listing_response(listing_content)
        product = Product(
            id=row["id"],
            product_name=row["productDisplayName"],
            category=row["masterCategory"],
            price=row["price"],
            listing=listing
        )
        results.append(product)

    except Exception as e:
        print(f"✗ Error processing product {idx}: {e}")
        product = Product(
            id=row.get("id", idx),
            product_name=row.get("productDisplayName", "Unknown"),
            category=row.get("masterCategory", "Unknown"),
            price=row.get("price", 0.0),
            error=str(e)
        )
        results.append(product)

# Save results to JSON
output_file = "product_listings.json"
with open(output_file, "w") as f:
    json.dump([product.model_dump() for product in results], f, indent=2)

print(f"\n{'='*50}")
print(f"✓ Saved {len(results)} listings to {output_file}")
print(f"  Successful: {len([r for r in results if r.listing is not None])}")
print(f"  Errors: {len([r for r in results if r.error is not None])}")