"""Mealie API client for fetching categories."""

import argparse
import os

import httpx
from dotenv import load_dotenv

from mealie_toolkit.categorizer_client import CategorizerClient
from mealie_toolkit.mealie_client import MealieClient

# Load environment variables from .env file
load_dotenv()

# Constants
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:12b")


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


def _collect_suggestions(
    categorizer: CategorizerClient,
    recipes: list[dict],
    available_categories: list[str],
    categories: list[dict],
    limit: int | None = None,
) -> list[dict]:
    """
    Collect category suggestions for recipes that don't already have categories.

    Args:
        categorizer: The CategorizerClient instance
        recipes: List of recipes to categorize
        available_categories: List of available category names
        categories: Full list of category objects
        limit: Limit the number of recipes to process (useful for debugging)

    Returns:
        List of suggestions with recipe name, slug, suggested category, and category object
    """
    suggestions = []
    recipes_to_process = recipes[:limit] if limit else recipes
    limit_msg = f" (limited to {limit})" if limit else ""
    print(f"Analyzing recipes and collecting category suggestions{limit_msg}...\n")

    # Build mapping of category name to category object
    category_name_map = {cat.get("name", ""): cat for cat in categories if cat.get("name")}

    skipped_with_categories = 0
    for i, recipe in enumerate(recipes_to_process, 1):
        recipe_name = recipe.get("name", "")
        recipe_slug = recipe.get("slug")
        
        # Skip recipes that already have categories
        existing_categories = recipe.get("recipeCategory", [])
        if existing_categories:
            print(f"[{i}/{len(recipes_to_process)}] [SKIP] {recipe_name} (already has {len(existing_categories)} category/categories)")
            skipped_with_categories += 1
            continue

        try:
            suggested_category = categorizer.categorize_recipe(
                recipe_name, available_categories
            )

            if suggested_category and suggested_category in category_name_map:
                category_obj = category_name_map[suggested_category]
                suggestions.append({
                    "recipe_name": recipe_name,
                    "recipe_slug": recipe_slug,
                    "suggested_category": suggested_category,
                    "category": category_obj
                })
                print(f"[{i}/{len(recipes_to_process)}] [OK] {recipe_name} -> {suggested_category}")
            else:
                print(f"[{i}/{len(recipes_to_process)}] [-] {recipe_name} (no valid category found)")

        except Exception as e:
            print(f"[{i}/{len(recipes_to_process)}] [ERR] Error processing {recipe_name}: {e}")

    if skipped_with_categories > 0:
        print(f"\n[SKIP] {skipped_with_categories} recipe/recipes already have categories and were skipped\n")

    return suggestions


def _display_suggestions(suggestions: list[dict]) -> None:
    """
    Display all collected suggestions to the user.

    Args:
        suggestions: List of suggestions to display
    """
    print(f"\n{'=' * 80}")
    print(f"Found {len(suggestions)} recipes to categorize:\n")

    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i:3d}. {suggestion['recipe_name']:<50} → {suggestion['suggested_category']}")

    print(f"\n{'=' * 80}\n")


def _get_user_confirmation() -> bool:
    """
    Ask user for confirmation to apply categorizations.

    Returns:
        True if user confirms, False otherwise
    """
    while True:
        response = input("Apply these categorizations? (yes/no): ").strip().lower()
        if response in ("yes", "y"):
            return True
        elif response in ("no", "n"):
            return False
        else:
            print("Please enter 'yes' or 'no'.")


def _apply_categorizations(client: MealieClient, suggestions: list[dict]) -> int:
    """
    Apply categorizations to recipes.

    Args:
        client: The MealieClient instance
        suggestions: List of suggestions to apply

    Returns:
        Number of successfully categorized recipes
    """
    print("\nApplying categorizations...\n")
    applied_count = 0

    for suggestion in suggestions:
        try:
            client.update_recipe_categories(
                suggestion["recipe_slug"],
                [suggestion["category"]]
            )
            print(f"[OK] {suggestion['recipe_name']} -> {suggestion['suggested_category']}")
            applied_count += 1
        except Exception as e:
            print(f"[ERR] Failed to categorize {suggestion['recipe_name']}: {e}")

    return applied_count


def auto_categorize_recipes(client: MealieClient, categories: list[dict] | None = None, limit: int | None = None) -> None:
    """
    Auto-categorize recipes using Ollama AI with user confirmation.

    Args:
        client: The MealieClient instance
        categories: List of available categories (deprecated, fetched internally)
        limit: Limit the number of recipes to process (useful for debugging)
    """
    # Initialize the categorizer client with Ollama
    categorizer = CategorizerClient(ollama_url=OLLAMA_URL, model=OLLAMA_MODEL)

    print("Fetching all categories...")
    categories = client.fetch_categories()
    print(f"Retrieved {len(categories)} categories")

    # Get available category names and mapping
    available_categories = [cat.get("name", "") for cat in categories if cat.get("name")]
    category_ids_map = {cat.get("name", ""): cat.get("id") for cat in categories}

    print("Fetching all recipes...")
    recipes = client.fetch_recipes()
    print(f"Retrieved {len(recipes)} recipes\n")

    # Collect suggestions
    suggestions = _collect_suggestions(
        categorizer, recipes, available_categories, categories, limit=limit
    )

    if not suggestions:
        print("No categories suggested for any recipes.")
        return

    # Display and confirm
    _display_suggestions(suggestions)

    if not _get_user_confirmation():
        print("Categorization cancelled.")
        return

    # Apply categorizations
    applied_count = _apply_categorizations(client, suggestions)
    print(f"\nResults: {applied_count}/{len(suggestions)} recipes categorized")



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


def main():
    """Example usage of the MealieClient."""
    parser = argparse.ArgumentParser(
        description="Fetch data from a Mealie instance"
    )
    subparsers = parser.add_subparsers(
        dest="command",
        help="Command to execute",
        required=True,
    )

    # Add fetch-categories subcommand
    subparsers.add_parser(
        "fetch-categories",
        help="Fetch all categories from the Mealie instance",
    )

    # Add fetch-recipes subcommand
    subparsers.add_parser(
        "fetch-recipes",
        help="Fetch all recipes from the Mealie instance",
    )

    # Add auto-categorize-recipes subcommand
    categorize_parser = subparsers.add_parser(
        "auto-categorize-recipes",
        help="Auto-categorize recipes using Ollama AI suggestions",
    )
    categorize_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of recipes to categorize (useful for debugging)",
    )

    # Add populate-categories subcommand
    populate_parser = subparsers.add_parser(
        "populate-categories",
        help="Populate categories from a file (one category per line)",
    )
    populate_parser.add_argument(
        "--file",
        required=True,
        help="Path to the file containing category names",
    )

    args = parser.parse_args()

    # Load configuration from environment variables
    mealie_url = os.getenv("MEALIE_URL", "https://demo.mealie.io")
    api_token = os.getenv("MEALIE_API_TOKEN")

    # Initialize the client
    client = MealieClient(mealie_url, api_token=api_token)

    try:
        if args.command == "fetch-recipes":
            print(f"Fetching recipes from {mealie_url}...")
            recipes = client.fetch_recipes()
            print_recipes(recipes)

        elif args.command == "fetch-categories":
            print(f"Fetching categories from {mealie_url}...")
            categories = client.fetch_categories()
            print_categories(categories, client)

        elif args.command == "auto-categorize-recipes":
            print(f"Auto-categorizing recipes from {mealie_url}...")
            auto_categorize_recipes(client, limit=args.limit)

        elif args.command == "populate-categories":
            print(f"Populating categories from file...")
            populate_categories(client, args.file)

    except httpx.HTTPError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
