"""Categorizer client for using Ollama to categorize recipes."""

from typing import Optional

import httpx


class OllamaClient:
    """Client for using Ollama to categorize recipes."""

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "gemma3:12b",
    ):
        """
        Initialize the Categorizer client.

        Args:
            ollama_url: The base URL of the Ollama instance (default: http://localhost:11434)
            model: The model name to use for categorization (default: gemma3:12b)
        """
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model

    def categorize_recipe(
        self,
        recipe_name: str,
        available_categories: list[str],
    ) -> str:
        """
        Use Ollama to categorize a recipe based on its name.

        Args:
            recipe_name: The name of the recipe to categorize
            available_categories: List of available category names to choose from

        Returns:
            The category name that best fits the recipe name

        Raises:
            httpx.HTTPError: If the API request fails
            ValueError: If Ollama response is invalid
        """
        categories_str = ", ".join(available_categories)
        prompt = f"""Given the recipe name "{recipe_name}", select which of these categories it belongs to: {categories_str}

Return only the category name that best fits the recipe name
Return only the category name, no other text
"""

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()

        if "response" not in data:
            raise ValueError("Invalid response from Ollama")

        result_text = data["response"].strip()

        # Parse the response
        if result_text.upper() == "NONE":
            return ""

        return result_text

    def check_tag_applies(self, recipe: dict, tag: str) -> bool:
        """
        Use Ollama to check if a tag applies to a recipe.

        Args:
            recipe: The recipe dictionary with full details
            tag: The tag to check (e.g., "vegetarian", "quick", "spicy")

        Returns:
            True if the tag applies to the recipe, False otherwise

        Raises:
            httpx.HTTPError: If the API request fails
            ValueError: If Ollama response is invalid
        """
        # Extract recipe details
        recipe_name = recipe.get("name", "Unknown")
        description = recipe.get("description", "")
        ingredients = recipe.get("recipeIngredient", [])
        
        # Build ingredient list
        ingredient_text = ""
        if ingredients:
            ingredient_names = []
            for ing in ingredients:
                if isinstance(ing, dict):
                    ing_name = ing.get("ingredient", {}).get("name", "")
                    if ing_name:
                        ingredient_names.append(ing_name)
            if ingredient_names:
                ingredient_text = f"\nIngredients: {', '.join(ingredient_names[:15])}"  # Limit to first 15
        
        # Build the prompt with full recipe details
        prompt = f"""Based on this recipe, does it appear to be {tag}?

Recipe Name: {recipe_name}
Description: {description}{ingredient_text}

Answer with only "YES" or "NO", nothing else.
"""

        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()

        if "response" not in data:
            raise ValueError("Invalid response from Ollama")

        result_text = data["response"].strip().upper()

        # Parse the response
        return result_text.startswith("YES")
