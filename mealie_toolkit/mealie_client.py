"""Mealie API client for interacting with Mealie instances."""

from typing import Optional

import httpx


class MealieClient:
    """Client for interacting with the Mealie API."""

    def __init__(self, base_url: str, api_token: Optional[str] = None):
        """
        Initialize the Mealie client.

        Args:
            base_url: The base URL of the Mealie instance (e.g., https://demo.mealie.io)
            api_token: Optional API token for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.headers = {}
        if api_token:
            self.headers["Authorization"] = f"Bearer {api_token}"

    def fetch_categories(self) -> list[dict]:
        """
        Fetch all categories from the Mealie instance with pagination support.

        Returns:
            List of category dictionaries containing category data

        Raises:
            httpx.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/api/organizers/categories"
        all_categories = []
        page = 1
        page_size = 100

        with httpx.Client() as client:
            while True:
                params = {"page": page, "pageSize": page_size}
                response = client.get(url, headers=self.headers, params=params)
                response.raise_for_status()

                data = response.json()

                # Handle pagination response
                if isinstance(data, dict) and "items" in data:
                    items = data["items"]
                    if not items:
                        # No more items, pagination complete
                        break
                    all_categories.extend(items)

                    # Check if there are more pages
                    total = data.get("total", 0)
                    if len(all_categories) >= total:
                        break
                    page += 1

                # Handle direct list response
                elif isinstance(data, list):
                    all_categories.extend(data)
                    break

        return all_categories

    def fetch_category_by_id(self, category_id: str) -> dict:
        """
        Fetch a specific category by ID.

        Args:
            category_id: The ID of the category to fetch

        Returns:
            Category data dictionary

        Raises:
            httpx.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/api/organizers/categories/{category_id}"

        with httpx.Client() as client:
            response = client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def fetch_category_by_slug(self, category_slug: str) -> dict:
        """
        Fetch a specific category by slug.

        Args:
            category_slug: The slug of the category to fetch

        Returns:
            Category data dictionary

        Raises:
            httpx.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/api/organizers/categories/slug/{category_slug}"

        with httpx.Client() as client:
            response = client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def fetch_recipes(self) -> list[dict]:
        """
        Fetch all recipes from the Mealie instance with pagination support.

        Returns:
            List of recipe dictionaries containing recipe data

        Raises:
            httpx.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/api/recipes"
        all_recipes = []
        page = 1
        page_size = 100

        with httpx.Client() as client:
            while True:
                params = {"page": page, "pageSize": page_size}
                response = client.get(url, headers=self.headers, params=params)
                response.raise_for_status()

                data = response.json()

                # Handle pagination response
                if isinstance(data, dict) and "items" in data:
                    items = data["items"]
                    if not items:
                        # No more items, pagination complete
                        break
                    all_recipes.extend(items)

                    # Check if there are more pages
                    total = data.get("total", 0)
                    if len(all_recipes) >= total:
                        break
                    page += 1

                # Handle direct list response
                elif isinstance(data, list):
                    all_recipes.extend(data)
                    break

        return all_recipes

    def update_recipe_categories(self, recipe_slug: str, categories: list) -> dict:
        """
        Update categories for a recipe.

        Args:
            recipe_slug: The slug of the recipe to update
            categories: List of category objects or IDs to assign to the recipe
                       Can be list of dicts with 'id'/'name'/'slug' or list of IDs

        Returns:
            Updated recipe data dictionary

        Raises:
            httpx.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/api/recipes/{recipe_slug}"
        
        # Build proper category payloads - ensure id, name, and slug are included
        category_payloads = []
        for cat in categories:
            if isinstance(cat, dict):
                # If it's already a dict with id, name, slug, use it as-is
                if "id" in cat and "name" in cat and "slug" in cat:
                    category_payloads.append({
                        "id": cat["id"],
                        "name": cat["name"],
                        "slug": cat["slug"]
                    })
                # If it only has id, we'd need to fetch the details
                elif "id" in cat:
                    category_payloads.append(cat)
                else:
                    category_payloads.append(cat)
            else:
                # Assume it's an ID string
                category_payloads.append({"id": cat})
        
        payload = {"recipeCategory": category_payloads}

        with httpx.Client() as client:
            response = client.patch(url, json=payload, headers=self.headers)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                # Include response body in error for debugging
                error_detail = ""
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text
                raise httpx.HTTPStatusError(
                    f"{e.response.status_code} {e.response.reason_phrase}: {error_detail}",
                    request=e.request,
                    response=e.response,
                ) from e
            return response.json()

    def create_category(self, name: str, description: Optional[str] = None) -> dict:
        """
        Create a new category in the Mealie instance.

        Args:
            name: The name of the category
            description: Optional description of the category

        Returns:
            Created category data dictionary

        Raises:
            httpx.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/api/organizers/categories"
        payload = {"name": name}
        if description:
            payload["description"] = description

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def fetch_tags(self) -> list[dict]:
        """
        Fetch all tags from the Mealie instance.

        Returns:
            List of tag dictionaries

        Raises:
            httpx.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/api/organizers/tags"

        with httpx.Client() as client:
            response = client.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            # Handle paginated response
            if isinstance(data, dict) and "items" in data:
                return data.get("items", [])
            # Handle direct list response
            elif isinstance(data, list):
                return data
            return []

    def add_recipe_tag(self, recipe_slug: str, tag_name: str) -> dict:
        """
        Add a tag to a recipe.

        Args:
            recipe_slug: The slug of the recipe to tag
            tag_name: The name of the tag to add

        Returns:
            Updated recipe data dictionary

        Raises:
            httpx.HTTPError: If the API request fails
        """
        # Fetch all tags from Mealie to find the matching tag
        all_tags = self.fetch_tags()
        tag_to_add = None
        
        for tag in all_tags:
            if tag.get("name", "").lower() == tag_name.lower():
                tag_to_add = tag
                break
        
        if not tag_to_add:
            raise ValueError(f"Tag '{tag_name}' not found in Mealie instance")
        
        # Add the full tag object from Mealie to existing tags
        updated_tags = [tag_to_add]
        
        url = f"{self.base_url}/api/recipes/{recipe_slug}"
        payload = {"tags": updated_tags}

        with httpx.Client() as client:
            response = client.patch(url, json=payload, headers=self.headers)
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                # Include response body in error for debugging
                error_detail = ""
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text
                raise httpx.HTTPStatusError(
                    f"{e.response.status_code} {e.response.reason_phrase}: {error_detail}",
                    request=e.request,
                    response=e.response,
                ) from e
            return response.json()
