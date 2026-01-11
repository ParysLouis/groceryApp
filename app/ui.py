import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from db.init_db import initialize_database
from services import ingredients as ingredient_service
from services import importer as importer_service


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
        notebook.add(
            PlaceholderTab(notebook, "Le créateur de recettes arrive bientôt."),
            text="Recettes",
        )
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
