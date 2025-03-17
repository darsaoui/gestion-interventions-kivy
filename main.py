from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.recycleview import RecycleView
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
import csv, re
from datetime import datetime

interventions = []

def is_valid_ip(ip):
    pattern = r"^(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})$"
    match = re.match(pattern, ip)
    return bool(match) and all(0 <= int(octet) <= 255 for octet in match.groups())

def is_valid_date(date_text):
    try:
        datetime.strptime(date_text, '%d/%m/%Y')
        return True
    except ValueError:
        return False

class InterventionApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.fields = {}

        for label_text in ["Nom utilisateur", "Nom du PC", "IP", "Numéro de Bureau", "Date d'intervention"]:
            box = BoxLayout(size_hint_y=None, height=40)
            box.add_widget(Label(text=label_text, size_hint_x=0.4))
            input_field = TextInput(multiline=False)
            box.add_widget(input_field)
            self.fields[label_text] = input_field
            self.add_widget(box)

        self.situation_internet = Spinner(
            text='Situation internet', values=('Connecté', 'Non connecté'), size_hint_y=None, height=40)
        self.add_widget(self.situation_internet)

        self.type_ip = Spinner(
            text='Type d\'IP', values=('Statique', 'Dynamique'), size_hint_y=None, height=40)
        self.add_widget(self.type_ip)

        self.observations = TextInput(hint_text='Observations', size_hint_y=None, height=80)
        self.add_widget(self.observations)

        buttons = BoxLayout(size_hint_y=None, height=50)
        buttons.add_widget(Button(text="Ajouter", on_press=self.ajouter))
        buttons.add_widget(Button(text="Supprimer", on_press=self.supprimer))
        buttons.add_widget(Button(text="Modifier", on_press=self.modifier))
        self.add_widget(buttons)

        self.rv = RecycleView(size_hint=(1, 1))
        self.rv.data = []
        self.add_widget(self.rv)

        self.charger_donnees_csv()

    def ajouter(self, instance):
        data = {key: field.text.strip() for key, field in self.fields.items()}
        data["Situation internet"] = self.situation_internet.text
        data["Type d'IP"] = self.type_ip.text
        data["Observations"] = self.observations.text

        if not all(data.values()) or data["Situation internet"] == 'Situation internet' or data["Type d'IP"] == 'Type d\'IP':
            self.popup_message("Remplissez tous les champs obligatoires.")
            return

        if not is_valid_ip(data["IP"]):
            self.popup_message("Adresse IP invalide.")
            return

        if not is_valid_date(data["Date d'intervention"]):
            self.popup_message("Date invalide (jj/mm/aaaa).")
            return

        interventions.append(data)
        self.update_list()
        self.enregistrer_donnees_csv()
        self.reset_fields()

    def supprimer(self, instance):
        if self.rv.data:
            interventions.pop()
            self.update_list()
            self.enregistrer_donnees_csv()

    def modifier(self, instance):
        if self.rv.data:
            data = interventions.pop()
            for key, field in self.fields.items():
                field.text = data[key]
            self.situation_internet.text = data["Situation internet"]
            self.type_ip.text = data["Type d'IP"]
            self.observations.text = data["Observations"]
            self.update_list()
            self.enregistrer_donnees_csv()

    def update_list(self):
        self.rv.data = [{'text': f"{i['Nom utilisateur']} - {i['IP']} - {i['Date d\'intervention']}"} for i in interventions]

    def reset_fields(self):
        for field in self.fields.values():
            field.text = ''
        self.situation_internet.text = 'Situation internet'
        self.type_ip.text = 'Type d\'IP'
        self.observations.text = ''

    def enregistrer_donnees_csv(self):
        with open("interventions.csv", "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=interventions[0].keys())
            writer.writeheader()
            writer.writerows(interventions)

    def charger_donnees_csv(self):
        try:
            with open("interventions.csv", "r") as file:
                reader = csv.DictReader(file)
                interventions.clear()
                interventions.extend(reader)
                self.update_list()
        except FileNotFoundError:
            pass

    def popup_message(self, message):
        popup = Popup(title='Erreur', content=Label(text=message), size_hint=(0.6, 0.3))
        popup.open()

class MainApp(App):
    def build(self):
        return InterventionApp()

if __name__ == '__main__':
    MainApp().run()
