import kivy
import json
from kivy.uix.checkbox import CheckBox
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.storage.jsonstore import JsonStore
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.togglebutton import ToggleButton
from datetime import datetime
from itertools import combinations
import random
import os

folder = "tournaments"
if not os.path.exists(folder):
    os.makedirs(folder)


BackGround = """
MDScreen:

    FitImage:
        source: 'background.png'
"""

def powerOfTwo(n):
    i = 1
    while pow(2,i) < n:
        i += 1
    return pow(2,i)

def encode(string):
        g = ord('а')
        f = ord('a')
        for i in range(33):
            while chr(g+i) in string:
                string = string.replace(chr(g+i), chr(f+i))
        g = ord('А')
        f = ord('A')
        for i in range(33):
            while chr(g+i) in string:
                string = string.replace(chr(g+i), chr(f+i))
        while ('ё' in string):
            string = string.replace('ё', '#')
        while ('Ё' in string):
            string = string.replace('Ё', '$') 
        return string

def decode(string):
        f = ord('а')
        g = ord('a')
        for i in range(33):
                while chr(g+i) in string:
                    string = string.replace(chr(g+i), chr(f+i))
        f = ord('А')
        g = ord('A')
        for i in range(33):
                while chr(g+i) in string:
                    string = string.replace(chr(g+i), chr(f+i))
        while ('#' in string):
                string = string.replace('#', 'ё')
        while ('$' in string):
                string = string.replace('$', 'Ё') 
        return string

store = JsonStore('table_data.json')

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(padding=[250, 50, 250, 100], orientation="vertical")

        logo = Image(
            source="logo.png",
            size_hint=(2.5, 2.5),
            pos_hint={"center_x": 0.5, "center_y": 1},
        )
        layout.add_widget(logo)

        upper_button = Button(
            text="Открыть таблицу членов клуба", background_color=[134 / 255, 130 / 255, 102 / 255, 1]
        )
        upper_button.bind(on_press=self.on_press_upper_button)
        layout.add_widget(upper_button)

        lower_button = Button(
            text="Открыть турнирное меню", background_color=[134 / 255, 130 / 255, 102 / 255, 1]
        )
        lower_button.bind(on_press=self.on_press_lower_button)
        layout.add_widget(lower_button)

        self.add_widget(layout)

    def on_press_upper_button(self, instance):
        self.manager.current = "peopleList"
    def on_press_lower_button(self, instance):
        self.manager.current = "TournamentMenu"


class listScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(padding=15, orientation="vertical")

        self.background = Widget()
        with self.background.canvas:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=Window.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)
        self.add_widget(self.background)

        self.refresh_table()

        button_layout = BoxLayout(size_hint=(1, 0.1), orientation="horizontal")

        back_button = Button(
            text="Вернуться на главный экран",
            background_color=[134 / 255, 130 / 255, 102 / 255, 1],
        )
        back_button.bind(on_press=self.on_press_back_button)
        button_layout.add_widget(back_button)

        add_button = Button(
            text="Добавить нового члена клуба",
            background_color=[102 / 255, 134 / 255, 102 / 255, 1],
        )
        add_button.bind(on_press=self.on_press_add_button)
        button_layout.add_widget(add_button)

        self.layout.add_widget(button_layout)
        self.add_widget(self.layout)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def delete_member(self, idx):
        global store
        keys = sorted(store.keys(), key=lambda x: int(x.replace('member', '')))
        del_key = keys[idx]
        store.delete(del_key)
        members = [store.get(k) for k in sorted(store.keys(), key=lambda x: int(x.replace('member', '')))]
        store.clear()
        for i, member in enumerate(members):
            store.put(f'member{i+1}', **member)
        self.refresh_table()

    def refresh_table(self):
        if hasattr(self, 'scroll_view') and self.scroll_view in self.layout.children:
            self.layout.remove_widget(self.scroll_view)

        global store
        members = len(store)
        if members == 0:
            self.table_data = [
                ("Нет", "Таблицы", "Данных", "-", "-", "-", "-", "-", "-", "-", "-"),
            ]
        else:
            tableData = []
            for g in range(members):
                i = str(g + 1)
                key = f'member{i}'
                tableData.append((
                    decode(store.get(key)['lastName']),
                    decode(store.get(key)['name']),
                    decode(store.get(key)['fatherName']),
                    decode(store.get(key)['age']),
                    decode(store.get(key)['gender']),
                    decode(store.get(key)['team']),
                    decode(store.get(key)['sword']),
                    decode(store.get(key)['swordANDbuckler']),
                    decode(store.get(key)['sabre']),
                    decode(store.get(key)['rapier']),
                    decode(store.get(key)['kendo']),
                    decode(store.get(key)['rating'])
                ))
            self.table_data = tableData

        self.scroll_view = ScrollView(size_hint=(1, 0.9), do_scroll_x=True, do_scroll_y=True)
        table_layout = GridLayout(
            cols=14,
            size_hint_y=None,
            size_hint_x=None,
            width=dp(1950)
        )
        table_layout.bind(minimum_height=table_layout.setter('height'))

        headers = [
            "Фамилия", "Имя", "Отчество", "Возраст", "Пол", "Команда",
            "Меч", "Меч + баклер", "Сабля", "Рапира", "Кендо", "Рейтинг", "", ""
        ]
        for header in headers:
            table_layout.add_widget(Label(text=header, color=(0, 0, 0, 1), size_hint_y=None, height=dp(40), size_hint_x=None, width=dp(130)))

        for idx, row in enumerate(self.table_data):
            for cell in row:
                table_layout.add_widget(Label(text=cell, color=(0, 0, 0, 1), size_hint_x=None, width=dp(130), halign='center', valign='middle', padding=(10, 10)))
            edit_btn = Button(text="Редактировать", size_hint_y=None, height=dp(40), size_hint_x=None, width=dp(130), font_size=dp(12))
            edit_btn.bind(on_press=lambda btn, idx=idx: self.open_edit_popup(idx))
            table_layout.add_widget(edit_btn)
            delete_btn = Button(text="Удалить", size_hint_y=None, height=dp(40), size_hint_x=None, width=dp(130), font_size=dp(12), background_color=[1, 0.4, 0.4, 1])
            delete_btn.bind(on_press=lambda btn, idx=idx: self.delete_member(idx))
            table_layout.add_widget(delete_btn)

        self.scroll_view.add_widget(table_layout)
        self.layout.add_widget(self.scroll_view, index=1)
    def open_edit_popup(self, idx):
        global store
        key = f'member{idx+1}'
        member = store.get(key)
        fields = [
            ("lastName", "Фамилия"),
            ("name", "Имя"),
            ("fatherName", "Отчество"),
            ("age", "Возраст"),
            ("gender", "Пол"),
            ("team", "Команда"),
            ("sword", "Меч"),
            ("swordANDbuckler", "Меч + баклер"),
            ("sabre", "Сабля"),
            ("rapier", "Рапира"),
            ("kendo", "Кендо"),
            ("rating", "Рейтинг"),
        ]
        content = BoxLayout(orientation="vertical", spacing=5, padding=10)
        inputs = {}
        for field, label in fields:
            box = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30))
            box.add_widget(Label(text=label, size_hint_x=0.4))
            ti = TextInput(text=decode(member[field]), multiline=False, size_hint_x=0.6)
            inputs[field] = ti
            box.add_widget(ti)
            content.add_widget(box)
        btn_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=10)
        save_btn = Button(text="Сохранить", background_color=[0.4, 0.7, 0.4, 1])
        cancel_btn = Button(text="Отмена", background_color=[0.7, 0.4, 0.4, 1])
        btn_box.add_widget(save_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)
        popup = Popup(title="Редактировать члена клуба", content=content, size_hint=(0.9, 0.9))

        def save_changes(instance):
            for field in inputs:
                member[field] = encode(inputs[field].text)
            store.put(key, **member)
            popup.dismiss()
            self.refresh_table()

        save_btn.bind(on_press=save_changes)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        popup.open()

    def on_press_back_button(self, instance):
        self.manager.current = "main"

    def on_press_add_button(self, instance):
        global store

        new_member_key = 'member' + str(len(store) + 1)
        store.put(
            new_member_key,
            lastName='Фамилия',
            name='Имя',
            fatherName='Отчество',
            age='Возраст',
            gender='Пол',
            team='Команда',
            sword='Нет',
            swordANDbuckler='Нет',
            sabre='Нет',
            rapier='Нет',
            kendo='Нет',
            rating='Рейтинг'
        )

        self.refresh_table()


class TournamentMenu (Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(padding=105, orientation="vertical")

        background = Builder.load_string(BackGround)
        self.add_widget(background)

        newTournament_button = Button(
            text="Начать новый турнир",
            background_color=[134 / 255, 130 / 255, 102 / 255, 1],
        )
        newTournament_button.bind(on_press=self.on_press_newTournament_button)
        layout.add_widget(newTournament_button)

        savedTournaments_button = Button(
            text="Посмотреть сохранённые турниры",
            background_color=[134 / 255, 130 / 255, 102 / 255, 1],
        )
        savedTournaments_button.bind(on_press=self.on_press_savedTournaments_button)
        layout.add_widget(savedTournaments_button)

        back_button = Button(
            text="Вернуться на главный экран",
            background_color=[134 / 255, 130 / 255, 102 / 255, 1],
        )
        back_button.bind(on_press=self.on_press_back_button)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def on_press_back_button(self, instance):
        self.manager.current = "main"
    
    def on_press_newTournament_button(self, instance):
        self.manager.current = "TournamentCreationScreen"
    
    def on_press_savedTournaments_button(self, instance):
        self.manager.current = "SavedTournamentsList"


class TournamentCreationScreen(Screen): 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(padding=75, orientation="vertical")

        background = Builder.load_string(BackGround)
        self.add_widget(background)

        qualifiers_button = Button(
            text="Отборочные группы",
            background_color=[134 / 255, 130 / 255, 102 / 255, 1],
        )
        qualifiers_button.bind(on_press=self.on_press_qualifiers_button)
        layout.add_widget(qualifiers_button)

        qualifiers_playoff_button = Button(
            text="Отборочные группы + плей-офф",
            background_color=[134 / 255, 130 / 255, 102 / 255, 1],
        )
        qualifiers_playoff_button.bind(on_press=self.on_press_qualifiers_playoff_button)
        layout.add_widget(qualifiers_playoff_button)

        swiss_button = Button(
            text="Швейцарская система",
            background_color=[134 / 255, 130 / 255, 102 / 255, 1],
        )
        swiss_button.bind(on_press=self.on_press_swiss_button)
        layout.add_widget(swiss_button)

        back_button = Button(
            text="Вернуться в меню турниров",
            background_color=[134 / 255, 130 / 255, 102 / 255, 1],
        )
        back_button.bind(on_press=self.on_press_back_button)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def on_press_qualifiers_button(self, instance):
        self.manager.current = "QualifiersTournament"

    def on_press_qualifiers_playoff_button(self, instance):
        self.manager.current = "QualifiersPlayOffTournament"

    def on_press_swiss_button(self, instance):
        self.manager.current = "SwissTournament"

    def on_press_back_button(self, instance):
        self.manager.current = "TournamentMenu"


class QualifiersTournament(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(padding=75, orientation="vertical")

        background = Builder.load_string(BackGround)
        self.add_widget(background)

        self.participants_input = TextInput(
            hint_text="Введите количество участников",
            multiline=False,
            size_hint=(1, 0.2),
        )
        layout.add_widget(self.participants_input)

        button_layout = BoxLayout(size_hint=(1, 0.2), orientation="horizontal")

        select_participants_button = Button(
            text="Выбрать участников",
            background_color=[102 / 255, 134 / 255, 102 / 255, 1],
        )
        select_participants_button.bind(on_press=self.on_press_select_participants_button)
        button_layout.add_widget(select_participants_button)

        back_button = Button(
            text="Вернуться в меню создания турнира",
            background_color=[134 / 255, 130 / 255, 102 / 255, 1],
        )
        back_button.bind(on_press=self.on_press_back_button)
        button_layout.add_widget(back_button)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def on_press_select_participants_button(self, instance):
        try:
            total_participants = int(self.participants_input.text)

            with open('table_data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                total_members = len(data)

            if total_participants < 2:
                self.show_error_popup("Количество участников\nне может быть меньше 2.")
                return
            if total_participants > total_members:
                self.show_error_popup("Количество участников\nне может быть больше\nколичества членов клуба.")
                return

            self.show_member_selection_popup(total_participants, list(data.keys()))
        except ValueError:
            self.show_error_popup("Пожалуйста, введите числовые значения.")

    def show_member_selection_popup(self, total_participants, member_keys):
        def after_selection(selected):
            participants = {
                k: {"points": 0, "hits": 0, "missedHits": 0, "hitsDifference": 0}
                for k in selected
            }
            battles = [list(pair) for pair in combinations(selected, 2)]

            def has_consecutive_battles(battles):
                for i in range(1, len(battles)):
                    prev = set(battles[i-1])
                    curr = set(battles[i])
                    if prev & curr:
                        return True
                return False

            max_attempts = 100000
            attempt = 0
            while has_consecutive_battles(battles) and attempt < max_attempts:
                random.shuffle(battles)
                attempt += 1

            results = {str(i): None for i in range(len(battles))}
            tournament_data = {
                "participants": participants,
                "battles": battles,
                "results": results,
                "current_battle": 0
            }
            import json
            date_str = datetime.now().strftime("%d-%m-%Y")
            filename = os.path.join("tournaments", f"QualifiersTournament_on_{date_str}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(tournament_data, f, ensure_ascii=False, indent=2)

        screen = self.manager.get_screen("MemberSelectionScreen")
        screen.setup(total_participants, member_keys, after_selection)
        self.manager.current = "MemberSelectionScreen"

    def show_error_popup(self, message):
        popup = Popup(
            title="Ошибка",
            content=Label(text=message),
            size_hint=(0.9, 0.9),
        )
        popup.open()

    def on_press_back_button(self, instance):
        self.manager.current = "TournamentCreationScreen"


class QualifiersPlayOffTournament(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(padding=15, orientation="vertical")

        background = Builder.load_string(BackGround)
        self.add_widget(background)

        self.participants_input = TextInput(
            hint_text="Введите количество участников",
            multiline=False,
            size_hint=(1, 0.2),
        )
        layout.add_widget(self.participants_input)

        self.playoff_participants_input = TextInput(
            hint_text="Количество участников плей-офф",
            multiline=False,
            size_hint=(1, 0.2),
        )
        layout.add_widget(self.playoff_participants_input)

        button_layout = BoxLayout(size_hint=(1, 0.2), orientation="horizontal")

        select_participants_button = Button(
            text="Выбрать участников",
            background_color=[102 / 255, 134 / 255, 102 / 255, 1],
        )
        select_participants_button.bind(on_press=self.on_press_select_participants_button)
        button_layout.add_widget(select_participants_button)

        back_button = Button(
            text="Вернуться в меню создания турнира",
            background_color=[134 / 255, 130 / 255, 102 / 255, 1],
        )
        back_button.bind(on_press=self.on_press_back_button)
        button_layout.add_widget(back_button)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def on_press_select_participants_button(self, instance):
        
        try:
            total_participants = int(self.participants_input.text)
            playoff_participants = int(self.playoff_participants_input.text)

            with open('table_data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                total_members = len(data)

            if total_participants < 2:
                self.show_error_popup("Количество участников\nне может быть меньше 2.")
                return
            if playoff_participants >= total_participants:
                self.show_error_popup("Количество участников плей-офф\nне может быть больше или равно\nобщему количеству участников.")
                return
            if total_participants > total_members:
                self.show_error_popup("Количество участников\nне может быть больше\nколичества членов клуба.")
                return
            if playoff_participants < 4:
                self.show_error_popup("Количество участников плей-офф\nне может быть меньше 4.")
                return

            screen = self.manager.get_screen("MemberSelectionScreen")
            def after_selection(selected):
                participants = {
                    k: {"points": 0, "hits": 0, "missedHits": 0, "hitsDifference": 0}
                    for k in selected
                }
                battles = [list(pair) for pair in combinations(selected, 2)]

                def has_consecutive_battles(battles):
                    for i in range(1, len(battles)):
                        prev = set(battles[i-1])
                        curr = set(battles[i])
                        if prev & curr:
                            return True
                    return False

                max_attempts = 100000
                attempt = 0
                while has_consecutive_battles(battles) and attempt < max_attempts:
                    random.shuffle(battles)
                    attempt += 1
                results = {str(i): None for i in range(len(battles))}
                tournament_data = {
                    "participants": participants,
                    "battles": battles,
                    "results": results,
                    "current_battle": 0,
                    "playoff_participants_count": playoff_participants,
                    "playoff_participants_list": []
                }
                import json
                date_str = datetime.now().strftime("%d-%m-%Y")
                filename = os.path.join("tournaments", f"QualifiersPlayOffTournament_on_{date_str}.json")
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(tournament_data, f, ensure_ascii=False, indent=2)
                self.manager.current = "SavedTournamentsList"

            screen.setup(total_participants, list(data.keys()), after_selection)
            self.manager.current = "MemberSelectionScreen"
        except ValueError:
            self.show_error_popup("Пожалуйста, введите числовые значения.")

    def show_error_popup(self, message):
        popup = Popup(
            title="Ошибка",
            content=Label(text=message),
            size_hint=(0.9, 0.9),
        )
        popup.open()

    def on_press_back_button(self, instance):
        self.manager.current = "TournamentCreationScreen"


class SwissTournament(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(padding=75, orientation="vertical")

        background = Builder.load_string(BackGround)
        self.add_widget(background)

        self.participants_input = TextInput(
            hint_text="Введите количество участников",
            multiline=False,
            size_hint=(1, 0.2),
        )
        layout.add_widget(self.participants_input)

        self.matches_input = TextInput(
            hint_text="Количество поединков на участника",
            multiline=False,
            size_hint=(1, 0.2),
        )
        layout.add_widget(self.matches_input)

        button_layout = BoxLayout(size_hint=(1, 0.2), orientation="horizontal")

        select_participants_button = Button(
            text="Выбрать участников",
            background_color=[102 / 255, 134 / 255, 102 / 255, 1],
        )
        select_participants_button.bind(on_press=self.on_press_select_participants_button)
        button_layout.add_widget(select_participants_button)

        back_button = Button(
            text="Вернуться в меню создания турнира",
            background_color=[134 / 255, 130 / 255, 102 / 255, 1],
        )
        back_button.bind(on_press=self.on_press_back_button)
        button_layout.add_widget(back_button)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def on_press_select_participants_button(self, instance):
        try:
            total_participants = int(self.participants_input.text)
            matches_per_participant = int(self.matches_input.text)

            with open('table_data.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                total_members = len(data)

            if total_participants < 3:
                self.show_error_popup("Количество участников\nне может быть меньше 3.")
                return
            if matches_per_participant >= total_participants:
                self.show_error_popup("Количество поединков на участника\nне может быть больше или равно\nобщему количеству участников.")
                return
            if total_participants > total_members:
                self.show_error_popup("Количество участников\nне может быть больше\nколичества членов клуба.")
                return
            if matches_per_participant < 1:
                self.show_error_popup("Количество поединков на участника\nне может быть меньше 1.")
                return

            screen = self.manager.get_screen("MemberSelectionScreen")
            def after_selection(selected):
                participants = {
                    k: {"points": 0, "hits": 0, "missedHits": 0, "hitsDifference": 0}
                    for k in selected
                }
                table_store = JsonStore('table_data.json')
                def get_rating(k):
                    try:
                        return int(table_store.get(k).get('rating', 0))
                    except Exception:
                        return 0
                sorted_participants = sorted(selected, key=get_rating)

                first_round_battles = []
                skipped = None
                working_list = sorted_participants.copy()
                if len(working_list) % 2 == 1:
                    skipped = working_list.pop(0)
                    participants[skipped]["points"] += 3

                half = len(working_list) // 2
                first_half = working_list[:half]
                second_half = working_list[half:]
                for a, b in zip(first_half, second_half):
                    first_round_battles.append([a, b])

                results = {str(i): None for i in range(len(first_round_battles))}

                tournament_data = {
                    "participants": participants,
                    "battles": [first_round_battles],
                    "results": [results],
                    "current_circle": 0,
                    "current_battle": 0,
                    "total_circles": matches_per_participant,
                    "already_played": []
                }
                import json
                date_str = datetime.now().strftime("%d-%m-%Y")
                filename = os.path.join("tournaments", f"SwissTournament_on_{date_str}.json")
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(tournament_data, f, ensure_ascii=False, indent=2)
                self.manager.current = "TournamentMenu"

            screen.setup(total_participants, list(data.keys()), after_selection)
            self.manager.current = "MemberSelectionScreen"
        except ValueError:
            self.show_error_popup("Пожалуйста, введите числовые значения.")

    def show_error_popup(self, message):
        popup = Popup(
            title="Ошибка",
            content=Label(text=message),
            size_hint=(0.9, 0.9),
        )
        popup.open()

    def on_press_back_button(self, instance):
        self.manager.current = "TournamentCreationScreen"


class SavedTournamentsList(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(padding=15, orientation="vertical")
        background = Builder.load_string(BackGround)
        self.add_widget(background)
        self.add_widget(self.layout)
        self.refresh_list()

    def on_pre_enter(self, *args):
        self.refresh_list()

    def show_interim_results_screen(self, filename):
        screen = self.manager.get_screen("InterimResultsScreen")
        screen.show_results(filename)
        self.manager.current = "InterimResultsScreen"

    def refresh_list(self):
        self.layout.clear_widgets()
        folder = "tournaments"
        if not os.path.exists(folder):
            os.makedirs(folder)
        tournament_files = [f for f in os.listdir(folder) if f.endswith(".json")]

        def extract_date(filename):
            import re
            from datetime import datetime
            match = re.search(r'_(\d{2}-\d{2}-\d{4})\.json$', filename)
            if match:
                try:
                    return datetime.strptime(match.group(1), "%d-%m-%Y")
                except Exception:
                    return datetime.min
            return datetime.min

        tournament_files.sort(key=extract_date, reverse=True)

        scroll = ScrollView(size_hint=(1, 0.8))
        grid = GridLayout(cols=1, size_hint_y=None, spacing=10, padding=10)
        grid.bind(minimum_height=grid.setter('height'))

        for filename in tournament_files:
            if filename.startswith("QualifiersTournament_on_"):
                label = "Отборочные группы"
                date = filename.replace("QualifiersTournament_on_", "").replace(".json", "")
                btn_callback = lambda inst, fn=filename: self.show_qualifiers_popup(fn)
            elif filename.startswith("QualifiersPlayOffTournament_on_"):
                label = "Отборочные группы + плей-офф"
                date = filename.replace("QualifiersPlayOffTournament_on_", "").replace(".json", "")
                btn_callback = lambda inst, fn=filename: self.show_playoff_popup(fn)
            elif filename.startswith("SwissTournament_on_"):
                label = "Турнир швейцарской системы"
                date = filename.replace("SwissTournament_on_", "").replace(".json", "")
                btn_callback = lambda inst, fn=filename: self.show_swiss_popup(fn)
            else:
                label = filename
                date = ""
                btn_callback = lambda inst: None

            btn = Button(
                text=f"{label} {date}",
                size_hint_y=None,
                height=dp(50),
                background_color=[102 / 255, 134 / 255, 102 / 255, 1],
            )
            btn.bind(on_press=btn_callback)
            grid.add_widget(btn)

        scroll.add_widget(grid)
        self.layout.add_widget(scroll)

        back_button = Button(
            text="Вернуться в меню турниров",
            background_color=[134 / 255, 130 / 255, 102 / 255, 1],
            size_hint_y=None,
            height=dp(50),
        )
        back_button.bind(on_press=self.on_press_back_button)
        self.layout.add_widget(back_button)

    def on_press_back_button(self, instance):
        self.manager.current = "TournamentMenu"

    def show_qualifiers_popup(self, filename):
        store = JsonStore(os.path.join("tournaments", filename))
        if store.exists('current_battle'):
            cb = store.get('current_battle')
            battle_index = cb['value'] if isinstance(cb, dict) and 'value' in cb else cb
        else:
            battle_index = 0
        battles = store.get('battles') if store.exists('battles') else []
        if isinstance(battles, dict):
            battles = [battles[str(i)] for i in range(len(battles))]
    
        if battle_index >= len(battles):
            with open(os.path.join("tournaments", filename), "r", encoding="utf-8") as f:
                data = json.load(f)
            table_store = JsonStore('table_data.json')
            def get_place_text(place_key, place_num):
                member_key = data.get(place_key)
                if member_key and table_store.exists(member_key):
                    member = table_store.get(member_key)
                    return f"{place_num} место: {decode(member['lastName'])} {decode(member['name'])} из команды {decode(member['team'])}"
                else:
                    return f"{place_num} место: -"
            first = get_place_text("first_place", "1")
            second = get_place_text("second_place", "2")
            third = get_place_text("third_place", "3")

            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(text="Турнир завершён!", size_hint_y=None, height=dp(40)))
            content.add_widget(Label(text=first, size_hint_y=None, height=dp(30)))
            content.add_widget(Label(text=second, size_hint_y=None, height=dp(30)))
            content.add_widget(Label(text=third, size_hint_y=None, height=dp(30)))
            btn_results = Button(text="Посмотреть результаты", size_hint_y=None, height=dp(50))
            btn_results.bind(on_press=lambda x: (popup.dismiss(), self.show_interim_results_screen(filename)))
            content.add_widget(btn_results)
            popup = Popup(title="Финал", content=content, size_hint=(0.9, 0.9))
            popup.open()
            return

        battle_number = battle_index + 1
        battle_pair = battles[battle_index]

        table_store = JsonStore('table_data.json')
        def get_info(key):
            member = table_store.get(key)
            return f"{decode(member['lastName'])} {decode(member['name'])} из команды {decode(member['team'])}"

        participant1 = get_info(battle_pair[0])
        participant2 = get_info(battle_pair[1])

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f"Бой №{battle_number}", size_hint_y=None, height=dp(40)))
        content.add_widget(Label(text=f"{participant1} VS {participant2}", size_hint_y=None, height=dp(40)))
        btn_results = Button(text="Объявить результаты боя", size_hint_y=None, height=dp(50))
        btn_interim = Button(text="Посмотреть промежуточные результаты", size_hint_y=None, height=dp(50))
        self._current_tournament_filename = filename
        self._current_battle_pair = battle_pair
        self._current_battle_index = battle_index
        btn_results.bind(on_press=lambda x: self.placeholder_battle_results())
        btn_interim.bind(on_press=lambda x: (popup.dismiss(), self.show_interim_results_screen(filename)))
        content.add_widget(btn_results)
        content.add_widget(btn_interim)
        popup = Popup(title="Текущий бой", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def placeholder_battle_results(self):
        filename = self._current_tournament_filename
        battle_pair = self._current_battle_pair
        battle_index = getattr(self, "_current_battle_index", 0)

        table_store = JsonStore('table_data.json')
        participant1 = battle_pair[0]
        participant2 = battle_pair[1]

        layout = BoxLayout(orientation='horizontal', spacing=10, padding=10)
        input1 = TextInput(hint_text="", input_filter='int', multiline=False, size_hint=(0.3, 1))
        label = Label(text="Нанесённые удары", size_hint=(0.4, 1), halign='center', valign='middle')
        input2 = TextInput(hint_text="", input_filter='int', multiline=False, size_hint=(0.3, 1))
        layout.add_widget(input1)
        layout.add_widget(label)
        layout.add_widget(input2)

        confirm_btn = Button(text="Подтвердить", size_hint_y=None, height=dp(50))

        def on_confirm(instance):
            store = JsonStore(os.path.join("tournaments", filename))
            if store.exists('current_battle'):
                cb = store.get('current_battle')
                battle_index = cb['value'] if isinstance(cb, dict) and 'value' in cb else cb
            else:
                battle_index = 0
            try:
                hits1 = int(input1.text)
                hits2 = int(input2.text)
            except ValueError:
                error_popup = Popup(title="Ошибка", content=Label(text="Введите целые числа!"), size_hint=(0.9, 0.9))
                error_popup.open()
                return

            if hits1 == hits2:
                draw_popup = Popup(
                    title="Ничья",
                    content=Label(text="Ничья! Переиграйте матч."),
                    size_hint=(0.9, 0.9)
                )
                draw_popup.open()
                return

            store = JsonStore(os.path.join("tournaments", filename))
            participants = store.get('participants')
            participants[participant1]['hits'] += hits1
            participants[participant1]['missedHits'] += hits2
            participants[participant1]['hitsDifference'] += (hits1 - hits2)
            participants[participant2]['hits'] += hits2
            participants[participant2]['missedHits'] += hits1
            participants[participant2]['hitsDifference'] += (hits2 - hits1)
            if hits1 > hits2:
                participants[participant1]['points'] += 3
            elif hits2 > hits1:
                participants[participant2]['points'] += 3
            else:
                participants[participant1]['points'] += 1
                participants[participant2]['points'] += 1
            store.put('participants', **participants)
            battle_index += 1
            store.put('current_battle', value=battle_index)
            popup.dismiss()
            self.show_qualifiers_popup(filename)

        confirm_btn.bind(on_press=on_confirm)

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(layout)
        content.add_widget(confirm_btn)
        print("Creating result popup")
        popup = Popup(title="Ввод результатов боя", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def show_playoff_popup(self, filename):
        store = JsonStore(os.path.join("tournaments", filename))
        if store.exists('current_battle'):
            cb = store.get('current_battle')
            battle_index = cb['value'] if isinstance(cb, dict) and 'value' in cb else cb
        else:
            battle_index = 0
        battles = store.get('battles') if store.exists('battles') else []
        if isinstance(battles, dict):
            battles = [battles[str(i)] for i in range(len(battles))]

        if battle_index >= len(battles):
            with open(os.path.join("tournaments", filename), "r", encoding="utf-8") as f:
                data = json.load(f)
            table_store = JsonStore('table_data.json')
            def get_place_text(place_key, place_num):
                member_key = data.get(place_key)
                if member_key and table_store.exists(member_key):
                    member = table_store.get(member_key)
                    return f"{place_num} место: {decode(member['lastName'])} {decode(member['name'])} из команды {decode(member['team'])}"
                else:
                    return f"{place_num} место: -"
            first = get_place_text("first_place", "1")
            second = get_place_text("second_place", "2")
            third = get_place_text("third_place", "3")

            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(text="Турнир завершён!", size_hint_y=None, height=dp(40)))
            content.add_widget(Label(text=first, size_hint_y=None, height=dp(30)))
            content.add_widget(Label(text=second, size_hint_y=None, height=dp(30)))
            content.add_widget(Label(text=third, size_hint_y=None, height=dp(30)))
            btn_results = Button(text="Посмотреть результаты", size_hint_y=None, height=dp(50))
            btn_results.bind(on_press=lambda x: (popup.dismiss(), self.show_interim_results_screen(filename)))
            content.add_widget(btn_results)
            popup = Popup(title="Финал", content=content, size_hint=(0.9, 0.9))
            popup.open()
            return

        battle_number = battle_index + 1
        battle_pair = battles[battle_index]

        table_store = JsonStore('table_data.json')
        def get_info(key):
            member = table_store.get(key)
            return f"{decode(member['lastName'])} {decode(member['name'])} из команды {decode(member['team'])}"

        participant1 = get_info(battle_pair[0])
        participant2 = get_info(battle_pair[1])

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f"Бой №{battle_number}", size_hint_y=None, height=dp(40)))
        content.add_widget(Label(text=f"{participant1} VS {participant2}", size_hint_y=None, height=dp(40)))
        btn_results = Button(text="Объявить результаты боя", size_hint_y=None, height=dp(50))
        btn_interim = Button(text="Посмотреть промежуточные результаты", size_hint_y=None, height=dp(50))
        self._current_tournament_filename = filename
        self._current_battle_pair = battle_pair
        self._current_battle_index = battle_index
        btn_results.bind(on_press=lambda x: self.placeholder_playoff_battle_results())
        btn_interim.bind(on_press=lambda x: (popup.dismiss(), self.show_interim_results_screen(filename)))
        content.add_widget(btn_results)
        content.add_widget(btn_interim)
        popup = Popup(title="Текущий бой", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def placeholder_playoff_battle_results(self):
        filename = self._current_tournament_filename
        battle_pair = self._current_battle_pair
        battle_index = getattr(self, "_current_battle_index", 0)

        table_store = JsonStore('table_data.json')
        participant1 = battle_pair[0]
        participant2 = battle_pair[1]

        layout = BoxLayout(orientation='horizontal', spacing=10, padding=10)
        input1 = TextInput(hint_text="", input_filter='int', multiline=False, size_hint=(0.3, 1))
        label = Label(text="Нанесённые удары", size_hint=(0.4, 1), halign='center', valign='middle')
        input2 = TextInput(hint_text="", input_filter='int', multiline=False, size_hint=(0.3, 1))
        layout.add_widget(input1)
        layout.add_widget(label)
        layout.add_widget(input2)

        confirm_btn = Button(text="Подтвердить", size_hint_y=None, height=dp(50))

        def on_confirm(instance):
            store = JsonStore(os.path.join("tournaments", filename))
            if store.exists('current_battle'):
                cb = store.get('current_battle')
                battle_index = cb['value'] if isinstance(cb, dict) and 'value' in cb else cb
            else:
                battle_index = 0
            try:
                hits1 = int(input1.text)
                hits2 = int(input2.text)
            except ValueError:
                error_popup = Popup(title="Ошибка", content=Label(text="Введите целые числа!"), size_hint=(0.9, 0.9))
                error_popup.open()
                return

            participants = store.get('participants')
            participants[participant1]['hits'] += hits1
            participants[participant1]['missedHits'] += hits2
            participants[participant1]['hitsDifference'] += (hits1 - hits2)
            participants[participant2]['hits'] += hits2
            participants[participant2]['missedHits'] += hits1
            participants[participant2]['hitsDifference'] += (hits2 - hits1)
            if hits1 > hits2:
                participants[participant1]['points'] += 3
            elif hits2 > hits1:
                participants[participant2]['points'] += 3
            else:
                participants[participant1]['points'] += 1
                participants[participant2]['points'] += 1
            store.put('participants', **participants)
            battle_index += 1
            store.put('current_battle', value=battle_index)

            import json
            with open(os.path.join("tournaments", filename), "r", encoding="utf-8") as f:
                data = json.load(f)

            if "playoff_battles" in data and data.get("battles") == data.get("playoff_battles"):
                playoff_list = data.get("playoff_participants_list", [])
                loser = None
                if hits1 > hits2:
                    loser = participant2
                elif hits2 > hits1:
                    loser = participant1
                if loser and loser in playoff_list and len(playoff_list) > 4:
                    playoff_list.remove(loser)
                    data["playoff_participants_list"] = playoff_list
                elif len(playoff_list) == 4:
                    if "playoff_semifinal_winners" not in data:
                        data["playoff_semifinal_winners"] = []
                    if "playoff_semifinal_losers" not in data:
                        data["playoff_semifinal_losers"] = []
                    if hits1 > hits2:
                        winner = participant1
                        loser = participant2
                    elif hits2 > hits1:
                        winner = participant2
                        loser = participant1
                    else:
                        winner = None
                        loser = None
                    if winner and winner not in data["playoff_semifinal_winners"]:
                        data["playoff_semifinal_winners"].append(winner)
                    if loser and loser not in data["playoff_semifinal_losers"]:
                        data["playoff_semifinal_losers"].append(loser)
                    with open(os.path.join("tournaments", filename), "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

            with open(os.path.join("tournaments", filename), "r", encoding="utf-8") as f:
                file_data = json.load(f)
            if "final_battles" in file_data:
                final1 = data["final_battles"][0]
                final2 = data["final_battles"][1]
                if "first_place" not in data:
                    if hits1 > hits2:
                        data["first_place"] = final1[0]
                        data["second_place"] = final1[1]
                    elif hits2 > hits1:
                        data["first_place"] = final1[1]
                        data["second_place"] = final1[0]
                    else:
                        draw_popup = Popup(
                            title="Ничья",
                            content=Label(text="Ничья! Переиграйте матч."),
                            size_hint=(0.9, 0.9)
                        )
                        draw_popup.open()
                        return
                else:
                    if hits1 > hits2:
                        data["third_place"] = final2[0]
                    elif hits2 > hits1: 
                        data["third_place"] = final2[1]
                    else:
                        draw_popup = Popup(
                            title="Ничья",
                            content=Label(text="Ничья! Переиграйте матч."),
                            size_hint=(0.9, 0.9)
                        )
                        draw_popup.open()
                        return
                with open(os.path.join("tournaments", filename), "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)


            battles = store.get('battles') if store.exists('battles') else []
            if isinstance(battles, dict):
                battles = [battles[str(i)] for i in range(len(battles))]

            if battle_index >= len(battles):
                playoff_count = store.get('playoff_participants_count') if store.exists('playoff_participants_count') else 4
                if isinstance(playoff_count, dict):
                    playoff_count = playoff_count.get('value', 4)
                try:
                    playoff_count = int(playoff_count)
                except Exception:
                    playoff_count = 4

                ranking = sorted(
                    participants.items(),
                    key=lambda x: (-x[1]['points'], -x[1]['hitsDifference'])
                )
                top_keys = [k for k, v in ranking[:playoff_count]]

                def get_rating(key):
                    try:
                        return int(table_store.get(key).get('rating', 0))
                    except Exception:
                        return 0
                top_keys_sorted = sorted(top_keys, key=get_rating, reverse=True)

                import json
                with open(os.path.join("tournaments", filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["playoff_participants_list"] = top_keys_sorted

                playoff_participants = top_keys_sorted
                N = len(playoff_participants)
                M = powerOfTwo(N)
                num_first_round = 2 * N - M

                playoff_battles = []
                for i in range(0, num_first_round, 2):
                    if i+1 < num_first_round:
                        playoff_battles.append([playoff_participants[i], playoff_participants[i+1]])

                if "final_battles" not in data:
                    data["playoff_battles"] = playoff_battles
                    data["playoff_results"] = {str(i): None for i in range(len(playoff_battles))}
                    data["playoff_current_battle"] = 0

                    data["battles"] = playoff_battles
                    data["results"] = {str(i): None for i in range(len(playoff_battles))}
                    data["current_battle"] = 0

                    with open(os.path.join("tournaments", filename), "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)

            popup.dismiss()
            self.show_playoff_popup(filename)

        confirm_btn.bind(on_press=on_confirm)

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(layout)
        content.add_widget(confirm_btn)
        popup = Popup(title="Ввод результатов боя", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def show_interim_results_screen(self, filename):
        screen = self.manager.get_screen("InterimResultsScreen")
        screen.show_results(filename)
        self.manager.current = "InterimResultsScreen"
    
    def show_swiss_popup(self, filename):
        with open(os.path.join("tournaments", filename), "r", encoding="utf-8") as f:
            data = json.load(f)
        battles_circles = data.get("battles", [])
        current_circle = data.get("current_circle", 0)
        current_battle = data.get("current_battle", 0)
        participants = data.get("participants", {})

        if not battles_circles or current_circle >= len(battles_circles):
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(text="Турнир завершён!", size_hint_y=None, height=dp(40)))
            btn_results = Button(text="Посмотреть результаты", size_hint_y=None, height=dp(50))
            btn_results.bind(on_press=lambda x: (popup.dismiss(), self.show_interim_results_screen(filename)))
            content.add_widget(btn_results)
            popup = Popup(title="Турнир завершён", content=content, size_hint=(0.9, 0.9))
            popup.open()
            return

        battles = battles_circles[current_circle]
        if current_battle >= len(battles):
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(text="Турнир завершён!", size_hint_y=None, height=dp(40)))
            btn_results = Button(text="Посмотреть результаты", size_hint_y=None, height=dp(50))
            btn_results.bind(on_press=lambda x: (popup.dismiss(), self.show_interim_results_screen(filename)))
            content.add_widget(btn_results)
            popup = Popup(title="Турнир завершён", content=content, size_hint=(0.9, 0.9))
            popup.open()
            return

        battle_number = current_battle + 1
        battle_pair = battles[current_battle]

        table_store = JsonStore('table_data.json')
        def get_info(key):
            member = table_store.get(key)
            return f"{decode(member['lastName'])} {decode(member['name'])} из команды {decode(member['team'])}"

        participant1 = get_info(battle_pair[0])
        participant2 = get_info(battle_pair[1])

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f"Бой №{battle_number}", size_hint_y=None, height=dp(40)))
        content.add_widget(Label(text=f"{participant1} VS {participant2}", size_hint_y=None, height=dp(40)))
        btn_results = Button(text="Объявить результаты боя", size_hint_y=None, height=dp(50))
        btn_interim = Button(text="Посмотреть промежуточные результаты", size_hint_y=None, height=dp(50))
        self._current_tournament_filename = filename
        self._current_circle = current_circle
        self._current_battle = current_battle
        self._current_battle_pair = battle_pair
        content.add_widget(btn_results)
        content.add_widget(btn_interim)
        popup = Popup(title="Текущий бой", content=content, size_hint=(0.9, 0.9))
        btn_results.bind(on_press=lambda x: self.placeholder_swiss_battle_results(popup))
        btn_interim.bind(on_press=lambda x: (popup.dismiss(), self.show_interim_results_screen(filename)))
        popup.open()

    def placeholder_swiss_battle_results(self, popup):
        filename = self._current_tournament_filename
        current_circle = self._current_circle
        current_battle = self._current_battle
        battle_pair = self._current_battle_pair

        with open(os.path.join("tournaments", filename), "r", encoding="utf-8") as f:
            data = json.load(f)

        participants = data["participants"]

        layout = BoxLayout(orientation='horizontal', spacing=10, padding=10)
        input1 = TextInput(hint_text="", input_filter='int', multiline=False, size_hint=(0.3, 1))
        label = Label(text="Нанесённые удары", size_hint=(0.4, 1), halign='center', valign='middle')
        input2 = TextInput(hint_text="", input_filter='int', multiline=False, size_hint=(0.3, 1))
        layout.add_widget(input1)
        layout.add_widget(label)
        layout.add_widget(input2)

        confirm_btn = Button(text="Подтвердить", size_hint_y=None, height=dp(50))

        def on_confirm(instance):
            try:
                hits1 = int(input1.text)
                hits2 = int(input2.text)
            except ValueError:
                error_popup = Popup(title="Ошибка", content=Label(text="Введите целые числа!"), size_hint=(0.9, 0.9))
                error_popup.open()
                return

            if hits1 == hits2:
                draw_popup = Popup(
                    title="Ничья",
                    content=Label(text="Ничья! Переиграйте матч."),
                    size_hint=(0.9, 0.9)
                )
                draw_popup.open()
                return

            participants[battle_pair[0]]['hits'] += hits1
            participants[battle_pair[0]]['missedHits'] += hits2
            participants[battle_pair[0]]['hitsDifference'] += (hits1 - hits2)
            participants[battle_pair[1]]['hits'] += hits2
            participants[battle_pair[1]]['missedHits'] += hits1
            participants[battle_pair[1]]['hitsDifference'] += (hits2 - hits1)
            if hits1 > hits2:
                participants[battle_pair[0]]['points'] += 3
            elif hits2 > hits1:
                participants[battle_pair[1]]['points'] += 3

            data["participants"] = participants
            data["results"][current_circle][str(current_battle)] = [hits1, hits2]
            data["current_battle"] += 1
            if "already_played" not in data:
                data["already_played"] = []
            played_pair = sorted([battle_pair[0], battle_pair[1]])
            if played_pair not in data["already_played"]:
                data["already_played"].append(played_pair)

            if "already_played" not in data:
                data["already_played"] = []
            played_pair = sorted([battle_pair[0], battle_pair[1]])
            if played_pair not in data["already_played"]:
                data["already_played"].append(played_pair)

            battles_in_circle = data["battles"][current_circle]
            if data["current_battle"] >= len(battles_in_circle):
                if data.get("current_circle", 0) + 1 < data.get("total_circles", 1):
                    ranking = sorted(
                        data["participants"].items(),
                        key=lambda x: (-x[1]["points"], -x[1]["hitsDifference"])
                    )
                    sorted_keys = [k for k, v in ranking]
                    already_played = set(tuple(sorted(pair)) for pair in data.get("already_played", []))
                    new_battles = []
                    used = set()
                    n = len(sorted_keys)
                    i = 0
                    skip_first = None
                    while i < n:
                        first = sorted_keys[i]
                        if first in used:
                            i += 1
                            continue
                        found = False
                        for j in range(i+1, n):
                            candidate = sorted_keys[j]
                            if candidate in used:
                                continue
                            k = j
                            while k < n:
                                second = sorted_keys[k]
                                if second in used or second == first:
                                    k += 1
                                    continue
                                pair = tuple(sorted([first, second]))
                                if pair not in already_played:
                                    new_battles.append([first, second])
                                    used.add(first)
                                    used.add(second)
                                    found = True
                                    break
                                k += 1
                            if found:
                                break
                        if not found:
                            print(f"Could not find a valid new battle for {first} in SwissTournament.")
                            skip_first = first
                            used.add(first)
                            i += 1
                    if skip_first is not None:
                        participants[skip_first]["points"] += 3

                    data["battles"].append(new_battles)
                    data["results"].append({str(idx): None for idx in range(len(new_battles))})
                    data["current_circle"] += 1
                    data["current_battle"] = 0
                else:
                    pass

            with open(os.path.join("tournaments", filename), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            popup.dismiss()
            self.show_swiss_popup(filename)

        confirm_btn.bind(on_press=on_confirm)

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(layout)
        content.add_widget(confirm_btn)
        popup = Popup(title="Ввод результатов боя", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def on_press_back_button(self, instance):
        self.manager.current = "TournamentMenu"

class InterimResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.add_widget(self.layout)

    def show_results(self, filename):
        self.layout.clear_widgets()
        store = JsonStore(os.path.join("tournaments", filename))
        participants = store.get('participants')

        ranking = []
        for key, data in participants.items():
            points = data.get('points', 0)
            hits_diff = data.get('hitsDifference', 0)
            ranking.append((key, points, hits_diff))

        ranking.sort(key=lambda x: (-x[1], -x[2]))

        table_store = JsonStore('table_data.json')
        header = Label(
            text="Место | Участник | Очки | Разница ударов",
            size_hint_y=None,
            height=dp(40),
            bold=True,
            color=(0, 0, 0, 1)
        )
        self.layout.add_widget(header)

        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=5)
        grid.bind(minimum_height=grid.setter('height'))

        for idx, (key, points, hits_diff) in enumerate(ranking, 1):
            member = table_store.get(key)
            name = f"{decode(member['lastName'])} {decode(member['name'])}"
            row = Label(
                text=f"{idx}. {name} — {points} очков, разница ударов: {hits_diff}",
                size_hint_y=None,
                height=dp(30),
                color=(0, 0, 0, 1)
            )
            grid.add_widget(row)

        scroll.add_widget(grid)
        self.layout.add_widget(scroll)

        back_button = Button(
            text="Назад к турниру",
            size_hint_y=None,
            height=dp(50),
            background_color=[134 / 255, 130 / 255, 102 / 255, 1],
        )
        back_button.bind(on_press=self.go_back)
        self.layout.add_widget(back_button)

    def go_back(self, instance):
        self.manager.current = "SavedTournamentsList"


class MemberSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.add_widget(self.layout)
        self.total_participants = 0
        self.callback = None

    def setup(self, total_participants, member_keys, callback):
        self.layout.clear_widgets()
        self.total_participants = total_participants
        self.callback = callback

        global store
        scroll = ScrollView(size_hint=(1, 0.8))
        grid = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=5)
        grid.bind(minimum_height=grid.setter('height'))

        self.checkboxes = {}
        for key in member_keys:
            member = store.get(key)
            label_text = f"{decode(member['lastName'])} {decode(member['name'])} {decode(member['fatherName'])} из команды {decode(member['team'])}"
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=10)
            btn = ToggleButton(
                text=label_text,
                size_hint_y=None,
                height=dp(40),
                group=None,
                background_normal='',
                background_color=[0.9, 0.9, 0.9, 1],
                background_down='',
                color=(0,0,0,1),
            )
            def on_state(instance, value):
                if value == 'down':
                    instance.background_color = [0.3, 0.7, 0.3, 1]
                else:
                    instance.background_color = [0.9, 0.9, 0.9, 1]

            btn.bind(state=on_state)

            grid.add_widget(btn)
            self.checkboxes[key] = btn

        scroll.add_widget(grid)
        self.layout.add_widget(scroll)

        self.info_label = Label(text=f"Выберите ровно {total_participants} участников", size_hint=(1, 0.1), color=(0,0,0,1))
        self.layout.add_widget(self.info_label)

        btn_box = BoxLayout(size_hint=(1, 0.1))
        ok_btn = Button(text="OK")
        cancel_btn = Button(text="Отмена")
        btn_box.add_widget(ok_btn)
        btn_box.add_widget(cancel_btn)
        self.layout.add_widget(btn_box)

        ok_btn.bind(on_press=self.on_ok)
        cancel_btn.bind(on_press=self.on_cancel)

    def on_ok(self, instance):
        selected = [k for k, btn in self.checkboxes.items() if btn.state == 'down']
        if len(selected) != self.total_participants:
            self.info_label.text = f"Выберите ровно {self.total_participants} участников!"
            return
        if self.callback:
            self.callback(selected)
        self.manager.current = "TournamentMenu"

    def on_cancel(self, instance):
        self.manager.current = "TournamentMenu"

class HBoxLayout(MDApp):
    def build(self):
        background_screen = Builder.load_string(BackGround)
        screenManager = ScreenManager()
        screenManager.add_widget(MainScreen(name="main"))
        screenManager.add_widget(listScreen(name="peopleList"))
        screenManager.add_widget(TournamentMenu(name="TournamentMenu"))
        screenManager.add_widget(TournamentCreationScreen(name="TournamentCreationScreen"))
        screenManager.add_widget(QualifiersTournament(name="QualifiersTournament"))
        screenManager.add_widget(QualifiersPlayOffTournament(name="QualifiersPlayOffTournament"))
        screenManager.add_widget(SwissTournament(name="SwissTournament"))
        screenManager.add_widget(SavedTournamentsList(name="SavedTournamentsList"))
        screenManager.add_widget(InterimResultsScreen(name="InterimResultsScreen"))
        screenManager.add_widget(MemberSelectionScreen(name="MemberSelectionScreen"))
        root = background_screen
        root.add_widget(screenManager)

        return root


if __name__ == "__main__":
    app = HBoxLayout()
    app.run()
