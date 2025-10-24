import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import os

class ItemScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg='#f0f4f8')
        self.controller = controller
        self.selected_quantity = 1
        self.max_quantity = 1
        self.current_item = None
        self.photo_image = None # To hold a reference to the image

        # --- Color and Font Scheme ---
        self.colors = {
            'background': '#f0f4f8',
            'text_fg': '#2c3e50',
            'gray_fg': '#7f8c8d',
            'price_fg': '#27ae60',
            'border': '#bdc3c7',
            'btn_bg': '#bdc3c7',
            'btn_fg': '#2c3e50',
            'cart_btn_bg': '#27ae60',
            'cart_btn_fg': '#ffffff',
        }
        self.fonts = {
            'name': tkfont.Font(family="Helvetica", size=36, weight="bold"),
            'description': tkfont.Font(family="Helvetica", size=18),
            'price': tkfont.Font(family="Helvetica", size=28, weight="bold"),
            'quantity': tkfont.Font(family="Helvetica", size=18),
            'image_placeholder': tkfont.Font(family="Helvetica", size=24),
            'qty_selector': tkfont.Font(family="Helvetica", size=20, weight="bold"),
            'action_button': tkfont.Font(family="Helvetica", size=18, weight="bold"),
        }

        self.create_widgets()

    def create_widgets(self):
        # Main frame uses pack for a single-column layout
        main_frame = tk.Frame(self, bg=self.colors['background'])
        main_frame.pack(expand=True, fill='both', padx=50, pady=50)

        # --- Top: Image ---
        image_frame = tk.Frame(
            main_frame, 
            bg='white', 
            highlightbackground=self.colors['border'],
            highlightthickness=1,
            height=400 # Give the image frame a default height
        )
        image_frame.pack(fill='x', pady=(0, 25))
        
        self.image_label = tk.Label(
            image_frame,
            text="No Image",
            font=self.fonts['image_placeholder'],
            fg=self.colors['gray_fg'],
            bg='white'
        )
        self.image_label.pack(expand=True, fill='both')

        # --- Bottom: Item Details ---
        details_frame = tk.Frame(main_frame, bg=self.colors['background'])
        details_frame.pack(fill='both', expand=True)

        self.name_label = tk.Label(details_frame, font=self.fonts['name'], fg=self.colors['text_fg'], bg=self.colors['background'], anchor='w', justify='left')
        self.name_label.pack(pady=(20, 10), fill='x')

        self.description_label = tk.Label(details_frame, font=self.fonts['description'], fg=self.colors['text_fg'], bg=self.colors['background'], wraplength=500, anchor='w', justify='left')
        self.description_label.pack(pady=10, fill='x')

        spacer = tk.Frame(details_frame, bg=self.colors['background'])
        spacer.pack(expand=True, fill='both')

        # --- Quantity Selector ---
        quantity_frame = tk.Frame(details_frame, bg=self.colors['background'])
        quantity_frame.pack(fill='x', pady=20)

        decrease_button = tk.Button(
            quantity_frame,
            text="-",
            font=self.fonts['qty_selector'],
            bg=self.colors['btn_bg'],
            fg=self.colors['btn_fg'],
            relief='flat',
            width=3,
            command=self.decrease_quantity
        )
        decrease_button.pack(side='left')

        self.quantity_display_label = tk.Label(
            quantity_frame,
            text="1",
            font=self.fonts['qty_selector'],
            bg=self.colors['background'],
            fg=self.colors['text_fg'],
            width=4
        )
        self.quantity_display_label.pack(side='left', padx=10)

        increase_button = tk.Button(
            quantity_frame,
            text="+",
            font=self.fonts['qty_selector'],
            bg=self.colors['btn_bg'],
            fg=self.colors['btn_fg'],
            relief='flat',
            width=3,
            command=self.increase_quantity
        )
        increase_button.pack(side='left')


        bottom_frame = tk.Frame(details_frame, bg=self.colors['background'])
        bottom_frame.pack(fill='x', pady=20)

        self.price_label = tk.Label(bottom_frame, font=self.fonts['price'], fg=self.colors['price_fg'], bg=self.colors['background'])
        self.price_label.pack(side='left')

        self.quantity_label = tk.Label(bottom_frame, font=self.fonts['quantity'], fg=self.colors['gray_fg'], bg=self.colors['background'])
        self.quantity_label.pack(side='right')

        # --- Action Buttons (Back and Cart) ---
        action_frame = tk.Frame(details_frame, bg=self.colors['background'])
        action_frame.pack(fill='x', pady=(10, 0))

        back_button = tk.Button(
            action_frame,
            text="Back",
            font=self.fonts['action_button'],
            bg=self.colors['gray_fg'],
            fg=self.colors['background'],
            relief='flat',
            pady=10,
            command=lambda: self.controller.show_kiosk()
        )
        back_button.pack(side='left', expand=True, fill='x', padx=(0, 5))

        cart_button = tk.Button(
            action_frame,
            text="Add to Cart",
            font=self.fonts['action_button'],
            bg=self.colors['cart_btn_bg'],
            fg=self.colors['cart_btn_fg'],
            relief='flat',
            pady=10,
            command=self.add_to_cart
        )
        cart_button.pack(side='left', expand=True, fill='x', padx=(5, 0))

    def add_to_cart(self):
        """Handles adding the item to the cart via the controller."""
        if self.current_item:
            self.controller.add_to_cart(self.current_item, self.selected_quantity)            
            self.controller.reduce_item_quantity(self.current_item, self.selected_quantity)
            # Navigate to the cart screen after adding an item
            self.controller.show_kiosk()

    def decrease_quantity(self):
        """Decreases the selected quantity by 1, with a minimum of 1."""
        if self.selected_quantity > 1:
            self.selected_quantity -= 1
            self.quantity_display_label.config(text=str(self.selected_quantity))

    def increase_quantity(self):
        """Increases the selected quantity by 1, up to the max available."""
        if self.selected_quantity < self.max_quantity:
            self.selected_quantity += 1
            self.quantity_display_label.config(text=str(self.selected_quantity))

    def set_item(self, item_data):
        """Populates the screen with data from the selected item."""
        self.current_item = item_data
        self.name_label.config(text=item_data['name'])
        self.description_label.config(text=item_data['description'])
        self.price_label.config(text=f"{self.controller.currency_symbol}{item_data['price']:.2f}")
        self.quantity_label.config(text=f"Quantity available: {item_data['quantity']}")
        
        # Reset quantity selector for the new item
        self.selected_quantity = 1
        self.max_quantity = item_data['quantity']
        self.quantity_display_label.config(text="1")
        
        # --- Update Image ---
        image_path = item_data.get("image")
        if image_path and os.path.exists(image_path):
            try:
                # Open, resize, and display the image
                img = Image.open(image_path)

                # Resize to fit a 400x400 box while maintaining aspect ratio
                img.thumbnail((400, 400), Image.Resampling.LANCZOS)

                self.photo_image = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.photo_image, text="")
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
                self.image_label.config(
                    image="", # Clear previous image
                    text="Image Error",
                    font=self.fonts['image_placeholder']
                )
        else:
            # Show placeholder if no image
            self.image_label.config(
                image="", # Clear previous image
                text="No Image",
                font=self.fonts['image_placeholder'],
            )