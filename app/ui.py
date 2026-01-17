import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from db.init_db import initialize_database
from services import ingredients as ingredient_service
from services import importer as importer_service
from services import recipes as recipes_service
from services.consolidation import (
    ShoppingItem,
    consolidate_items,
    group_by_aisle,
)


class IngredientDialog(tk.Toplevel):
    def __init__(self, master, title, aisles, units, seasons, ingredient=None):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.aisles = aisles
        self.units = units
        self.seasons = seasons
        self.ingredient = ingredient
        self.result = None
        self.name_var = tk.StringVar(value=ingredient["name"] if ingredient else "")
        self.aisle_var = tk.StringVar()
        self.unit_var = tk.StringVar()
        self.season_vars = {}
        self._build()
        self._populate_defaults()
        self.grab_set()

    def _build(self):
        body = ttk.Frame(self, padding=12)
        body.pack(fill=tk.BOTH, expand=True)

        ttk.Label(body, text="Nom").grid(row=0, column=0, sticky="w")
        ttk.Entry(body, textvariable=self.name_var, width=30).grid(
            row=0, column=1, sticky="ew"
        )

        ttk.Label(body, text="Rayon par défaut").grid(row=1, column=0, sticky="w")
        aisle_names = [aisle["name"] for aisle in self.aisles]
        self.aisle_combo = ttk.Combobox(
            body, textvariable=self.aisle_var, values=aisle_names, state="readonly"
        )
        self.aisle_combo.grid(row=1, column=1, sticky="ew")

        ttk.Label(body, text="Unité").grid(row=2, column=0, sticky="w")
        unit_names = [unit["name"] for unit in self.units]
        self.unit_combo = ttk.Combobox(
            body, textvariable=self.unit_var, values=unit_names, state="readonly"
        )
        self.unit_combo.grid(row=2, column=1, sticky="ew")

        ttk.Label(body, text="Saisons").grid(row=3, column=0, sticky="nw")
        seasons_frame = ttk.Frame(body)
        seasons_frame.grid(row=3, column=1, sticky="w")
        for idx, season in enumerate(self.seasons):
            var = tk.BooleanVar()
            self.season_vars[season["id"]] = var
            ttk.Checkbutton(seasons_frame, text=season["name"], variable=var).grid(
                row=idx // 2, column=idx % 2, sticky="w", padx=4, pady=2
            )

        button_frame = ttk.Frame(body)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(12, 0), sticky="e")
        ttk.Button(button_frame, text="Annuler", command=self.destroy).pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        ttk.Button(button_frame, text="Enregistrer", command=self._on_save).pack(
            side=tk.RIGHT
        )
        body.columnconfigure(1, weight=1)

    def _populate_defaults(self):
        if self.aisles:
            self.aisle_var.set(self.aisles[0]["name"])
        if self.units:
            self.unit_var.set(self.units[0]["name"])
        if self.ingredient:
            aisle_name = next(
                (a["name"] for a in self.aisles if a["id"] == self.ingredient["default_aisle_id"]),
                "",
            )
            unit_name = next(
                (u["name"] for u in self.units if u["id"] == self.ingredient["unit_id"]),
                "",
            )
            self.aisle_var.set(aisle_name)
            self.unit_var.set(unit_name)
            _, seasons = ingredient_service.get_ingredient(self.ingredient["id"])
            for season_id in seasons:
                self.season_vars[season_id].set(True)

    def _on_save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror(
                "Validation", "Le nom de l'ingrédient est obligatoire."
            )
            return
        aisle_id = next(
            (a["id"] for a in self.aisles if a["name"] == self.aisle_var.get()),
            None,
        )
        unit_id = next(
            (u["id"] for u in self.units if u["name"] == self.unit_var.get()),
            None,
        )
        if aisle_id is None or unit_id is None:
            messagebox.showerror(
                "Validation", "Sélectionnez un rayon et une unité valides."
            )
            return
        season_ids = [
            season_id
            for season_id, var in self.season_vars.items()
            if var.get()
        ]
        self.result = {
            "name": name,
            "aisle_id": aisle_id,
            "unit_id": unit_id,
            "season_ids": season_ids,
        }
        self.destroy()


class IngredientsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.tree = None
        self._build()
        self.refresh()

    def _build(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=8, pady=8)
        ttk.Button(toolbar, text="Ajouter", command=self._add).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Modifier", command=self._edit).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(toolbar, text="Supprimer", command=self._delete).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Importer", command=self._import).pack(
            side=tk.LEFT, padx=4
        )

        self.tree = ttk.Treeview(
            self,
            columns=("name", "aisle", "unit", "seasons"),
            show="headings",
            height=14,
        )
        for column, label in [
            ("name", "Nom"),
            ("aisle", "Rayon"),
            ("unit", "Unité"),
            ("seasons", "Saisons"),
        ]:
            self.tree.heading(column, text=label)
            self.tree.column(column, width=140, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for ingredient in ingredient_service.list_ingredients():
            self.tree.insert(
                "",
                tk.END,
                iid=str(ingredient["id"]),
                values=(
                    ingredient["name"],
                    ingredient["aisle_name"],
                    ingredient["unit_name"],
                    ingredient["seasons"] or "",
                ),
            )

    def _add(self):
        aisles = ingredient_service.list_aisles()
        units = ingredient_service.list_units()
        seasons = ingredient_service.list_seasons()
        dialog = IngredientDialog(self, "Ajouter un ingrédient", aisles, units, seasons)
        self.wait_window(dialog)
        if dialog.result:
            ingredient_service.create_ingredient(**dialog.result)
            self.refresh()

    def _edit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(
                "Sélection", "Choisissez un ingrédient à modifier."
            )
            return
        ingredient_id = int(selected[0])
        ingredient, _ = ingredient_service.get_ingredient(ingredient_id)
        if ingredient is None:
            messagebox.showerror("Erreur", "L'ingrédient n'existe plus.")
            self.refresh()
            return
        aisles = ingredient_service.list_aisles()
        units = ingredient_service.list_units()
        seasons = ingredient_service.list_seasons()
        dialog = IngredientDialog(
            self,
            "Modifier l'ingrédient",
            aisles,
            units,
            seasons,
            ingredient=ingredient,
        )
        self.wait_window(dialog)
        if dialog.result:
            ingredient_service.update_ingredient(ingredient_id, **dialog.result)
            self.refresh()

    def _delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(
                "Sélection", "Choisissez un ingrédient à supprimer."
            )
            return
        ingredient_id = int(selected[0])
        if not messagebox.askyesno("Confirmation", "Supprimer cet ingrédient ?"):
            return
        ingredient_service.delete_ingredient(ingredient_id)
        self.refresh()

    def _import(self):
        file_path = filedialog.askopenfilename(
            title="Importer des ingrédients (JSON)",
            filetypes=[("Fichiers JSON", "*.json")],
        )
        if not file_path:
            return
        try:
            imported = importer_service.import_ingredients_from_json(file_path)
        except importer_service.IngredientImportError as exc:
            messagebox.showerror("Import", str(exc))
            return
        except OSError as exc:
            messagebox.showerror(
                "Import", f"Impossible de lire le fichier: {exc}"
            )
            return
        messagebox.showinfo(
            "Import", f"{imported} ingrédient(s) importé(s)."
        )
        self.refresh()


class PlaceholderTab(ttk.Frame):
    def __init__(self, master, label):
        super().__init__(master)
        ttk.Label(self, text=label).pack(padx=16, pady=16)


class RecipeDialog(tk.Toplevel):
    def __init__(self, master, title, recipe=None):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.recipe = recipe
        self.result = None
        self.name_var = tk.StringVar(value=recipe["name"] if recipe else "")
        self.time_var = tk.StringVar()
        self.difficulty_var = tk.StringVar()
        self.instructions_text = None
        self._build()
        self.grab_set()

    def _build(self):
        body = ttk.Frame(self, padding=12)
        body.pack(fill=tk.BOTH, expand=True)

        ttk.Label(body, text="Nom").grid(row=0, column=0, sticky="w")
        ttk.Entry(body, textvariable=self.name_var, width=40).grid(
            row=0, column=1, sticky="ew"
        )

        ttk.Label(body, text="Instructions").grid(row=1, column=0, sticky="nw")
        self.instructions_text = tk.Text(body, height=6, width=50)
        self.instructions_text.grid(row=1, column=1, sticky="ew")

        if self.recipe and self.recipe.get("instructions"):
            self.instructions_text.insert("1.0", self.recipe["instructions"])

        ttk.Label(body, text="Temps").grid(row=2, column=0, sticky="w", pady=(6, 0))
        time_options = recipes_service.TIME_OPTIONS
        self.time_combo = ttk.Combobox(
            body, textvariable=self.time_var, values=time_options, state="readonly"
        )
        self.time_combo.grid(row=2, column=1, sticky="w", pady=(6, 0))

        ttk.Label(body, text="Difficulté").grid(
            row=3, column=0, sticky="w", pady=(6, 0)
        )
        difficulty_options = recipes_service.DIFFICULTY_OPTIONS
        self.difficulty_combo = ttk.Combobox(
            body,
            textvariable=self.difficulty_var,
            values=difficulty_options,
            state="readonly",
        )
        self.difficulty_combo.grid(row=3, column=1, sticky="w", pady=(6, 0))

        self._populate_defaults(time_options, difficulty_options)

        button_frame = ttk.Frame(body)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(12, 0), sticky="e")
        ttk.Button(button_frame, text="Annuler", command=self.destroy).pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        ttk.Button(button_frame, text="Enregistrer", command=self._on_save).pack(
            side=tk.RIGHT
        )
        body.columnconfigure(1, weight=1)

    def _populate_defaults(self, time_options, difficulty_options):
        if self.recipe:
            time_label = self.recipe.get("time_label")
            difficulty = self.recipe.get("difficulty")
            if time_label in time_options:
                self.time_var.set(time_label)
            if difficulty in difficulty_options:
                self.difficulty_var.set(difficulty)
        if not self.time_var.get() and time_options:
            self.time_var.set(time_options[0])
        if not self.difficulty_var.get() and difficulty_options:
            self.difficulty_var.set(difficulty_options[0])

    def _on_save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror(
                "Validation", "Le nom de la recette est obligatoire."
            )
            return
        instructions = self.instructions_text.get("1.0", tk.END).strip()
        time_label = self.time_var.get().strip()
        difficulty = self.difficulty_var.get().strip()
        self.result = {
            "name": name,
            "instructions": instructions,
            "time_label": time_label,
            "difficulty": difficulty,
        }
        self.destroy()


class RecipeIngredientDialog(tk.Toplevel):
    def __init__(self, master, title, ingredient_name, quantity):
        super().__init__(master)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self.quantity_var = tk.StringVar(value=str(quantity))
        self.ingredient_name = ingredient_name
        self._build()
        self.grab_set()

    def _build(self):
        body = ttk.Frame(self, padding=12)
        body.pack(fill=tk.BOTH, expand=True)

        ttk.Label(body, text="Ingrédient").grid(row=0, column=0, sticky="w")
        ttk.Label(body, text=self.ingredient_name).grid(row=0, column=1, sticky="w")

        ttk.Label(body, text="Quantité").grid(row=1, column=0, sticky="w")
        ttk.Entry(body, textvariable=self.quantity_var, width=20).grid(
            row=1, column=1, sticky="w"
        )

        button_frame = ttk.Frame(body)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(12, 0), sticky="e")
        ttk.Button(button_frame, text="Annuler", command=self.destroy).pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        ttk.Button(button_frame, text="Enregistrer", command=self._on_save).pack(
            side=tk.RIGHT
        )

    def _on_save(self):
        quantity_text = self.quantity_var.get().strip().replace(",", ".")
        try:
            quantity = float(quantity_text)
        except ValueError:
            messagebox.showerror(
                "Validation", "La quantité doit être un nombre."
            )
            return
        if quantity <= 0:
            messagebox.showerror(
                "Validation", "La quantité doit être supérieure à zéro."
            )
            return
        self.result = quantity
        self.destroy()


class RecipesTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.tree = None
        self.ingredients_tree = None
        self.selected_recipe_id = None
        self.search_var = tk.StringVar()
        self.ingredient_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.ingredients = []
        self._build()
        self.refresh()

    def _build(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=8, pady=8)
        ttk.Button(toolbar, text="Ajouter", command=self._add).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Modifier", command=self._edit).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(toolbar, text="Supprimer", command=self._delete).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Importer", command=self._import).pack(
            side=tk.LEFT, padx=4
        )

        content = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        content.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        recipes_frame = ttk.Frame(content)
        content.add(recipes_frame, weight=3)

        self.tree = ttk.Treeview(
            recipes_frame,
            columns=("name", "time", "difficulty", "instructions"),
            show="headings",
            height=12,
        )
        self.tree.heading("name", text="Nom")
        self.tree.heading("time", text="Temps")
        self.tree.heading("difficulty", text="Difficulté")
        self.tree.heading("instructions", text="Instructions")
        self.tree.column("name", width=160, anchor="w")
        self.tree.column("time", width=80, anchor="center")
        self.tree.column("difficulty", width=90, anchor="center")
        self.tree.column("instructions", width=320, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_recipe_select)

        ingredients_frame = ttk.Frame(content)
        content.add(ingredients_frame, weight=2)

        ttk.Label(ingredients_frame, text="Ingrédients").pack(
            anchor="w", pady=(0, 6)
        )

        search_frame = ttk.Frame(ingredients_frame)
        search_frame.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(search_frame, text="Recherche").grid(
            row=0, column=0, sticky="w"
        )
        search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var, width=20
        )
        search_entry.grid(row=0, column=1, sticky="ew", padx=(4, 8))
        search_entry.bind("<KeyRelease>", self._on_search_changed)

        ttk.Label(search_frame, text="Ingrédient").grid(
            row=1, column=0, sticky="w", pady=(4, 0)
        )
        self.ingredient_combo = ttk.Combobox(
            search_frame, textvariable=self.ingredient_var, state="readonly", width=24
        )
        self.ingredient_combo.grid(
            row=1, column=1, sticky="ew", padx=(4, 8), pady=(4, 0)
        )

        ttk.Label(search_frame, text="Quantité").grid(
            row=2, column=0, sticky="w", pady=(4, 0)
        )
        ttk.Entry(search_frame, textvariable=self.quantity_var, width=10).grid(
            row=2, column=1, sticky="w", padx=(4, 8), pady=(4, 0)
        )
        ttk.Button(
            search_frame, text="Ajouter", command=self._add_ingredient
        ).grid(row=2, column=2, sticky="e", pady=(4, 0))
        search_frame.columnconfigure(1, weight=1)

        self.ingredients_tree = ttk.Treeview(
            ingredients_frame,
            columns=("ingredient", "quantity", "unit"),
            show="headings",
            height=8,
        )
        self.ingredients_tree.heading("ingredient", text="Ingrédient")
        self.ingredients_tree.heading("quantity", text="Quantité")
        self.ingredients_tree.heading("unit", text="Unité")
        self.ingredients_tree.column("ingredient", width=160, anchor="w")
        self.ingredients_tree.column("quantity", width=80, anchor="e")
        self.ingredients_tree.column("unit", width=80, anchor="w")
        self.ingredients_tree.pack(fill=tk.BOTH, expand=True, pady=(8, 4))

        ingredient_buttons = ttk.Frame(ingredients_frame)
        ingredient_buttons.pack(fill=tk.X)
        ttk.Button(
            ingredient_buttons, text="Modifier", command=self._edit_ingredient
        ).pack(side=tk.LEFT)
        ttk.Button(
            ingredient_buttons, text="Supprimer", command=self._delete_ingredient
        ).pack(side=tk.LEFT, padx=4)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for recipe in recipes_service.list_recipes():
            self.tree.insert(
                "",
                tk.END,
                iid=str(recipe["id"]),
                values=(
                    recipe["name"],
                    recipe.get("time_label") or "",
                    recipe.get("difficulty") or "",
                    recipe["instructions"] or "",
                ),
            )
        self._refresh_ingredient_options()
        self._refresh_recipe_ingredients()

    def _add(self):
        dialog = RecipeDialog(self, "Ajouter une recette")
        self.wait_window(dialog)
        if dialog.result:
            recipes_service.create_recipe(**dialog.result)
            self.refresh()

    def _edit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Sélection", "Choisissez une recette à modifier.")
            return
        recipe_id = int(selected[0])
        recipe = recipes_service.get_recipe(recipe_id)
        if recipe is None:
            messagebox.showerror("Erreur", "La recette n'existe plus.")
            self.refresh()
            return
        dialog = RecipeDialog(self, "Modifier la recette", recipe=recipe)
        self.wait_window(dialog)
        if dialog.result:
            recipes_service.update_recipe(recipe_id, **dialog.result)
            self.refresh()

    def _delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Sélection", "Choisissez une recette à supprimer.")
            return
        recipe_id = int(selected[0])
        if not messagebox.askyesno("Confirmation", "Supprimer cette recette ?"):
            return
        recipes_service.delete_recipe(recipe_id)
        self.refresh()

    def _import(self):
        file_path = filedialog.askopenfilename(
            title="Importer des recettes (JSON)",
            filetypes=[("Fichiers JSON", "*.json")],
        )
        if not file_path:
            return
        try:
            imported = importer_service.import_recipes_from_json(file_path)
        except importer_service.RecipeImportError as exc:
            messagebox.showerror("Import", str(exc))
            return
        except OSError as exc:
            messagebox.showerror(
                "Import", f"Impossible de lire le fichier: {exc}"
            )
            return
        messagebox.showinfo(
            "Import", f"{imported} recette(s) importée(s)."
        )
        self.refresh()

    def _on_recipe_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            self.selected_recipe_id = None
        else:
            self.selected_recipe_id = int(selected[0])
        self._refresh_recipe_ingredients()

    def _refresh_ingredient_options(self):
        self.ingredients = ingredient_service.list_ingredients()
        filtered = self._filter_ingredients(self.search_var.get())
        self.ingredient_combo["values"] = filtered
        if filtered:
            self.ingredient_var.set(filtered[0])
        else:
            self.ingredient_var.set("")

    def _filter_ingredients(self, query: str) -> list[str]:
        cleaned = query.strip().lower()
        if not cleaned:
            return [ingredient["name"] for ingredient in self.ingredients]
        return [
            ingredient["name"]
            for ingredient in self.ingredients
            if cleaned in ingredient["name"].lower()
        ]

    def _on_search_changed(self, _event):
        filtered = self._filter_ingredients(self.search_var.get())
        self.ingredient_combo["values"] = filtered
        if filtered and self.ingredient_var.get() not in filtered:
            self.ingredient_var.set(filtered[0])
        elif not filtered:
            self.ingredient_var.set("")

    def _add_ingredient(self):
        if self.selected_recipe_id is None:
            messagebox.showinfo(
                "Sélection", "Sélectionnez une recette d'abord."
            )
            return
        ingredient_name = self.ingredient_var.get().strip()
        if not ingredient_name:
            messagebox.showerror(
                "Validation", "Choisissez un ingrédient."
            )
            return
        quantity_text = self.quantity_var.get().strip().replace(",", ".")
        try:
            quantity = float(quantity_text)
        except ValueError:
            messagebox.showerror(
                "Validation", "La quantité doit être un nombre."
            )
            return
        if quantity <= 0:
            messagebox.showerror(
                "Validation", "La quantité doit être supérieure à zéro."
            )
            return
        ingredient_id = next(
            (ingredient["id"] for ingredient in self.ingredients
             if ingredient["name"] == ingredient_name),
            None,
        )
        if ingredient_id is None:
            messagebox.showerror(
                "Validation", "Ingrédient introuvable."
            )
            return
        recipes_service.add_recipe_ingredient(
            self.selected_recipe_id, ingredient_id, quantity
        )
        self.quantity_var.set("")
        self._refresh_recipe_ingredients()

    def _refresh_recipe_ingredients(self):
        for item in self.ingredients_tree.get_children():
            self.ingredients_tree.delete(item)
        if self.selected_recipe_id is None:
            return
        for item in recipes_service.list_recipe_ingredients(self.selected_recipe_id):
            self.ingredients_tree.insert(
                "",
                tk.END,
                iid=str(item["id"]),
                values=(
                    item["ingredient_name"],
                    item["quantity"],
                    item["unit_name"],
                ),
            )

    def _edit_ingredient(self):
        selected = self.ingredients_tree.selection()
        if not selected:
            messagebox.showinfo(
                "Sélection", "Choisissez un ingrédient à modifier."
            )
            return
        ingredient_id = int(selected[0])
        item = recipes_service.get_recipe_ingredient(ingredient_id)
        if item is None:
            messagebox.showerror("Erreur", "L'ingrédient n'existe plus.")
            self._refresh_recipe_ingredients()
            return
        dialog = RecipeIngredientDialog(
            self,
            "Modifier la quantité",
            item["ingredient_name"],
            item["quantity"],
        )
        self.wait_window(dialog)
        if dialog.result is not None:
            recipes_service.update_recipe_ingredient(
                ingredient_id, dialog.result
            )
            self._refresh_recipe_ingredients()

    def _delete_ingredient(self):
        selected = self.ingredients_tree.selection()
        if not selected:
            messagebox.showinfo(
                "Sélection", "Choisissez un ingrédient à supprimer."
            )
            return
        ingredient_id = int(selected[0])
        if not messagebox.askyesno(
            "Confirmation", "Supprimer cet ingrédient ?"
        ):
            return
        recipes_service.delete_recipe_ingredient(ingredient_id)
        self._refresh_recipe_ingredients()


class ShoppingListTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.recipes = []
        self.recipe_lookup = {}
        self.selected_recipe_ids = []
        self.manual_items = {}
        self.manual_item_counter = 0
        self.aisles = []
        self.units = []
        self.seasons = []
        self.ingredients = []
        self.ingredient_lookup = {}
        self.available_recipes_list = None
        self.selected_recipes_list = None
        self.recipe_search_var = tk.StringVar()
        self.recipe_time_var = tk.StringVar()
        self.recipe_difficulty_var = tk.StringVar()
        self.recipe_season_var = tk.StringVar()
        self.manual_search_var = tk.StringVar()
        self.manual_season_var = tk.StringVar()
        self.manual_filter_aisle_var = tk.StringVar()
        self.manual_filter_unit_var = tk.StringVar()
        self.manual_ingredient_var = tk.StringVar()
        self.manual_quantity_var = tk.StringVar()
        self.manual_unit_var = tk.StringVar()
        self.manual_aisle_var = tk.StringVar()
        self.recipe_time_combo = None
        self.recipe_difficulty_combo = None
        self.recipe_season_combo = None
        self.manual_ingredient_combo = None
        self.manual_season_combo = None
        self.manual_filter_aisle_combo = None
        self.manual_filter_unit_combo = None
        self.manual_unit_combo = None
        self.manual_aisle_combo = None
        self.manual_items_tree = None
        self.preview_tree = None
        self.grouped_tree = None
        self.selected_ingredient = None
        self._scroll_canvas = None
        self._build()
        self._load_data()

    def _build(self):
        self._scroll_canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self._scroll_canvas.yview
        )
        self._scroll_canvas.configure(yscrollcommand=scrollbar.set)
        self._scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        container = ttk.Frame(self._scroll_canvas, padding=8)
        container_id = self._scroll_canvas.create_window(
            (0, 0), window=container, anchor="nw"
        )
        container.bind(
            "<Configure>",
            lambda _event: self._scroll_canvas.configure(
                scrollregion=self._scroll_canvas.bbox("all")
            ),
        )
        self._scroll_canvas.bind(
            "<Configure>",
            lambda event: self._scroll_canvas.itemconfigure(
                container_id, width=event.width
            ),
        )
        container.bind("<Enter>", self._bind_mousewheel)
        container.bind("<Leave>", self._unbind_mousewheel)

        selection_frame = ttk.LabelFrame(container, text="Sélection")
        selection_frame.pack(fill=tk.X, padx=4, pady=4)
        selection_frame.columnconfigure(0, weight=1)
        selection_frame.columnconfigure(1, weight=1)

        recipes_frame = ttk.Frame(selection_frame)
        recipes_frame.grid(row=0, column=0, sticky="nsew", padx=(4, 8), pady=4)
        recipes_frame.columnconfigure(0, weight=1)
        ttk.Label(recipes_frame, text="Recettes").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        filters_frame = ttk.Frame(recipes_frame)
        filters_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        filters_frame.columnconfigure(1, weight=1)
        filters_frame.columnconfigure(3, weight=1)
        ttk.Label(filters_frame, text="Recherche").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Entry(filters_frame, textvariable=self.recipe_search_var).grid(
            row=0, column=1, sticky="ew", padx=(4, 8)
        )
        ttk.Label(filters_frame, text="Temps").grid(
            row=0, column=2, sticky="w"
        )
        self.recipe_time_combo = ttk.Combobox(
            filters_frame, textvariable=self.recipe_time_var, state="readonly"
        )
        self.recipe_time_combo.grid(row=0, column=3, sticky="ew")
        ttk.Label(filters_frame, text="Difficulté").grid(
            row=1, column=0, sticky="w", pady=(4, 0)
        )
        self.recipe_difficulty_combo = ttk.Combobox(
            filters_frame, textvariable=self.recipe_difficulty_var, state="readonly"
        )
        self.recipe_difficulty_combo.grid(
            row=1, column=1, sticky="ew", padx=(4, 8), pady=(4, 0)
        )
        ttk.Label(filters_frame, text="Saison").grid(
            row=1, column=2, sticky="w", pady=(4, 0)
        )
        self.recipe_season_combo = ttk.Combobox(
            filters_frame, textvariable=self.recipe_season_var, state="readonly"
        )
        self.recipe_season_combo.grid(
            row=1, column=3, sticky="ew", pady=(4, 0)
        )
        self.available_recipes_list = tk.Listbox(
            recipes_frame, height=6, exportselection=False
        )
        self.available_recipes_list.grid(
            row=2, column=0, rowspan=2, sticky="nsew", pady=(4, 0)
        )
        ttk.Button(recipes_frame, text="Ajouter ➜", command=self._add_recipe).grid(
            row=2, column=1, sticky="ew", padx=4, pady=(4, 2)
        )
        ttk.Button(recipes_frame, text="Retirer", command=self._remove_recipe).grid(
            row=3, column=1, sticky="ew", padx=4
        )
        ttk.Label(recipes_frame, text="Sélectionnées").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        self.selected_recipes_list = tk.Listbox(
            recipes_frame, height=6, exportselection=False
        )
        self.selected_recipes_list.grid(
            row=5, column=0, columnspan=2, sticky="nsew", pady=(4, 0)
        )

        manual_frame = ttk.Frame(selection_frame)
        manual_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 4), pady=4)
        manual_frame.columnconfigure(1, weight=1)
        ttk.Label(manual_frame, text="Article manuel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(manual_frame, text="Recherche").grid(
            row=1, column=0, sticky="w", pady=(4, 0)
        )
        ttk.Entry(manual_frame, textvariable=self.manual_search_var).grid(
            row=1, column=1, sticky="ew", pady=(4, 0)
        )
        ttk.Label(manual_frame, text="Saison").grid(
            row=2, column=0, sticky="w", pady=(4, 0)
        )
        self.manual_season_combo = ttk.Combobox(
            manual_frame, textvariable=self.manual_season_var, state="readonly"
        )
        self.manual_season_combo.grid(row=2, column=1, sticky="ew", pady=(4, 0))
        ttk.Label(manual_frame, text="Filtre rayon").grid(
            row=3, column=0, sticky="w", pady=(4, 0)
        )
        self.manual_filter_aisle_combo = ttk.Combobox(
            manual_frame, textvariable=self.manual_filter_aisle_var, state="readonly"
        )
        self.manual_filter_aisle_combo.grid(
            row=3, column=1, sticky="ew", pady=(4, 0)
        )
        ttk.Label(manual_frame, text="Filtre unité").grid(
            row=4, column=0, sticky="w", pady=(4, 0)
        )
        self.manual_filter_unit_combo = ttk.Combobox(
            manual_frame, textvariable=self.manual_filter_unit_var, state="readonly"
        )
        self.manual_filter_unit_combo.grid(
            row=4, column=1, sticky="ew", pady=(4, 0)
        )
        ttk.Label(manual_frame, text="Ingrédient").grid(
            row=5, column=0, sticky="w", pady=(4, 0)
        )
        self.manual_ingredient_combo = ttk.Combobox(
            manual_frame, textvariable=self.manual_ingredient_var
        )
        self.manual_ingredient_combo.grid(
            row=5, column=1, sticky="ew", pady=(4, 0)
        )
        self.manual_ingredient_combo.bind(
            "<<ComboboxSelected>>", self._on_manual_ingredient_selected
        )
        ttk.Label(manual_frame, text="Quantité").grid(
            row=6, column=0, sticky="w", pady=(4, 0)
        )
        ttk.Entry(manual_frame, textvariable=self.manual_quantity_var).grid(
            row=6, column=1, sticky="ew", pady=(4, 0)
        )
        ttk.Label(manual_frame, text="Unité").grid(
            row=7, column=0, sticky="w", pady=(4, 0)
        )
        self.manual_unit_combo = ttk.Combobox(
            manual_frame, textvariable=self.manual_unit_var, state="readonly"
        )
        self.manual_unit_combo.grid(row=7, column=1, sticky="ew", pady=(4, 0))
        ttk.Label(manual_frame, text="Rayon").grid(
            row=8, column=0, sticky="w", pady=(4, 0)
        )
        self.manual_aisle_combo = ttk.Combobox(
            manual_frame, textvariable=self.manual_aisle_var, state="readonly"
        )
        self.manual_aisle_combo.grid(row=8, column=1, sticky="ew", pady=(4, 0))
        ttk.Button(manual_frame, text="Ajouter", command=self._add_manual_item).grid(
            row=9, column=1, sticky="e", pady=(6, 6)
        )
        self.manual_items_tree = ttk.Treeview(
            manual_frame,
            columns=("quantity", "unit", "aisle"),
            show="tree headings",
            height=4,
        )
        self.manual_items_tree.heading("#0", text="Article")
        self.manual_items_tree.heading("quantity", text="Quantité")
        self.manual_items_tree.heading("unit", text="Unité")
        self.manual_items_tree.heading("aisle", text="Rayon")
        self.manual_items_tree.column("#0", width=140, anchor="w")
        self.manual_items_tree.column("quantity", width=80, anchor="center")
        self.manual_items_tree.column("unit", width=80, anchor="center")
        self.manual_items_tree.column("aisle", width=120, anchor="w")
        self.manual_items_tree.grid(
            row=10, column=0, columnspan=2, sticky="nsew", pady=(4, 0)
        )
        ttk.Button(
            manual_frame, text="Supprimer", command=self._remove_manual_item
        ).grid(row=11, column=1, sticky="e", pady=(4, 0))
        self.manual_search_var.trace_add("write", self._on_manual_filter_changed)
        self.manual_season_combo.bind(
            "<<ComboboxSelected>>", self._on_manual_filter_changed
        )
        self.manual_filter_aisle_combo.bind(
            "<<ComboboxSelected>>", self._on_manual_filter_changed
        )
        self.manual_filter_unit_combo.bind(
            "<<ComboboxSelected>>", self._on_manual_filter_changed
        )
        self.manual_ingredient_var.trace_add(
            "write", self._on_manual_ingredient_changed
        )
        self.recipe_search_var.trace_add("write", self._on_recipe_filter_changed)
        self.recipe_time_combo.bind(
            "<<ComboboxSelected>>", self._on_recipe_filter_changed
        )
        self.recipe_difficulty_combo.bind(
            "<<ComboboxSelected>>", self._on_recipe_filter_changed
        )
        self.recipe_season_combo.bind(
            "<<ComboboxSelected>>", self._on_recipe_filter_changed
        )

        preview_frame = ttk.LabelFrame(container, text="Section 1 - Aperçu")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(8, 4))
        self.preview_tree = ttk.Treeview(
            preview_frame,
            columns=("quantity", "unit"),
            show="tree headings",
            height=8,
        )
        self.preview_tree.heading("#0", text="Élément")
        self.preview_tree.heading("quantity", text="Quantité")
        self.preview_tree.heading("unit", text="Unité")
        self.preview_tree.column("#0", width=240, anchor="w")
        self.preview_tree.column("quantity", width=100, anchor="center")
        self.preview_tree.column("unit", width=100, anchor="center")
        self.preview_tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        grouped_frame = ttk.LabelFrame(container, text="Section 2 - Liste par rayon")
        grouped_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 8))
        self.grouped_tree = ttk.Treeview(
            grouped_frame,
            columns=("quantity", "unit"),
            show="tree headings",
            height=8,
        )
        self.grouped_tree.heading("#0", text="Article")
        self.grouped_tree.heading("quantity", text="Quantité")
        self.grouped_tree.heading("unit", text="Unité")
        self.grouped_tree.column("#0", width=240, anchor="w")
        self.grouped_tree.column("quantity", width=100, anchor="center")
        self.grouped_tree.column("unit", width=100, anchor="center")
        self.grouped_tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    def _bind_mousewheel(self, _event):
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, _event):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if not self._scroll_canvas:
            return
        if event.num == 4:
            self._scroll_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._scroll_canvas.yview_scroll(1, "units")
        else:
            self._scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _load_data(self):
        self.aisles = ingredient_service.list_aisles()
        self.units = ingredient_service.list_units()
        self.seasons = ingredient_service.list_seasons()
        self.recipes = recipes_service.list_recipes()
        self.recipe_lookup = {recipe["id"]: recipe for recipe in self.recipes}
        self._refresh_recipe_filter_options()
        self._refresh_recipe_list()
        self._refresh_manual_options()
        self._refresh_previews()

    def _refresh_recipe_filter_options(self):
        season_names = [season["name"] for season in self.seasons]
        self.recipe_time_combo["values"] = ["Tous"] + recipes_service.TIME_OPTIONS
        self.recipe_difficulty_combo["values"] = ["Tous"] + recipes_service.DIFFICULTY_OPTIONS
        self.recipe_season_combo["values"] = ["Toutes"] + season_names
        if not self.recipe_time_var.get():
            self.recipe_time_var.set("Tous")
        if not self.recipe_difficulty_var.get():
            self.recipe_difficulty_var.set("Tous")
        if not self.recipe_season_var.get():
            self.recipe_season_var.set("Toutes")

    def _get_selected_recipe_season_id(self):
        selected_season = self.recipe_season_var.get()
        if not selected_season or selected_season == "Toutes":
            return None
        return next(
            (season["id"] for season in self.seasons if season["name"] == selected_season),
            None,
        )

    def _refresh_recipe_list(self):
        season_id = self._get_selected_recipe_season_id()
        base_recipes = recipes_service.list_recipes(season_id=season_id)
        search_text = self.recipe_search_var.get().strip().lower()
        time_filter = self.recipe_time_var.get()
        difficulty_filter = self.recipe_difficulty_var.get()
        filtered_recipes = []
        for recipe in base_recipes:
            if search_text and search_text not in recipe["name"].lower():
                continue
            if time_filter and time_filter != "Tous" and recipe["time_label"] != time_filter:
                continue
            if (
                difficulty_filter
                and difficulty_filter != "Tous"
                and recipe["difficulty"] != difficulty_filter
            ):
                continue
            filtered_recipes.append(recipe)
            self.recipe_lookup[recipe["id"]] = recipe
        self.recipes = filtered_recipes
        self.available_recipes_list.delete(0, tk.END)
        for recipe in self.recipes:
            self.available_recipes_list.insert(tk.END, recipe["name"])
        self._refresh_selected_recipes_list()

    def _refresh_selected_recipes_list(self):
        self.selected_recipe_ids = [
            recipe_id
            for recipe_id in self.selected_recipe_ids
            if recipe_id in self.recipe_lookup
        ]
        self.selected_recipes_list.delete(0, tk.END)
        for recipe_id in self.selected_recipe_ids:
            self.selected_recipes_list.insert(
                tk.END, self.recipe_lookup[recipe_id]["name"]
            )

    def _refresh_manual_options(self):
        unit_names = [unit["name"] for unit in self.units]
        aisle_names = [aisle["name"] for aisle in self.aisles]
        season_names = [season["name"] for season in self.seasons]
        self.manual_unit_combo["values"] = unit_names
        self.manual_aisle_combo["values"] = aisle_names
        self.manual_season_combo["values"] = ["Toutes"] + season_names
        self.manual_filter_aisle_combo["values"] = ["Tous"] + aisle_names
        self.manual_filter_unit_combo["values"] = ["Toutes"] + unit_names
        if not self.manual_season_var.get():
            self.manual_season_var.set("Toutes")
        if not self.manual_filter_aisle_var.get():
            self.manual_filter_aisle_var.set("Tous")
        if not self.manual_filter_unit_var.get():
            self.manual_filter_unit_var.set("Toutes")
        if unit_names and not self.manual_unit_var.get():
            self.manual_unit_var.set(unit_names[0])
        if aisle_names and not self.manual_aisle_var.get():
            self.manual_aisle_var.set(aisle_names[0])
        self._refresh_ingredient_options()

    def _refresh_ingredient_options(self):
        selected_season = self.manual_season_var.get()
        season_id = next(
            (season["id"] for season in self.seasons if season["name"] == selected_season),
            None,
        )
        self.ingredients = ingredient_service.list_ingredients(season_id=season_id)
        search_text = self.manual_search_var.get().strip().lower()
        aisle_filter = self.manual_filter_aisle_var.get()
        unit_filter = self.manual_filter_unit_var.get()
        filtered = []
        for ingredient in self.ingredients:
            if aisle_filter and aisle_filter != "Tous" and ingredient["aisle_name"] != aisle_filter:
                continue
            if unit_filter and unit_filter != "Toutes" and ingredient["unit_name"] != unit_filter:
                continue
            if search_text and search_text not in ingredient["name"].lower():
                continue
            filtered.append(ingredient)
        self.ingredient_lookup = {
            ingredient["name"]: ingredient for ingredient in self.ingredients
        }
        self.manual_ingredient_combo["values"] = [item["name"] for item in filtered]
        self._sync_selected_ingredient()

    def _on_manual_filter_changed(self, *_):
        self._refresh_ingredient_options()

    def _on_manual_ingredient_selected(self, _event):
        self._sync_selected_ingredient()

    def _on_manual_ingredient_changed(self, *_):
        self._sync_selected_ingredient()

    def _on_recipe_filter_changed(self, *_):
        self._refresh_recipe_list()

    def _sync_selected_ingredient(self):
        name = self.manual_ingredient_var.get().strip()
        ingredient = self.ingredient_lookup.get(name)
        if ingredient:
            self._apply_selected_ingredient(ingredient)
        else:
            self._clear_selected_ingredient()

    def _apply_selected_ingredient(self, ingredient):
        self.selected_ingredient = ingredient
        self.manual_unit_var.set(ingredient["unit_name"])
        self.manual_aisle_var.set(ingredient["aisle_name"])
        self.manual_unit_combo.configure(state="disabled")
        self.manual_aisle_combo.configure(state="disabled")

    def _clear_selected_ingredient(self):
        self.selected_ingredient = None
        self.manual_unit_combo.configure(state="readonly")
        self.manual_aisle_combo.configure(state="readonly")

    def _add_recipe(self):
        selection = self.available_recipes_list.curselection()
        if not selection:
            messagebox.showinfo(
                "Sélection", "Choisissez une recette à ajouter."
            )
            return
        for index in selection:
            recipe_id = self.recipes[index]["id"]
            if recipe_id not in self.selected_recipe_ids:
                self.selected_recipe_ids.append(recipe_id)
        self._refresh_selected_recipes_list()
        self._refresh_previews()

    def _remove_recipe(self):
        selection = self.selected_recipes_list.curselection()
        if not selection:
            messagebox.showinfo(
                "Sélection", "Choisissez une recette à retirer."
            )
            return
        for index in reversed(selection):
            self.selected_recipe_ids.pop(index)
        self._refresh_selected_recipes_list()
        self._refresh_previews()

    def _add_manual_item(self):
        name = self.manual_ingredient_var.get().strip()
        if not name:
            messagebox.showerror(
                "Validation", "Le nom de l'article est obligatoire."
            )
            return
        quantity_text = self.manual_quantity_var.get().strip().replace(",", ".")
        try:
            quantity = float(quantity_text)
        except ValueError:
            messagebox.showerror(
                "Validation", "La quantité doit être un nombre."
            )
            return
        if quantity <= 0:
            messagebox.showerror(
                "Validation", "La quantité doit être supérieure à zéro."
            )
            return
        ingredient = self.ingredient_lookup.get(name)
        if ingredient:
            unit = ingredient["unit_name"]
            aisle = ingredient["aisle_name"]
        else:
            unit = self.manual_unit_var.get().strip()
            aisle = self.manual_aisle_var.get().strip()
            if not unit or not aisle:
                messagebox.showerror(
                    "Validation", "Sélectionnez une unité et un rayon."
                )
                return
        aisle_order = next(
            (aisle_item["sort_order"] for aisle_item in self.aisles
             if aisle_item["name"] == aisle),
            0,
        )
        item_id = f"manual-{self.manual_item_counter}"
        self.manual_item_counter += 1
        self.manual_items[item_id] = {
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "aisle_name": aisle,
            "aisle_order": aisle_order,
        }
        self.manual_items_tree.insert(
            "",
            tk.END,
            iid=item_id,
            text=name,
            values=(self._format_quantity(quantity), unit, aisle),
        )
        self.manual_ingredient_var.set("")
        self.manual_quantity_var.set("")
        self._clear_selected_ingredient()
        self._refresh_previews()

    def _remove_manual_item(self):
        selection = self.manual_items_tree.selection()
        if not selection:
            messagebox.showinfo(
                "Sélection", "Choisissez un article à supprimer."
            )
            return
        for item_id in selection:
            self.manual_items_tree.delete(item_id)
            self.manual_items.pop(item_id, None)
        self._refresh_previews()

    def _refresh_previews(self):
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        for recipe_id in self.selected_recipe_ids:
            recipe = self.recipe_lookup.get(recipe_id)
            if not recipe:
                continue
            parent = self.preview_tree.insert(
                "",
                tk.END,
                text=recipe["name"],
                values=("", ""),
            )
            for ingredient in recipes_service.list_recipe_ingredients_with_metadata(
                recipe_id
            ):
                self.preview_tree.insert(
                    parent,
                    tk.END,
                    text=ingredient["ingredient_name"],
                    values=(
                        self._format_quantity(ingredient["quantity"]),
                        ingredient["unit_name"],
                    ),
                )
            self.preview_tree.item(parent, open=True)
        if self.manual_items:
            manual_parent = self.preview_tree.insert(
                "",
                tk.END,
                text="Articles manuels",
                values=("", ""),
            )
            for item in self.manual_items.values():
                self.preview_tree.insert(
                    manual_parent,
                    tk.END,
                    text=item["name"],
                    values=(
                        self._format_quantity(item["quantity"]),
                        item["unit"],
                    ),
                )
            self.preview_tree.item(manual_parent, open=True)
        self._refresh_grouped_list()

    def _refresh_grouped_list(self):
        for item in self.grouped_tree.get_children():
            self.grouped_tree.delete(item)
        items = self._build_shopping_items()
        if not items:
            return
        consolidated = consolidate_items(items)
        grouped = group_by_aisle(consolidated)
        for aisle_name, aisle_items in grouped:
            parent = self.grouped_tree.insert(
                "",
                tk.END,
                text=aisle_name,
                values=("", ""),
            )
            for item in aisle_items:
                label = item.ingredient_name
                if item.note:
                    label = f"{label} ({item.note})"
                self.grouped_tree.insert(
                    parent,
                    tk.END,
                    text=label,
                    values=(
                        self._format_quantity(item.quantity),
                        item.unit,
                    ),
                )
            self.grouped_tree.item(parent, open=True)

    def _build_shopping_items(self):
        items = []
        for recipe_id in self.selected_recipe_ids:
            for ingredient in recipes_service.list_recipe_ingredients_with_metadata(
                recipe_id
            ):
                items.append(
                    ShoppingItem(
                        ingredient_name=ingredient["ingredient_name"],
                        aisle_name=ingredient["aisle_name"],
                        aisle_order=ingredient["aisle_order"],
                        unit=ingredient["unit_name"],
                        quantity=float(ingredient["quantity"]),
                    )
                )
        for item in self.manual_items.values():
            items.append(
                ShoppingItem(
                    ingredient_name=item["name"],
                    aisle_name=item["aisle_name"],
                    aisle_order=item["aisle_order"],
                    unit=item["unit"],
                    quantity=float(item["quantity"]),
                )
            )
        return items

    @staticmethod
    def _format_quantity(quantity: float) -> str:
        return f"{quantity:g}"


class RecipesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recettes et liste de courses")
        try:
            self.state("zoomed")
        except tk.TclError:
            self.attributes("-zoomed", True)
        initialize_database()
        self._build()

    def _build(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)
        notebook.add(IngredientsTab(notebook), text="Ingrédients")
        notebook.add(RecipesTab(notebook), text="Recettes")
        notebook.add(ShoppingListTab(notebook), text="Liste de courses")


def main():
    app = RecipesApp()
    app.mainloop()


if __name__ == "__main__":
    main()
