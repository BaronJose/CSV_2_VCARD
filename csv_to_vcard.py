import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import csv
import os
import base64
import requests

APP_NAME = "ContactCard Maker"
TAGLINE = "Effortless CSV to vCard for iOS & macOS Contacts"

class CSVtoVCardApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("720x540")
        self.csv_data = []
        self.field_vars = {}
        self.field_names = []
        self.vcard_fields = [
            "Skip", "First Name", "Last Name", "Phone (Mobile)", "Phone (Work)",
            "Email (Work)", "Email (Home)", "Organization", "Title", "Website",
            "Birthday", "Photo URL", "Notes", "Address - Street", "Address - City",
            "Address - State", "Address - ZIP", "Address - Country"
        ]
        self.create_widgets()

    def create_widgets(self):
        header = tk.Frame(self.root)
        header.pack(pady=10)
        tk.Label(header, text=APP_NAME, font=("Arial", 16, "bold")).pack()
        tk.Label(header, text=TAGLINE, font=("Arial", 10, "italic"), fg="gray").pack()

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)
        tk.Button(top_frame, text="📂 Load CSV", command=self.load_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="⬇️ Sample CSV", command=self.save_sample_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="❓ Help", command=self.show_help).pack(side=tk.LEFT, padx=5)

        self.mapping_frame = tk.Frame(self.root)
        self.mapping_frame.pack(pady=10)

        self.option_frame = tk.Frame(self.root)
        self.option_frame.pack(pady=10)

        self.vcard_option = tk.StringVar(value="single")
        tk.Radiobutton(self.option_frame, text="📄 One vCard per contact", variable=self.vcard_option, value="single").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(self.option_frame, text="📦 One big vCard file", variable=self.vcard_option, value="bulk").pack(side=tk.LEFT, padx=5)

        tk.Button(self.root, text="📤 Export vCard(s)", command=self.export_vcards).pack(pady=10)

        self.status = tk.StringVar()
        status_bar = tk.Label(self.root, textvariable=self.status, relief=tk.SUNKEN, anchor='w', bd=1)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.set_status("Ready")

        footer = tk.Label(self.root, text="Built with ❤️ for Apple Contacts", font=("Arial", 8), fg="gray")
        footer.pack(side=tk.BOTTOM, pady=2)

    def set_status(self, text, error=False):
        self.status.set(("❌ " if error else "✅ ") + text)

    def log_message(self, text):
        print(text)
        self.set_status(text)

    def show_help(self):
        help_win = Toplevel(self.root)
        help_win.title("How to Use")
        help_win.geometry("400x300")
        tk.Label(help_win, text="📘 How to Use ContactCard Maker", font=("Arial", 12, "bold")).pack(pady=10)

        msg = (
            "1. Click 'Load CSV' and select your contact CSV file.\n"
            "2. Use the dropdowns to map each CSV column to a vCard field.\n"
            "   ✅ First and Last Name are required.\n"
            "3. Choose export type:\n"
            "   - One vCard per contact\n"
            "   - One big vCard file\n"
            "4. Click 'Export vCards' to save your .vcf files.\n\n"
            "Need a format example? Click 'Sample CSV'."
        )
        tk.Label(help_win, text=msg, justify=tk.LEFT, wraplength=380).pack(padx=10)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        try:
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.csv_data = list(reader)
                self.field_names = reader.fieldnames or []

            if not self.field_names:
                raise ValueError("CSV has no headers")

            self.display_mapping_options()
            self.set_status(f"Loaded {len(self.csv_data)} contact(s) from CSV")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
            self.set_status("CSV load failed", error=True)

    def display_mapping_options(self):
        for widget in self.mapping_frame.winfo_children():
            widget.destroy()

        tk.Label(self.mapping_frame, text="CSV Field", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        tk.Label(self.mapping_frame, text="Map to vCard Field", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5)

        self.field_vars = {}
        for idx, field in enumerate(self.field_names):
            tk.Label(self.mapping_frame, text=field).grid(row=idx+1, column=0, sticky="w", padx=5)
            var = tk.StringVar(value="Skip")
            dropdown = tk.OptionMenu(self.mapping_frame, var, *self.vcard_fields)
            dropdown.grid(row=idx+1, column=1, sticky="w", padx=5)
            self.field_vars[field] = var

    def validate_mapping(self):
        mapped = [v.get() for v in self.field_vars.values()]
        if "First Name" not in mapped or "Last Name" not in mapped:
            messagebox.showerror("Missing Fields", "Please map both First Name and Last Name.")
            return False
        return True

    def generate_vcard(self, contact):
        def get_value(label):
            for field, var in self.field_vars.items():
                if var.get() == label:
                    return contact.get(field, "").strip()
            return ""

        first = get_value("First Name")
        last = get_value("Last Name")
        if not first or not last:
            return None

        name = f"{first} {last}".strip()
        org = get_value("Organization")
        title = get_value("Title")
        phone_mobile = get_value("Phone (Mobile)")
        phone_work = get_value("Phone (Work)")
        email_work = get_value("Email (Work)")
        email_home = get_value("Email (Home)")
        url = get_value("Website")
        bday = get_value("Birthday")
        photo_url = get_value("Photo URL")
        notes = get_value("Notes")

        street = get_value("Address - Street")
        city = get_value("Address - City")
        state = get_value("Address - State")
        zip_code = get_value("Address - ZIP")
        country = get_value("Address - Country")
        address = f";;{street};{city};{state};{zip_code};{country}"

        vcard = "BEGIN:VCARD\nVERSION:3.0\n"
        vcard += f"N:{last};{first};;;\n"
        vcard += f"FN:{name}\n"
        if phone_mobile:
            vcard += f"TEL;TYPE=CELL:{phone_mobile}\n"
        if phone_work:
            vcard += f"TEL;TYPE=WORK:{phone_work}\n"
        if email_work:
            vcard += f"EMAIL;TYPE=INTERNET:{email_work}\n"
        if email_home:
            vcard += f"EMAIL;TYPE=HOME:{email_home}\n"
        if org:
            vcard += f"ORG:{org}\n"
        if title:
            vcard += f"TITLE:{title}\n"
        if url:
            vcard += f"URL:{url}\n"
        if bday:
            vcard += f"BDAY:{bday}\n"
        if photo_url:
            try:
                img_data = requests.get(photo_url, timeout=5).content
                encoded = base64.b64encode(img_data).decode("utf-8")
                vcard += f"PHOTO;ENCODING=b;TYPE=JPEG:{encoded}\n"
            except Exception as e:
                self.log_message(f"Could not load photo from {photo_url}: {e}")
        if notes:
            vcard += f"NOTE:{notes}\n"
        if street or city or state or zip_code or country:
            vcard += f"ADR;TYPE=HOME:{address}\n"
        vcard += "END:VCARD\n"
        return vcard

    def export_vcards(self):
        if not self.csv_data:
            messagebox.showwarning("No Data", "Please load a CSV file first.")
            return

        if not self.validate_mapping():
            return

        export_dir = filedialog.askdirectory(title="Select Export Folder")
        if not export_dir:
            return

        big_card = self.vcard_option.get() == "bulk"
        success_count = 0
        failed = 0
        vcards = []

        for idx, contact in enumerate(self.csv_data):
            vcard = self.generate_vcard(contact)
            if not vcard:
                failed += 1
                continue

            if big_card:
                vcards.append(vcard)
            else:
                first = get_value_from_contact(contact, "First Name")
                last = get_value_from_contact(contact, "Last Name")
                full_name = f"{first} {last}".strip() or f"contact_{idx+1}"
                safe_name = "".join(c for c in full_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_name}.vcf"

                try:
                    with open(os.path.join(export_dir, filename), "w", encoding="utf-8") as f:
                        f.write(vcard)
                    success_count += 1
                except Exception as e:
                    failed += 1
                    self.log_message(f"Failed to export {full_name}: {e}")

        if big_card and vcards:
            try:
                with open(os.path.join(export_dir, "contacts.vcf"), "w", encoding="utf-8") as f:
                    f.write("\n".join(vcards))
                success_count = len(vcards)
            except Exception as e:
                self.log_message(f"Failed to export big vCard: {e}")
                failed += len(vcards)

        self.log_message(f"Exported {success_count} contact(s), {failed} failed.")

    def validate_mapping(self):
 
        for field in self.field_vars.values():
            if field.get() != 'Skip':
                return True
        messagebox.showwarning("Missing Mapping", "Please map at least one field before exporting.")
        return False

    def save_sample_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "First Name", "Last Name", "Phone", "Email", "Organization", "Title", "Website",
                    "Birthday", "Photo URL", "Notes", "Street", "City", "State", "ZIP", "Country"
                ])
                writer.writerow([
                    "Jane", "Smith", "5551234567", "jane@work.com", "Widgets Inc", "Developer",
                    "https://widgets.com", "1990-05-15", "https://example.com/jane.jpg", "Met at conference",
                    "456 Elm St", "Clovis", "CA", "93611", "USA"
                ])
            self.set_status("Sample CSV downloaded")

def get_value_from_contact(contact, label):
    for field, var in app.field_vars.items():
        if var.get() == label:
            return contact.get(field, "").strip()
    return ""

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVtoVCardApp(root)
    root.mainloop()
