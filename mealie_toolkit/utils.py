"""Utility functions for the Mealie Toolkit."""

import os

import httpx

from mealie_toolkit.mealie_client import MealieClient


def print_recipes(recipes: list[dict]) -> None:
    """
    Print all recipes in a formatted manner.

    Args:
        recipes: List of recipe dictionaries to print
    """
    print(f"Found {len(recipes)} recipes:\n")

    for recipe in recipes:
        name = recipe.get("name", "Unknown")
        recipe_id = recipe.get("id")
        slug = recipe.get("slug", "N/A")
        categories = recipe.get("recipeCategory", [])
        print(f"  - {name}")
        print(f"    ID: {recipe_id}")
        print(f"    Slug: {slug}")
        if categories:
            cat_names = ", ".join([c.get("name", "Unknown") for c in categories])
            print(f"    Categories: {cat_names}")
        if recipe.get("image"):
            print(f"    Image: {recipe.get('image')}")
        print()


def print_categories(categories: list[dict], client: MealieClient) -> None:
    """
    Print all categories in a formatted manner.

    Args:
        categories: List of category dictionaries to print
        client: The MealieClient instance for fetching additional details
    """
    print(f"Found {len(categories)} categories:\n")

    for category in categories:
        print(f"  - {category.get('name', 'Unknown')} (ID: {category.get('id')})")


def populate_categories(client: MealieClient, file_path: str) -> None:
    """
    Populate categories from a file.

    Args:
        client: The MealieClient instance
        file_path: Path to the file containing category names (one per line)
    """
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        category_names = [line.strip() for line in f if line.strip()]

    print(f"Creating {len(category_names)} categories from file...\n")

    for name in category_names:
        try:
            category = client.create_category(name)
            print(f"Created category: {category.get('name')} (ID: {category.get('id')})")
        except httpx.HTTPError as e:
            print(f"Failed to create category '{name}': {e}")
