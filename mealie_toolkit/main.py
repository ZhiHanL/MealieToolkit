"""Command-line interface for the Mealie Toolkit."""

import argparse
import os

import httpx
from dotenv import load_dotenv

from mealie_toolkit.mealie_client import MealieClient
from mealie_toolkit.utils import print_recipes, print_categories, populate_categories
from mealie_toolkit.categorize import auto_categorize_recipes
from mealie_toolkit.tagging import auto_tag_recipes

# Load environment variables from .env file
load_dotenv()

def main():
    """Main CLI entry point for the Mealie Toolkit."""
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

    # Add auto-tag subcommand
    tag_parser = subparsers.add_parser(
        "auto-tag",
        help="Auto-tag recipes based on a given tag (e.g., vegetarian, quick, spicy)",
    )
    tag_parser.add_argument(
        "--tag",
        required=True,
        help="The tag to check for (e.g., 'vegetarian', 'quick', 'spicy')",
    )
    tag_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of recipes to check (useful for debugging)",
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

        elif args.command == "auto-tag":
            print(f"Auto-tagging recipes with '{args.tag}' tag from {mealie_url}...")
            auto_tag_recipes(client, args.tag, limit=args.limit)

    except httpx.HTTPError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
