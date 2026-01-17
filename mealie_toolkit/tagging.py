"""Auto-tagging logic for recipes using Ollama AI."""

import os

from mealie_toolkit.ollama_client import OllamaClient
from mealie_toolkit.mealie_client import MealieClient


# Constants
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:12b")


def _collect_tag_suggestions(
    categorizer: OllamaClient,
    recipes: list[dict],
    tag: str,
    limit: int | None = None,
) -> list[dict]:
    """
    Collect recipes that match the given tag.

    Args:
        categorizer: The OllamaClient instance
        recipes: List of recipes to check
        tag: The tag to check for
        limit: Limit the number of recipes to process (useful for debugging)

    Returns:
        List of matching recipes with recipe name and slug
    """
    matching_recipes = []
    recipes_to_process = recipes[:limit] if limit else recipes
    limit_msg = f" (limited to {limit})" if limit else ""
    print(f"Checking recipes for '{tag}' tag{limit_msg}...\n")

    for i, recipe in enumerate(recipes_to_process, 1):
        recipe_name = recipe.get("name", "")

        try:
            if categorizer.check_tag_applies(recipe, tag):
                matching_recipes.append({
                    "recipe_name": recipe_name,
                    "recipe_slug": recipe.get("slug"),
                })
                print(f"[{i}/{len(recipes_to_process)}] [OK] {recipe_name} (matches '{tag}')")
            else:
                print(f"[{i}/{len(recipes_to_process)}] [-] {recipe_name} (does not match '{tag}')")

        except Exception as e:
            print(f"[{i}/{len(recipes_to_process)}] [ERR] Error processing {recipe_name}: {e}")

    return matching_recipes


def _display_tag_suggestions(matching_recipes: list[dict], tag: str) -> None:
    """
    Display all recipes that match the given tag.

    Args:
        matching_recipes: List of matching recipes to display
        tag: The tag name
    """
    print(f"\n{'=' * 80}")
    print(f"Found {len(matching_recipes)} recipes to tag with '{tag}':\n")

    for i, recipe in enumerate(matching_recipes, 1):
        print(f"{i:3d}. {recipe['recipe_name']}")

    print(f"\n{'=' * 80}\n")


def _get_tag_confirmation(tag: str) -> bool:
    """
    Ask user for confirmation to apply the tag.

    Args:
        tag: The tag name

    Returns:
        True if user confirms, False otherwise
    """
    while True:
        response = input(f"Apply tag '{tag}' to these recipes? (yes/no): ").strip().lower()
        if response in ("yes", "y"):
            return True
        elif response in ("no", "n"):
            return False
        else:
            print("Please enter 'yes' or 'no'.")


def _apply_tags(client: MealieClient, matching_recipes: list[dict], tag: str) -> int:
    """
    Apply the tag to matching recipes.

    Args:
        client: The MealieClient instance
        matching_recipes: List of recipes to tag
        tag: The tag to apply

    Returns:
        Number of successfully tagged recipes
    """
    print("\nApplying tags...\n")
    tagged_count = 0

    for recipe in matching_recipes:
        try:
            client.add_recipe_tag(recipe["recipe_slug"], tag)
            print(f"[OK] {recipe['recipe_name']} -> {tag}")
            tagged_count += 1
        except Exception as e:
            print(f"[ERR] Failed to tag {recipe['recipe_name']}: {e}")

    return tagged_count


def auto_tag_recipes(client: MealieClient, tag: str, limit: int | None = None) -> None:
    """
    Auto-tag recipes based on a given tag using Ollama AI with user confirmation.

    Args:
        client: The MealieClient instance
        tag: The tag to check (e.g., "vegetarian", "quick", "spicy")
        limit: Limit the number of recipes to process (useful for debugging)
    """
    # Initialize the categorizer client with Ollama
    categorizer = OllamaClient(ollama_url=OLLAMA_URL, model=OLLAMA_MODEL)

    print("Fetching all recipes...")
    recipes = client.fetch_recipes()
    print(f"Retrieved {len(recipes)} recipes\n")

    # Collect matching recipes
    matching_recipes = _collect_tag_suggestions(
        categorizer, recipes, tag, limit=limit
    )

    if not matching_recipes:
        print("\nNo recipes matched the tag.")
        return

    # Display results and get confirmation
    _display_tag_suggestions(matching_recipes, tag)

    if not _get_tag_confirmation(tag):
        print("Tagging cancelled.")
        return

    # Apply the tags
    tagged_count = _apply_tags(client, matching_recipes, tag)
    print(f"\nResults: {tagged_count}/{len(matching_recipes)} recipes tagged")
