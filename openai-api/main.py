import os
import json
import random
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from product_listing_prompt import create_product_listing_prompt
from product_data import products_df, get_base64_data_url
from dotenv import load_dotenv


load_dotenv()

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set randm prices for products (since the dataset doesn't include prices)
products_df["price"] = [round(random.uniform(10, 100), 2) for _ in range(len(products_df))]


results = []
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

        listing = response.choices[0].message.content
        results.append({
            "id": row["id"],
            "product_name": row["productDisplayName"],
            "category": row["masterCategory"],
            "price": row["price"],
            "listing": listing
        })

    except Exception as e:
        print(f"✗ Error processing product {idx}: {e}")
        results.append({
            "id": row.get("id", idx),
            "product_name": row.get("productDisplayName", "Unknown"),
            "error": str(e)
        })

# Save results to JSON
output_file = "product_listings.json"
with open(output_file, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n{'='*50}")
print(f"✓ Saved {len(results)} listings to {output_file}")
print(f"  Successful: {len([r for r in results if 'listing' in r])}")
print(f"  Errors: {len([r for r in results if 'error' in r])}")