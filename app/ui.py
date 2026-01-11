import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from db.init_db import initialize_database
from services import ingredients as ingredient_service
from services import importer as importer_service
from services import recipes as recipes_service


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

        button_frame = ttk.Frame(body)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(12, 0), sticky="e")
        ttk.Button(button_frame, text="Annuler", command=self.destroy).pack(
            side=tk.RIGHT, padx=(8, 0)
        )
        ttk.Button(button_frame, text="Enregistrer", command=self._on_save).pack(
            side=tk.RIGHT
        )
        body.columnconfigure(1, weight=1)

    def _on_save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror(
                "Validation", "Le nom de la recette est obligatoire."
            )
            return
        instructions = self.instructions_text.get("1.0", tk.END).strip()
        self.result = {
            "name": name,
            "instructions": instructions,
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
            columns=("name", "instructions"),
            show="headings",
            height=12,
        )
        self.tree.heading("name", text="Nom")
        self.tree.heading("instructions", text="Instructions")
        self.tree.column("name", width=200, anchor="w")
        self.tree.column("instructions", width=420, anchor="w")
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
                values=(recipe["name"], recipe["instructions"] or ""),
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


class RecipesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recettes et liste de courses")
        self.geometry("800x500")
        initialize_database()
        self._build()

    def _build(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)
        notebook.add(IngredientsTab(notebook), text="Ingrédients")
        notebook.add(RecipesTab(notebook), text="Recettes")
        notebook.add(
            PlaceholderTab(
                notebook, "Le créateur de liste de courses arrive bientôt."
            ),
            text="Liste de courses",
        )


def main():
    app = RecipesApp()
    app.mainloop()


if __name__ == "__main__":
    main()
