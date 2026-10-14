"""Construction of the application panels and reusable widgets."""

import tkinter as tk
from typing import List

import customtkinter as ctk

from .constants import (
    BADGE_BG,
    BADGE_TEXT,
    BLUE,
    BLUE_HOVER,
    BORDER_SOFT,
    CANVAS,
    CARD,
    CARD_PADDING,
    CARD_RADIUS,
    CONTROL_BG,
    CONTROL_HOVER,
    CONTROL_HOVER_STRONG,
    CONTROL_RADIUS,
    DISABLED_TEXT,
    DISTANCE_UPDATED,
    FONT_BODY,
    FONT_CAPTION,
    FONT_FAMILY,
    FONT_SECTION,
    FONT_TITLE,
    INK,
    LINE,
    MARKER_RADIUS,
    MUTED,
    NODE_ACTIVE,
    NODE_START,
    NODE_TARGET,
    PANEL_BG,
    PATH_BLUE,
    PURPLE,
    SELECTOR_BG,
    SELECTOR_BUTTON,
    SELECTOR_HOVER,
    SOFT_TEXT,
    SPACE,
    STATUS_RADIUS,
    STRONG_MUTED,
    WHITE,
)

class PanelsMixin:
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.header = header
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 12))
        header.grid_columnconfigure(0, weight=1)

        self.header_title = ctk.CTkLabel(
            header,
            text="Dijkstra Lab",
            text_color=INK,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_TITLE, weight="bold"),
        )
        self.header_title.grid(row=0, column=0, sticky="w")
        self.header_subtitle = ctk.CTkLabel(
            header,
            text="Visualisez la différence entre recalcul complet et mise à jour dynamique.",
            text_color=MUTED,
            font=ctk.CTkFont(size=FONT_BODY + 2),
        )
        self.header_subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))
        self.header_badge = ctk.CTkLabel(
            header,
            text="MODE DÉMONSTRATION",
            text_color=BADGE_TEXT,
            fg_color=BADGE_BG,
            corner_radius=CONTROL_RADIUS,
            padx=11,
            pady=6,
            font=ctk.CTkFont(size=FONT_CAPTION, weight="bold"),
        )
        self.header_badge.grid(row=0, column=1, rowspan=2, sticky="e")
        self.header.grid_columnconfigure(1, weight=0)

    def _build_workspace(self) -> None:
        workspace = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.workspace = workspace
        workspace.grid(row=1, column=0, sticky="nsew", padx=30)
        workspace.grid_columnconfigure(0, weight=64, uniform="dashboard")
        workspace.grid_columnconfigure(1, weight=36, uniform="dashboard")
        workspace.grid_rowconfigure(0, weight=1)

        graph_card = self._card(workspace)
        self.graph_card = graph_card
        graph_card.grid(row=0, column=0, sticky="nsew", padx=(0, 9))
        graph_card.grid_columnconfigure(0, weight=1)
        graph_card.grid_rowconfigure(4, weight=1, minsize=420)
        self._section_heading(
            graph_card, "01  ·  GRAPHE ORIENTÉ ET PONDÉRÉ", "Graphe actif"
        )
        self.graph_subtitle = ctk.CTkLabel(
            graph_card,
            text="Le chemin sélectionné et les étapes de calcul sont mis en évidence.",
            text_color=MUTED,
            font=ctk.CTkFont(size=FONT_BODY),
            anchor="w",
        )
        self.graph_subtitle.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 12))
        self.graph_canvas = tk.Canvas(
            graph_card,
            bg=CANVAS,
            highlightthickness=0,
            relief="flat",
        )
        self.graph_canvas.grid(row=4, column=0, sticky="nsew", padx=18, pady=(0, 10))
        self.graph_canvas.bind("<Configure>", self._draw_graph)

        legend = ctk.CTkFrame(graph_card, fg_color="transparent")
        self.legend_frame = legend
        legend.grid(row=5, column=0, sticky="ew", padx=22, pady=(2, 0))
        self.legend_items = [
            self._legend_item(legend, "Départ", NODE_START, 0),
            self._legend_item(legend, "Arrivée", NODE_TARGET, 1, outlined=True),
            self._legend_item(legend, "Chemin optimal", PATH_BLUE, 2),
            self._legend_item(legend, "Sommet actif", NODE_ACTIVE, 3, outlined=True),
            self._legend_item(
                legend, "Distance mise à jour", DISTANCE_UPDATED, 4, outlined=True
            ),
        ]

        self.graph_summary = ctk.CTkLabel(
            graph_card,
            text="",
            text_color=MUTED,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
        )
        self.graph_summary.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=CARD_PADDING,
            pady=(SPACE, SPACE * 2),
        )
        self.graph_play_status = ctk.CTkLabel(
            graph_card,
            text="Étape prête à explorer.",
            text_color=MUTED,
            font=ctk.CTkFont(size=FONT_CAPTION),
            anchor="w",
        )
        self.graph_play_status.grid(
            row=7, column=0, sticky="ew", padx=22, pady=(0, 14)
        )

        controls = self._card(workspace)
        self.controls_card = controls
        controls.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        controls.grid_columnconfigure((0, 1), weight=1, uniform="edit-controls")
        self._section_heading(
            controls, "PARCOURS", "Configurez l’expérience", columnspan=2
        )

        self.controls_subtitle = ctk.CTkLabel(
            controls,
            text="Choisissez un trajet, modifiez une arête et comparez.",
            text_color=MUTED,
            font=ctk.CTkFont(size=11),
            justify="left",
            anchor="w",
            wraplength=280,
        )
        self.controls_subtitle.grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 8)
        )
        self.endpoint_selectors = ctk.CTkFrame(controls, fg_color="transparent")
        self.endpoint_selectors.grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 10)
        )
        self.endpoint_selectors.grid_columnconfigure(
            (0, 1), weight=1, uniform="endpoints"
        )
        self._selector(self.endpoint_selectors, "Départ", self.start_node, 0, SOFT_TEXT)
        self._selector(self.endpoint_selectors, "Arrivée", self.target_node, 1, PURPLE)
        ctk.CTkLabel(
            controls,
            text="2. Modifier une arête",
            text_color=INK,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).grid(row=4, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 6))
        ctk.CTkLabel(
            controls,
            text="Action",
            text_color=MUTED,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        ).grid(row=5, column=0, sticky="w", padx=(18, 8), pady=(0, 4))
        ctk.CTkOptionMenu(
            controls,
            variable=self.change_type,
            values=["Modifier le poids", "Supprimer une arête", "Ajouter une arête"],
            command=self._on_change_type,
            fg_color=CONTROL_BG,
            button_color=CONTROL_HOVER,
            button_hover_color=CONTROL_HOVER,
            text_color=INK,
            dropdown_text_color=INK,
            height=34,
        ).grid(row=5, column=1, sticky="ew", padx=(0, 18), pady=(0, 4))

        self.edge_label = ctk.CTkLabel(
            controls,
            text="Arête",
            text_color=MUTED,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        self.edge_label.grid(row=6, column=0, sticky="w", padx=(18, 8), pady=(0, 4))
        self.edge_menu = ctk.CTkOptionMenu(
            controls,
            variable=self.edge_selection,
            values=[],
            fg_color=CONTROL_BG,
            button_color=CONTROL_HOVER,
            button_hover_color=CONTROL_HOVER,
            text_color=INK,
            dropdown_text_color=INK,
        )
        self.edge_menu.grid(row=6, column=1, sticky="ew", padx=(0, 18), pady=(0, 4))

        self.weight_label = ctk.CTkLabel(
            controls,
            text="Nouveau poids",
            text_color=MUTED,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        self.weight_label.grid(row=7, column=0, sticky="w", padx=(18, 8), pady=(0, 5))
        self.weight_entry = ctk.CTkEntry(
            controls,
            textvariable=self.new_weight,
            placeholder_text="Ex. 5.5",
            height=36,
        )
        self.weight_entry.grid(row=7, column=1, sticky="ew", padx=(0, 18), pady=(0, 5))

        self.apply_button = ctk.CTkButton(
            controls,
            text="Appliquer",
            command=self._apply_change,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            text_color=WHITE,
            height=42,
            corner_radius=STATUS_RADIUS,
            font=ctk.CTkFont(size=FONT_BODY + 1, weight="bold"),
        )
        self.apply_button.grid(
            row=8, column=0, columnspan=2, sticky="ew", padx=18, pady=(2, 7)
        )
        self.change_status = ctk.CTkLabel(
            controls,
            text="Prêt · les résultats suivent chaque action.",
            text_color=MUTED,
            font=ctk.CTkFont(size=FONT_CAPTION + 1),
            justify="left",
            anchor="w",
            wraplength=280,
        )
        self.change_status.grid(
            row=9, column=0, columnspan=2, sticky="ew", padx=18, pady=(0, 5)
        )
        self._refresh_edge_options()

    def _build_comparison(self) -> None:
        comparison = ctk.CTkFrame(self.controls_card, fg_color="transparent")
        self.comparison_frame = comparison
        comparison.grid(row=11, column=0, columnspan=2, sticky="ew", padx=12, pady=(4, 10))
        comparison.grid_columnconfigure((0, 1), weight=1)
        self.comparison_heading = ctk.CTkLabel(
            comparison,
            text="3. Comparer les résultats",
            text_color=INK,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.comparison_heading.grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 3)
        )
        self.comparison_explainer = ctk.CTkLabel(
            comparison,
            text=(
                "Temps et travail : finalisations/relâchements côté classique, "
                "réparations/valeurs rhs côté dynamique."
            ),
            text_color=MUTED,
            font=ctk.CTkFont(size=10),
            justify="left",
            anchor="w",
            wraplength=350,
        )
        self.comparison_explainer.grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(0, 7)
        )
        self.algorithm_cards: List[ctk.CTkFrame] = []
        self._algorithm_path_labels: List[ctk.CTkLabel] = []

        self._algorithm_card(
            comparison,
            column=0,
            title="Dijkstra classique",
            accent=BLUE,
            result_key="classic",
        )
        self._algorithm_card(
            comparison,
            column=1,
            title="Dijkstra dynamique",
            accent=PURPLE,
            result_key="dynamic",
        )
        playback = self._card(self.content_frame)
        self.playback_card = playback
        playback.grid(row=2, column=0, sticky="ew", padx=30, pady=(10, 16))
        playback.grid_columnconfigure(0, weight=0)
        playback.grid_columnconfigure(1, weight=1)
        playback.grid_columnconfigure(2, weight=0)
        self.playback_title = ctk.CTkLabel(
            playback,
            text="4. Explorer le calcul",
            text_color=INK,
            font=ctk.CTkFont(size=FONT_SECTION - 2, weight="bold"),
        )
        self.playback_title.grid(row=0, column=0, sticky="w", padx=18, pady=(12, 1))
        self.playback_subtitle = ctk.CTkLabel(
            playback,
            text="Suivez les sommets traités et les distances mises à jour.",
            text_color=MUTED,
            font=ctk.CTkFont(size=FONT_BODY),
        )
        self.playback_subtitle.grid(
            row=1, column=0, sticky="w", padx=18, pady=(0, 8)
        )
        self.trace_menu = ctk.CTkOptionMenu(
            playback,
            variable=self.trace_algorithm,
            values=["Dijkstra classique", "Dijkstra dynamique"],
            command=self._on_trace_algorithm_changed,
            width=205,
            height=32,
            fg_color=CONTROL_BG,
            button_color=CONTROL_HOVER,
            button_hover_color=CONTROL_HOVER_STRONG,
            text_color=INK,
            dropdown_text_color=INK,
        )
        self.trace_menu.grid(row=0, column=1, rowspan=2, sticky="e", padx=12, pady=10)

        controls = ctk.CTkFrame(playback, fg_color="transparent")
        self.playback_controls = controls
        controls.grid(
            row=0, column=2, rowspan=2, sticky="ew", padx=12, pady=(8, 8)
        )
        self.restart_button = ctk.CTkButton(
            controls,
            text="⏮ Début",
            width=100,
            height=36,
            command=self._restart_trace,
            fg_color=CONTROL_BG,
            hover_color=CONTROL_HOVER,
            text_color=INK,
            text_color_disabled=DISABLED_TEXT,
        )
        self.previous_button = ctk.CTkButton(
            controls,
            text="◀ Précédent",
            width=128,
            height=36,
            command=self._previous_trace_step,
            fg_color=CONTROL_BG,
            hover_color=CONTROL_HOVER,
            text_color=INK,
            text_color_disabled=DISABLED_TEXT,
        )
        self.play_button = ctk.CTkButton(
            controls,
            text="▶ Lire",
            width=102,
            height=36,
            command=self._toggle_trace_playback,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            text_color=WHITE,
        )
        self.next_button = ctk.CTkButton(
            controls,
            text="Suivant ▶",
            width=112,
            height=36,
            command=self._next_trace_step,
            fg_color=CONTROL_BG,
            hover_color=CONTROL_HOVER,
            text_color=INK,
            text_color_disabled=DISABLED_TEXT,
        )
        self.playback_button_widgets = [
            self.restart_button,
            self.previous_button,
            self.play_button,
            self.next_button,
        ]
        self.trace_counter = ctk.CTkLabel(
            controls,
            text="Étape 0 sur 0",
            text_color=MUTED,
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        self.trace_counter.grid(row=0, column=4, sticky="e", padx=8)
        self.trace_explanation = ctk.CTkLabel(
            playback,
            text="Choisissez un algorithme puis avancez étape par étape.",
            text_color=STRONG_MUTED,
            fg_color=PANEL_BG,
            corner_radius=STATUS_RADIUS,
            wraplength=1000,
            justify="left",
            anchor="w",
            padx=12,
            pady=10,
            font=ctk.CTkFont(size=11),
        )
        self.trace_explanation.grid(
            row=2, column=0, columnspan=3, sticky="ew", padx=18, pady=(2, 12)
        )
        self.playback_mode = ""

    @staticmethod
    def _card(parent: ctk.CTkBaseClass) -> ctk.CTkFrame:
        return ctk.CTkFrame(
            parent,
            fg_color=CARD,
            corner_radius=CARD_RADIUS,
            border_width=1,
            border_color=LINE,
        )

    def _section_heading(
        self,
        parent: ctk.CTkFrame,
        eyebrow: str,
        title: str,
        columnspan: int = 1,
    ) -> None:
        ctk.CTkLabel(
            parent,
            text=eyebrow,
            text_color=MUTED,
            font=ctk.CTkFont(size=10, weight="bold"),
        ).grid(
            row=0, column=0, columnspan=columnspan, sticky="ew", padx=22, pady=(18, 3)
        )
        ctk.CTkLabel(
            parent,
            text=title,
            text_color=INK,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(
            row=1, column=0, columnspan=columnspan, sticky="ew", padx=22, pady=(0, 12)
        )

    def _selector(
        self,
        parent: ctk.CTkFrame,
        label: str,
        variable: ctk.StringVar,
        column: int,
        accent: str,
    ) -> None:
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, sticky="ew", padx=(0, 10) if column == 0 else 0)
        ctk.CTkLabel(
            frame,
            text=f"●  {label}",
            text_color=accent,
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 5))
        menu = ctk.CTkOptionMenu(
            frame,
            variable=variable,
            values=self.nodes,
            fg_color=SELECTOR_BG,
            button_color=SELECTOR_BUTTON,
            button_hover_color=SELECTOR_HOVER,
            text_color=INK,
            dropdown_text_color=INK,
            command=self._on_endpoint_selected,
            height=34,
        )
        menu.pack(fill="x")

    def _legend_item(
        self,
        parent: ctk.CTkFrame,
        label: str,
        color: str,
        column: int,
        outlined: bool = False,
    ) -> ctk.CTkFrame:
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.grid(row=0, column=column, sticky="w", padx=(0, 8), pady=2)
        ctk.CTkFrame(
            item,
            width=10,
            height=10,
            corner_radius=MARKER_RADIUS,
            fg_color=color,
            border_width=1 if outlined else 0,
            border_color=BORDER_SOFT,
        ).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(
            item,
            text=label,
            text_color=MUTED,
            font=ctk.CTkFont(size=10),
        ).pack(side="left")
        return item

    def _algorithm_card(
        self,
        parent: ctk.CTkFrame,
        column: int,
        title: str,
        accent: str,
        result_key: str,
    ) -> None:
        card = self._card(parent)
        self.algorithm_cards.append(card)
        card.grid(row=2, column=column, sticky="nsew", padx=(0, 7) if column == 0 else (7, 0))
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card,
            text=title,
            text_color=INK,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 1))
        status = ctk.CTkLabel(
            card,
            text="Prêt · calcul initial",
            text_color=accent,
            fg_color=SELECTOR_BG,
            corner_radius=8,
            padx=9,
            pady=4,
            font=ctk.CTkFont(size=10, weight="bold"),
        )
        status.grid(row=1, column=0, sticky="w", padx=18, pady=(0, 5))
        path_label = ctk.CTkLabel(
            card,
            text="Chemin : —",
            text_color=INK,
            wraplength=380,
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self._algorithm_path_labels.append(path_label)
        path_label.grid(row=2, column=0, sticky="ew", padx=18, pady=(3, 5))
        distance_label = ctk.CTkLabel(
            card,
            text="Coût total : —",
            text_color=INK,
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        distance_label.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 3))
        time_label = ctk.CTkLabel(
            card,
            text="Mesure sur ce graphe : —",
            text_color=MUTED,
            anchor="w",
            font=ctk.CTkFont(size=11),
        )
        time_label.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 15))
        processed_label = ctk.CTkLabel(
            card,
            text="Sommets traités · —",
            text_color=INK,
            anchor="w",
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        processed_label.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 2))
        updates_label = ctk.CTkLabel(
            card,
            text="Mises à jour · —",
            text_color=MUTED,
            anchor="w",
            font=ctk.CTkFont(size=10),
        )
        updates_label.grid(row=6, column=0, sticky="ew", padx=18, pady=(0, 12))
        labels = {
            "status": status,
            "path": path_label,
            "distance": distance_label,
            "time": time_label,
            "processed": processed_label,
            "updates": updates_label,
        }
        if result_key == "classic":
            self.classic_result_labels = labels
        else:
            self.dynamic_result_labels = labels
