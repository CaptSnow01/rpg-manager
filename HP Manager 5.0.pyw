import customtkinter as ctk # Estou em characters... tá indo
import tkinter as tk
from tkinter import ttk  # Import ttk for Tooltips
from idlelib.tooltip import Hovertip #
from PIL import Image
from CTkMessagebox import CTkMessagebox, ctkmessagebox
from customtkinter import CTk, CTkComboBox, CTkFrame, CTkButton, CTkLabel, CTkEntry, CTkToplevel
from customtkinter import CTkScrollbar, CTkCanvas
from customtkinter import CTkProgressBar
from customtkinter import CTkInputDialog
from customtkinter import CTkFont, CTkImage
from CTkSpinbox import *
from tkinter import simpledialog, messagebox
from tkinter import ttk
from tkinter.ttk import Progressbar, Style, Combobox
import json
import os

# Caminho para o ícone do HP (simbolizado como o ícone do Plus)
plus_icon_path = "C:/Users/hacus/Downloads/plus-sign.png"
mana_icon_path = "C:/Users/hacus/Downloads/mana-sign.png"
healing_icon_path = "C:/Users/hacus/Downloads/Healing_Icon.png"
damage_icon_path = "C:/Users/hacus/Downloads/damage_icon.png"
alter_hp_path = "C:/Users/hacus/Downloads/alter_hp.png"
mana_useorheal_path = "C:/Users/hacus/Downloads/game_skill_magic_fire_fireball-512.png"

blood_icon_path = "C:/Users/hacus/Downloads/blood-drop-svgrepo-com(1).png"
dot_heal_icon_path = "C:/Users/hacus/Downloads/plus.png"

# Carregar a imagem do ícone do HP
hp_icon_image = Image.open(plus_icon_path)
mana_icon_image = Image.open(mana_icon_path)
healing_icon_path = Image.open(healing_icon_path)
damage_icon_path = Image.open(damage_icon_path)
alter_hp_path = Image.open(alter_hp_path)
mana_useorheal_path = Image.open(mana_useorheal_path)

blood_icon_image = Image.open(blood_icon_path)
dot_heal_icon_image = Image.open(dot_heal_icon_path)

# Criar o CTkImage para o ícone do HP
hp_icon = ctk.CTkImage(light_image=hp_icon_image, size=(10, 10))
mana_icon = ctk.CTkImage(light_image=mana_icon_image, size=(10, 10))
damage_icon = CTkImage(light_image=damage_icon_path, size=(10, 10))
healing_icon = CTkImage(light_image=healing_icon_path, size=(10, 10))
mana_useorheal_icon = CTkImage(light_image=mana_useorheal_path, size=(15,15))

blood_icon = ctk.CTkImage(light_image=blood_icon_image, size=(16, 16))  # Ajuste o tamanho conforme necessário
dot_heal_icon = ctk.CTkImage(light_image=dot_heal_icon_image, size=(16, 16)) 

class Character:
    def __init__(self, name, hp, mp, max_hp, max_mp, level=1, exp=0, max_exp=1, player_gold=1):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.max_hp = max_hp
        self.max_mp = max_mp
        self.level = level
        self.exp = exp
        self.max_exp = max_exp
        self.skills = {}  # Dicionário para armazenar as habilidades do personagem
        self.temp_buffs_debuffs = {}  # Dicionário para armazenar buffs/debuffs temporários
        self.player_gold = player_gold
        self.hp_label = None  # Para armazenar o label de HP
        self.hp_bar = None    # Para armazenar a barra de HP
        self.mp_label = None  # Para armazenar o label de MP
        self.mp_bar = None    # Para armazenar a barra de MP
        self.bar_data = {}  # Inicializa bar_data como um dicionário vazio
        self.bar_widgets = {} # Dicionário para armazenar os widgets das barras

    def add_temp_buff_debuff(self, name, duration, buff_type="buff_debuff", **kwargs):
        if buff_type == "dot":
            dot_amount = kwargs.get('dot_amount', 0)
            formatted_text = f"{name} ({dot_amount:+d} HP por {duration} turnos)"
        else:
            formatted_text = name  # Mantém a formatação padrão para buffs/debuffs regulares

        self.temp_buffs_debuffs[name] = {
            'duration': duration,
            'remaining_duration': duration,
            'dot_amount': kwargs.get('dot_amount', 0),
            'type': buff_type,
            'formatted_text': formatted_text,  # Adiciona o texto formatado
            **kwargs 
        }

    def decrease_temp_buff_debuff_durations(self):
        buffs_to_remove = []
        for buff_debuff_name, buff_debuff_data in self.temp_buffs_debuffs.items():
            if buff_debuff_data['remaining_duration'] > 0:
                buff_debuff_data['remaining_duration'] -= 1
            if buff_debuff_data['remaining_duration'] == 0:
                buffs_to_remove.append(buff_debuff_name)
        for buff_name in buffs_to_remove:
            del self.temp_buffs_debuffs[buff_name]

    def decrease_buff_debuff_durations_by_turn(self):
        for buff_debuff_data in self.temp_buffs_debuffs.values():
            if buff_debuff_data['remaining_duration'] > 0:
                buff_debuff_data['remaining_duration'] -= 1

    def remove_buff_debuff(self, name):
        if name in self.temp_buffs_debuffs:
            del self.temp_buffs_debuffs[name]
        else:
            messagebox.showerror("Erro", f"{self.name} não possui o buff/debuff '{name}'.")

    def delete_skill(self, skill_name):
        if skill_name in self.skills:
            del self.skills[skill_name]
            return True
        else:
            return False

    def add_skill(self, name, cooldown, mana_cost=0, hp_cost=0, description="", temp_buff_debuff=None):
        self.skills[name] = {
            'cooldown': cooldown,
            'mana_cost': mana_cost,
            'hp_cost': hp_cost,
            'remaining_cooldown': 0,  # Adiciona um campo para rastrear o cooldown restante
            'description': description,  # Adiciona a descrição da habilidade
            'temp_buff_debuff': temp_buff_debuff  # Adiciona o buff/debuff temporário à habilidade, se fornecido
        }
            
    def use_skill(self, character, name):
        skill = character.skills.get(name)
        if skill:
            if skill['remaining_cooldown'] == 0:
                if character.hp >= skill['hp_cost'] and character.mp >= skill['mana_cost']:
                    character.hp -= skill['hp_cost']
                    character.mp -= skill['mana_cost']
                    skill['remaining_cooldown'] = skill['cooldown']

                    # Verifica se a habilidade adiciona um buff/debuff temporário
                    if 'temp_buff_debuff' in skill:
                        character.add_temp_buff_debuff(skill['temp_buff_debuff']['name'], skill['temp_buff_debuff']['duration'])
                else:
                    messagebox.showerror("Erro", "Mana ou HP insuficiente para usar esta habilidade.")
                    return False
            else:
                # Habilidade está em cooldown, perguntar se deseja reutilizar
                reuse_option = messagebox.askyesno("Habilidade em cooldown", f"A habilidade '{name}' está em cooldown. Deseja reutilizá-la agora, resetando seu cooldown?")
                if reuse_option:
                    character.reset_skill_cooldown(name)
                    skill['remaining_cooldown'] = 0  # Ajusta remaining_cooldown para 0 após o reset
                    self.update_character_display()  # Atualiza a exibição após resetar o cooldown
                    return True  # Retorna True após reutilizar a habilidade
                else: 
                    return False  # Retorna False se não quiser reutilizar a habilidade
        else:
            messagebox.showerror("Erro", "Habilidade inexistente.")
            return False

    def decrease_skill_cooldowns(self):
        for skill in self.skills.values():
            if skill['remaining_cooldown'] > 0:
                skill['remaining_cooldown'] -= 1

    def reset_skill_cooldown(self, skill_name):
        if skill_name in self.skills:
            self.skills[skill_name]['remaining_cooldown'] = 0

    def to_dict(self):
        return {
            "name": self.name,
            "hp": self.hp,
            "mp": self.mp,
            "max_hp": self.max_hp,
            "max_mp": self.max_mp,
            "level": self.level,
            "exp": self.exp,
            "max_exp": self.max_exp,
            "skills": {name: {**skill, 'description': skill.get('description', '')} for name, skill in self.skills.items()},
            "temp_buffs_debuffs": self.temp_buffs_debuffs,  # inclui os buffs/debuffs temporários no dicionário retornado
            "player_gold": self.player_gold,
            "bar_data": {  
                bar_name: {
                    'color': bar_data['color'],
                    'current_value': bar_data['current_value'],
                    'max_value': bar_data['max_value']
                } for bar_name, bar_data in self.bar_data.items()
            } if hasattr(self, 'bar_data') else {}  # Adiciona bar_data se existir
        }

    @classmethod
    def from_dict(cls, data):
        character = cls(data["name"], data["hp"], data["mp"], data["max_hp"], data["max_mp"], data.get("level", 1), data.get("exp", 0), data.get("max_exp", 1))
        character.skills = data.get("skills", {})
        for skill_name, skill_data in character.skills.items():
            skill_data.setdefault('description', '')  # Garante que cada habilidade tenha uma descrição, mesmo se não estiver presente no dicionário
        character.temp_buffs_debuffs = data.get("temp_buffs_debuffs", {})
        character.player_gold = data.get("player_gold", 1)
        character.bar_data = data.get("bar_data", {})  # Inicializa se não existir
        for bar_data in character.bar_data.values():
            bar_data.setdefault('bar_frame', None)
            bar_data.setdefault('bar_label', None)
            bar_data.setdefault('bar', None)
            bar_data.setdefault('bar_value_label', None) 
            bar_data.setdefault('remove_bar_button', None)
        return character

    def use_skill(self, name):
        skill = self.skills.get(name)
        if skill:
            if skill['remaining_cooldown'] == 0:
                if self.hp >= skill['hp_cost'] and self.mp >= skill['mana_cost']:
                    self.hp -= skill['hp_cost']
                    self.mp -= skill['mana_cost']
                    skill['remaining_cooldown'] = skill['cooldown']

                    # Verifica se a habilidade adiciona um buff/debuff temporário
                    if 'temp_buff_debuff' in skill and skill['temp_buff_debuff']:
                        self.add_temp_buff_debuff(skill['temp_buff_debuff']['name'], skill['temp_buff_debuff']['duration'])

                    # Mensagem de confirmação com descrição da habilidade
                    messagebox.showinfo("Habilidade Utilizada", f"Habilidade '{name}' usada com sucesso!\n{skill['description']}")

                    # Chama o método update_character_display da instância da classe App
                    app.update_character_display()  
                    return True
                else:
                    messagebox.showerror("Erro", "Mana ou HP insuficiente para usar esta habilidade.")
                    return False
            else:
                # Habilidade está em cooldown, perguntar se deseja reutilizar
                reuse_option = messagebox.askyesno("Habilidade em cooldown", f"A habilidade '{name}' está em cooldown. Deseja reutilizá-la agora, resetando seu cooldown?")
                if reuse_option:
                    self.reset_skill_cooldown(name)
                    skill['remaining_cooldown'] = 0  # Ajusta remaining_cooldown para 0 após o reset
                    app.update_character_display()  # Atualiza a exibição após resetar o cooldown
                    return True  # Retorna True após reutilizar a habilidade
                else:
                    return False  # Retorna False se não quiser reutilizar a habilidade
        else:
            messagebox.showerror("Erro", "Habilidade inexistente.")
            return False
            
class NPC:
    def __init__(self, name, max_hp):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.temp_buffs_debuffs = {}
        self.hp_color = "white"  # Cor padrão para a barra de vida
        self.spinbox_value = 0  # Valor inicial do spinbox
        self.spinbox = None  # Para armazenar o spinbox
        self.on_spinbox_change = None  # Para armazenar a função de callback
        self.hp_label = None  # Para armazenar o label de HP
        self.hp_bar = None    # Para armazenar a barra de HP
        self.dot_icons_frame = None  # Frame para armazenar os ícones de DoT

    def to_dict(self):
        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "temp_buffs_debuffs": self.temp_buffs_debuffs,
            "hp_color": self.hp_color,  # Adiciona a cor da barra de vida ao dicionário retornado
            "spinbox_value": self.spinbox_value 
        }

    @classmethod
    def from_dict(cls, data):
        npc = cls(data["name"], data["max_hp"])
        npc.hp = data.get("hp", data["max_hp"])
        npc.temp_buffs_debuffs = data.get("temp_buffs_debuffs", {})
        npc.hp_color = data.get("hp_color", "red")  # Define a cor padrão como vermelha se não houver cor definida
        npc.spinbox_value = data.get("spinbox_value", 0)  # Carrega o valor do spinbox ou define como 0 se não existir
        return npc

    def remove_buff_debuff(self, name):
        if name in self.temp_buffs_debuffs:
            del self.temp_buffs_debuffs[name]
        else:
            messagebox.showerror("Erro", f"{self.name} não possui o buff/debuff '{name}'.")

    def add_temp_buff_debuff(self, buff_debuff_name, duration, dot_amount=None, heal_amount=None):
        """Adds a temporary buff or debuff to the NPC.

        Args:
            buff_debuff_name (str): The name of the buff or debuff.
            duration (int): The duration of the buff or debuff in turns.
            dot_amount (int, optional): The amount of damage per turn if it's a DoT.
            heal_amount (int, optional): The amount of healing per turn if it's a HoT.
        """
        if buff_debuff_name in self.temp_buffs_debuffs:
            # If the buff/debuff already exists, update its duration
            self.temp_buffs_debuffs[buff_debuff_name]['remaining_duration'] = duration
        else:
            # Otherwise, add a new buff/debuff
            self.temp_buffs_debuffs[buff_debuff_name] = {
                'remaining_duration': duration,
                'dot_amount': dot_amount,
                'heal_amount': heal_amount
            }

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Character Status Manager")
        self.root.geometry("1200x900")
        bg_color = "#393D43"  # Escolha a cor padrão do ctk aqui
        self.root.configure(bg=bg_color)

        self.exhaustion_value = 0  # Valor inicial da exaustão

        self.players = []
        self.npcs = []  # Lista para armazenar NPCs
        self.turn_count = 0  # Inicializa o contador de turnos
        self.combatant_labels = []
        self.combatant = []
        self.character_combobox = None  # Add this line to store the combobox reference
        self.create_widgets()

    def get_selected_character(self):
        selected_character_name = self.dot_target_combobox.get()
        if selected_character_name:
            for character in self.players + self.npcs:
                if character.name == selected_character_name:
                    return character
        return None

    def create_widgets(self):
        control_frame = CTkFrame(self.root, fg_color="transparent", corner_radius=0, border_width=0)
        control_frame.pack(anchor=tk.W)  # Ancora o frame à esquerda (oeste)

        self.create_player_button = CTkButton(control_frame, text="Criar Player", command=self.create_player,
                                            width=50, height=10, corner_radius=0,
                                            border_color='#D3A62C', border_width=1,
                                            hover_color='black', fg_color='#2A2A33',
                                            text_color='grey75', font=('Helvetica', 12))
        self.create_player_button.pack(side=tk.LEFT, padx=1, pady=5)

        self.save_button = CTkButton(control_frame, text="Salvar", command=self.save_data,
                                    width=50, height=10, corner_radius=0,
                                    border_color='#D3A62C', border_width=1,
                                    hover_color='black', fg_color='#2A2A33',
                                    text_color='grey75', font=('Helvetica', 12))
        self.save_button.pack(side=tk.LEFT, padx=1, pady=5)

        self.load_button = CTkButton(control_frame, text="Carregar Progresso", command=self.load_data,
                                    width=50, height=10, corner_radius=0,
                                    border_color='#D3A62C', border_width=1,
                                    hover_color='black', fg_color='#2A2A33',
                                    text_color='grey75', font=('Helvetica', 12))
        self.load_button.pack(side=tk.LEFT, padx=1, pady=5)

        # Um espaço vazio para empurrar o botão para a direita
        ctk.CTkLabel(control_frame, height=1, text="").pack(side=tk.LEFT, padx=20)

        self.create_npc_button = CTkButton(control_frame, text="Criar NPC", command=self.create_npc,
                                        width=50, height=10, corner_radius=0,
                                        border_color='#D3A62C', border_width=2,
                                        hover_color='#1D1C21', fg_color='#2A2A33',
                                        text_color='#C9B273', font=('Helvetica', 12))
        self.create_npc_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.delete_npc_button = ctk.CTkButton(control_frame,
                                            text="Deletar NPC",
                                            command=self.delete_npc,
                                            width=20,
                                            height=10,
                                            fg_color=('#2A2A33'),
                                            border_color=('#D3A62C'),
                                            corner_radius=0,
                                            border_width=2,
                                            hover_color=('#520C0A'),
                                            text_color=('#C9B273'),
                                            font=('Helvetica', 12))
        self.delete_npc_button.pack(side=ctk.LEFT, padx=0, pady=5)  # Ajuste os valores de padx e pady conforme necessário para o espaçamento desejado

        # Botão "Adicionar Barra" movido para cá, ao lado do botão "Criar NPC"
        self.add_bar_button = CTkButton(control_frame,
                                        text="Adicionar Barra",
                                        command=self.open_add_bar_window,  # Agora a função está disponível
                                        width=50,
                                        height=10,
                                        corner_radius=0,
                                        border_color='#D3A62C',
                                        border_width=1,
                                        hover_color='black',
                                        fg_color='#2A2A33',
                                        text_color='grey75',
                                        font=('Helvetica', 12))
        self.add_bar_button.pack(side=tk.LEFT, padx=25, pady=5)

        self.dot_target_combobox = ctk.CTkComboBox(control_frame, values=[])
        self.dot_target_combobox.set("Selecione um alvo") 
        self.dot_target_combobox.pack(side=tk.LEFT, padx=10, pady=5)  # Use pack for the combobox

        self.dot_target_combobox.configure(
            width=200,
            height=20,
            fg_color=('#2A2A33'),
            border_color=('#D3A62C'),
            text_color=('#C9B273'),
            dropdown_fg_color=('#2A2A33'),
            dropdown_hover_color=('#1D1C21'),
            dropdown_text_color=('#C9B273'),
            button_color=('#616161'),
            button_hover_color=('#181823'),
            border_width=1,
            font=('Helvetica', 11),
            dropdown_font=('Helvetica', 11)
        )

        self.apply_dot_button = CTkButton(control_frame, 
                                        text="Aplicar DoT", 
                                        command=self.apply_dot,
                                        width=50, height=10, corner_radius=0,
                                        border_color='#D3A62C', border_width=1,
                                        hover_color='black', fg_color='#2A2A33',
                                        text_color='grey75', font=('Helvetica', 12))
        self.apply_dot_button.pack(side=tk.LEFT, padx=5, pady=5)  # Use pack for the button, adjust padx for spacing

        # Criando o frame exp_frame (FG, não BG)
        self.exp_frame = ctk.CTkFrame(self.root, height=35)
        self.exp_frame.configure(fg_color="#393D43", corner_radius=0, border_width=2, border_color="#D3A62C")  # Define a cor de fundo para #121329
        self.exp_frame.pack(fill=tk.X)

        self.exp_frame.pack_propagate(False)

        self.level_label = ctk.CTkLabel(self.exp_frame, text="Level: 1", font=("Helvetica", 12), height=15)
        self.level_label.pack(side=tk.LEFT, padx=10)

        self.exp_label = ctk.CTkLabel(self.exp_frame, text="EXP: 0/1", font=("Helvetica", 12), height=15)
        self.exp_label.pack(side=tk.LEFT, padx=10)

        self.exp_bar = ctk.CTkProgressBar(self.exp_frame, width=250, fg_color="#787878", progress_color="#EAEAEA")
        self.exp_bar.pack(side=tk.LEFT, padx=10, pady=2)

        # Botão "Add XP"
        self.add_exp_button = ctk.CTkButton(self.exp_frame, text="Add XP", command=self.add_exp,
                                            width=50,
                                            height=25,
                                            fg_color='#2A2A33',
                                            border_color='#D3A62C',
                                            corner_radius=0,
                                            border_width=1,
                                            hover_color='#1D1C21',
                                            text_color='#C9B273',
                                            font=('Helvetica', 12))
        self.add_exp_button.pack(side=tk.LEFT, padx=2)

        # Botão "Set Max XP"
        self.set_max_exp_button = ctk.CTkButton(self.exp_frame, text="Set Max", command=self.set_max_exp,
                                                width=50,
                                                height=25,
                                                fg_color='#2A2A33',
                                                border_color='#D3A62C',
                                                corner_radius=0,
                                                border_width=1,
                                                hover_color='#1D1C21',
                                                text_color='#C9B273',
                                                font=('Helvetica', 12))
        self.set_max_exp_button.pack(side=tk.LEFT, padx=2)

        # Botão "Set Current Level"
        self.set_level_button = ctk.CTkButton(self.exp_frame, text="Set Level", command=self.set_level,
                                            width=50,
                                            height=25,
                                            fg_color='#2A2A33',
                                            border_color='#D3A62C',
                                            corner_radius=0,
                                            border_width=1,
                                            hover_color='#1D1C21',
                                            text_color='#C9B273',
                                            font=('Helvetica', 12))
        self.set_level_button.pack(side=tk.LEFT, padx=2)

        self.character_frame = ctk.CTkFrame(self.root)
        self.character_frame.pack(fill=tk.BOTH, expand=True)

        # Frame principal para os NPCs com cor mais escura
        self.npc_container = CTkFrame(self.root, fg_color="#2A2A2A")  # Cor escura
        self.npc_container.pack(fill=tk.BOTH, expand=True, pady=10)  # Preencher verticalmente

        # Canvas para os NPCs
        self.npc_canvas = CTkCanvas(self.npc_container)
        self.npc_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Barra de rolagem
        self.npc_scrollbar = CTkScrollbar(self.npc_container, orientation="vertical", command=self.npc_canvas.yview)
        self.npc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.npc_canvas.configure(yscrollcommand=self.npc_scrollbar.set)

        # Frame que vai dentro do canvas para os NPCs
        self.npc_frame = CTkFrame(self.npc_canvas, fg_color="#2A2A2A")
        self.npc_canvas.create_window((0, 0), window=self.npc_frame, anchor="nw")

        # Atualiza a barra de rolagem conforme o conteúdo cresce
        self.npc_frame.bind("<Configure>", lambda e: self.npc_canvas.configure(scrollregion=self.npc_canvas.bbox("all")))

        self.update_character_display()
# Frame para combatentes
        self.combatant_names_frame = ctk.CTkFrame(self.root, fg_color="#393D43", corner_radius=0, border_width=2, border_color="#D3A62C")
        self.combatant_names_frame.configure(height=32)  # Aumenta a altura para 35 pixels
        self.combatant_names_frame.pack_propagate(False)  # Impede que o frame se adapte aos seus filhos
        self.combatant_names_frame.pack(fill=tk.X, pady=(0, 5))
# Fim para o Frame
        self.exhaustion_frame = ctk.CTkFrame(self.root)
        self.exhaustion_frame.pack(fill=tk.X)

        self.turn_label = ctk.CTkLabel(self.exhaustion_frame, text="Turno: 0")
        self.turn_label.pack(side=tk.LEFT, padx=3)

        # Botão para adicionar turno
        self.add_turn_button = ctk.CTkButton(
            self.exhaustion_frame,
            text=" +1",
            command=self.add_turn,
            width=10,  # Ajuste conforme necessário
            height=2,  # Ajuste conforme necessário
            corner_radius=0,
            border_width=1,
            fg_color="#2A2A33",
            border_color=('#D3A62C'), 
            hover_color='#305C6E',
            text_color='#C9B273',
            font=('Helvetica', 13, 'bold')
        )
        self.add_turn_button.pack(side=tk.LEFT, padx=1)

        # Botão para remover turno
        self.remove_turn_button = ctk.CTkButton(
            self.exhaustion_frame,
            text="  -1",
            command=self.remove_turn,
            width=10,  # Ajuste conforme necessário
            height=2,  # Ajuste conforme necessário
            corner_radius=0,
            border_width=1,
            fg_color="#2A2A33",
            border_color=('#D3A62C'), 
            hover_color='#852525',
            text_color='#C9B273',
            font=('Helvetica', 13, 'bold'))
        self.remove_turn_button.pack(side=tk.LEFT, padx=1)
        
        # Botão para encerrar combate
        self.end_combat_button = ctk.CTkButton(
            self.exhaustion_frame,
            text="Encerrar Combate",
            command=self.end_combat,
            width=10,  # Ajuste conforme necessário
            height=2,  # Ajuste conforme necessário
            corner_radius=0,
            border_width=1,
            fg_color="#2A2A33",
            border_color=('#D3A62C'), 
            hover_color='#193816',
            text_color='#C9B273',
            font=('Helvetica', 13, 'bold'))
        self.end_combat_button.pack(side=tk.LEFT, padx=1)

# Seção de Combatentes e iniciativa

        # Frame para os nomes dos combatentes
        self.add_combatant_button = ctk.CTkButton(
            self.exhaustion_frame,
            text="Add",
            command=self.add_combatant,
            width=50,
            height=25,
            corner_radius=0,
            border_width=1,
            fg_color='#2A2A33',
            border_color=('#D3A62C'),
            hover_color='#1D1C21',
            text_color='#C9B273',
            font=('Helvetica', 10)
        )
        self.add_combatant_button.pack(side=tk.LEFT, padx=10)  # Ajuste o padx conforme necessário

        self.prev_turn_button = ctk.CTkButton(self.exhaustion_frame, text="◄", command=self.prev_turn, width=30, height=25)
        self.prev_turn_button.configure(fg_color='#2A2A33', border_color=('#D3A62C'), hover_color='#1D1C21', text_color='#C9B273', font=('Helvetica', 10, 'bold'))
        self.prev_turn_button.pack(side=tk.LEFT, padx=2)

        self.next_turn_button = ctk.CTkButton(self.exhaustion_frame, text="►", command=self.next_turn, width=30, height=25)
        self.next_turn_button.configure(fg_color='#2A2A33', border_color=('#D3A62C'), hover_color='#1D1C21', text_color='#C9B273', font=('Helvetica', 10, 'bold'))
        self.next_turn_button.pack(side=tk.LEFT, padx=2)

        self.reorder_button = ctk.CTkButton(self.exhaustion_frame, text="Reorder", command=self.reorder_combatant, width=60, height=25)
        self.reorder_button.configure(fg_color='#2A2A33', border_color=('#D3A62C'), hover_color='#1D1C21', text_color='#C9B273', font=('Helvetica', 10))
        self.reorder_button.pack(side=tk.LEFT, padx=2)

        self.remove_combatant_button = ctk.CTkButton(self.exhaustion_frame, text="Remove", command=self.remove_combatant, width=60, height=25)
        self.remove_combatant_button.configure(fg_color='#2A2A33', border_color=('#D3A62C'), hover_color='#520C0A', text_color='#C9B273', font=('Helvetica', 10))
        self.remove_combatant_button.pack(side=tk.LEFT, padx=2)

        self.remove_all_combatant_button = ctk.CTkButton(self.exhaustion_frame, text="Remove All", command=self.remove_all_combatant, width=60, height=25)
        self.remove_all_combatant_button.configure(fg_color='#2A2A33', border_color=('#D3A62C'), hover_color='#520C0A', text_color='#C9B273', font=('Helvetica', 10))
        self.remove_all_combatant_button.pack(side=tk.LEFT, padx=2)

 ################### Exaustão abaiixo ##############
        self.exhaustion_label = ctk.CTkLabel(self.exhaustion_frame, text="Exaustão:", font=("Helvetica", 12))
        self.exhaustion_label.pack(side=tk.LEFT, padx=(10, 0))

        self.exhaustion_bar = ctk.CTkProgressBar(self.exhaustion_frame, width=200, height=12, mode='determinate',
                                                 fg_color="grey75")
        self.exhaustion_bar.pack(side=tk.LEFT, padx=5)

        self.exhaustion_value_label = ctk.CTkLabel(self.exhaustion_frame, text=str(self.exhaustion_value), fg_color=("white", "black"), font=("Arial", 12, "bold"))
        self.exhaustion_value_label.pack(side=tk.LEFT)

        self.edit_exhaustion_button = ctk.CTkButton(
            self.exhaustion_frame,
            text="Editar Exaustão",
            command=self.edit_exhaustion,
            width=50,
            height=10,
            fg_color='#2A2A33',
            border_color='#D3A62C',
            corner_radius=0,
            border_width=1,
            hover_color='#1D1C21',
            text_color='#C9B273',
            font=('Helvetica', 12)
        )
        self.edit_exhaustion_button.pack(side=tk.LEFT, padx=(10, 0))  # 10 pixels à esquerda, 0 pixels à direita

    def open_add_bar_window(self):
        if not self.players:
            messagebox.showinfo("Informação", "Nenhum jogador para adicionar barra.")
            return

        # Criar a janela de diálogo usando CTkToplevel
        add_bar_window = ctk.CTkToplevel(self.root)
        add_bar_window.title("Adicionar Barra")
        add_bar_window.attributes('-topmost', 'true')
        add_bar_window.minsize(300, 150)

        # Criar o combobox para seleção do jogador
        player_names = [player.name for player in self.players]
        player_combobox = ctk.CTkComboBox(add_bar_window, values=player_names)
        player_combobox.pack(pady=10)

        def confirm_add_bar():
            selected_player_name = player_combobox.get()
            player_to_add_bar = next((player for player in self.players if player.name == selected_player_name), None)
            if player_to_add_bar:
                # Obtém o nome da barra usando CTkInputDialog
                dialog_name = CTkInputDialog(text="Nome da barra:", title="Adicionar Barra")
                bar_name = dialog_name.get_input()

                if bar_name:  # Verifica se o usuário não cancelou a entrada do nome
                    # Obtém a cor da barra usando CTkInputDialog
                    dialog_color = CTkInputDialog(text="Cor da barra (hexadecimal, ex: #FF0000):", title="Adicionar Barra")
                    bar_color = dialog_color.get_input()

                    if bar_color:  # Verifica se o usuário não cancelou a entrada da cor
                        self.add_bar_to_player(player_to_add_bar, bar_name, bar_color)
                    else:
                        messagebox.showinfo("Informação", "Adição da barra cancelada.")

                    add_bar_window.destroy()
                else:
                    messagebox.showinfo("Informação", "Adição da barra cancelada.")
            else:
                messagebox.showerror("Erro", "Jogador não encontrado.")

        add_bar_button = ctk.CTkButton(add_bar_window, text="Adicionar", command=confirm_add_bar)
        add_bar_button.pack(pady=10)

        # Centralizar a janela na tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = add_bar_window.winfo_reqwidth()
        window_height = add_bar_window.winfo_reqheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        add_bar_window.geometry(f"+{x}+{y}")

    def delete_character(self, character):
        if character in self.players:
            # Função para exibir o aviso de confirmação
            resposta = messagebox.askyesno("Confirmação", f"Tem certeza que deseja deletar o personagem?")

            if resposta:
                self.players.remove(character)
                self.update_character_display()
        else:
            messagebox.showerror("Erro", "Personagem não encontrado na lista.")

    def add_bar_to_player(self, player, bar_name, bar_color):
        # Cria um dicionário para armazenar os dados da barra, se ainda não existir
        if not hasattr(player, 'bar_data'):
            player.bar_data = {}

        # Cria os dados da barra para este nome específico, usando a cor fornecida
        player.bar_data[bar_name] = {
            'color': bar_color if bar_color.startswith('#') else 'green',  # Usa a cor fornecida se válida, senão usa verde como padrão
            'current_value': 0,
            'max_value': 100,
            'label': bar_name,  # Adiciona o nome da barra como label
            'bar_frame': None,  # Inicialmente, o frame da barra é None
            'bar_label': None,
            'bar': None,
            'bar_value_label': None,
            'remove_bar_button': None
        }

        # Atualiza a exibição do jogador para mostrar a barra
        self.update_character_display()

    def add_combatant(self):
        name = simpledialog.askstring("Adicionar Combatente", "Nome:", parent=self.root)
        initiative = simpledialog.askinteger("Adicionar Combatente", "Iniciativa:", parent=self.root)
        if name and initiative is not None:
            self.combatant.append({"name": name, "initiative": initiative})
            self.combatant.sort(key=lambda x: x["initiative"], reverse=True)  # Ordena por iniciativa decrescente
            self.current_turn = 0  # Reinicia o turno para o primeiro combatente
            self.update_combatant_display()

    def update_combatant_display(self):
        # Limpa as labels antigas
        for label in self.combatant_labels:
            label.destroy()
        self.combatant_labels = []

        # Cria novas labels para os combatentes
        for i, combatant in enumerate(self.combatant):
            label = ctk.CTkLabel(self.combatant_names_frame, text=combatant["name"], font=("Helvetica", 8))  # Fonte menor
            if i == self.current_turn:
                label.configure(font=("Helvetica", 10, "bold")) 
            self.combatant_labels.append(label)
            label.pack(side=tk.LEFT, padx=5)

    def next_turn(self):
        if self.combatant:
            self.current_turn = (self.current_turn + 1) % len(self.combatant)
            self.update_combatant_display()

    def prev_turn(self):
        if self.combatant:
            self.current_turn = (self.current_turn - 1) % len(self.combatant)
            self.update_combatant_display()

    def reorder_combatant(self):
        if not self.combatant:
            return

        def move_up():
            if selected_index > 0:
                self.combatants[selected_index], self.combatants[selected_index - 1] = self.combatants[selected_index - 1], self.combatants[selected_index]
                self.current_turn = selected_index - 1
                update_listbox()
                self.update_combatant_display()
                listbox.selection_clear(0, tk.END)  # Limpa a seleção atual
                listbox.selection_set(self.current_turn)  # Seleciona o item movido

        def move_down():
            if selected_index < len(self.combatants) - 1:
                self.combatants[selected_index], self.combatants[selected_index + 1] = self.combatants[selected_index + 1], self.combatants[selected_index]
                self.current_turn = selected_index + 1
                update_listbox()
                self.update_combatant_display()
                listbox.selection_clear(0, tk.END)  # Limpa a seleção atual
                listbox.selection_set(self.current_turn)  # Seleciona o item movido

        def update_listbox():
            listbox.delete(0, tk.END)
            for combatant in self.combatant:
                listbox.insert(tk.END, combatant["name"])
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(self.current_turn)

        reorder_window = ctk.CTkToplevel(self.root)
        reorder_window.title("Reordenar Combatentes")
        reorder_window.configure(fg_color="#393D43")
        reorder_window.minsize(200, 200)

        listbox = tk.Listbox(reorder_window, bg="#2A2A33", fg="#C9B273")
        listbox.pack()
        update_listbox()

        button_frame = ctk.CTkFrame(reorder_window)
        button_frame.pack()

        up_button = ctk.CTkButton(button_frame, text="▲")
        up_button.configure(width=40, height=30, corner_radius=5, fg_color='#2A2A33', border_color=('#D3A62C'), 
                            hover_color='#1D1C21', text_color='#C9B273', font=('Helvetica', 12, 'bold'), command=move_up)
        up_button.pack(side=tk.LEFT, padx=5)

        down_button = ctk.CTkButton(button_frame, text="▼")
        down_button.configure(width=40, height=30, corner_radius=5, fg_color='#2A2A33', border_color=('#D3A62C'), 
                            hover_color='#1D1C21', text_color='#C9B273', font=('Helvetica', 12, 'bold'), command=move_down)
        down_button.pack(side=tk.LEFT, padx=5)  # Movido para dentro do button_frame
        
        def on_select(event):
            nonlocal selected_index
            selected_index = listbox.curselection()[0]

        listbox.bind("<<ListboxSelect>>", on_select)

        selected_index = self.current_turn  # Inicialmente seleciona o combatente atual

    def remove_combatant(self):
        if self.combatant:
            del self.combatant[self.current_turn]
            if self.current_turn >= len(self.combatant):
                self.current_turn = 0
            self.update_combatant_display()

    def remove_all_combatant(self):
        self.combatant = []
        self.current_turn = 0
        self.update_combatant_display()

    def create_npc(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Criar NPC")
        dialog.attributes('-topmost', 'true')  # Manter a janela no topo
        dialog.minsize(300, 200)  # Definir tamanho mínimo

        name_label = ctk.CTkLabel(dialog, text="Nome:")
        name_label.pack(pady=5)
        name_entry = ctk.CTkEntry(dialog)
        name_entry.pack(pady=5)

        max_hp_label = ctk.CTkLabel(dialog, text="HP Máximo:")
        max_hp_label.pack(pady=5)
        max_hp_entry = ctk.CTkEntry(dialog)
        max_hp_entry.pack(pady=5)

        def create_npc_confirm():
            name = name_entry.get()
            max_hp = max_hp_entry.get()

            if name and max_hp:
                try:
                    max_hp = int(max_hp)
                    if max_hp > 0:
                        npc = NPC(name, max_hp)
                        self.npcs.append(npc)
                        self.update_character_display()
                        dialog.destroy()
                    else:
                        messagebox.showerror("Error", "Maximum HP must be greater than zero")
                except ValueError:
                    messagebox.showerror("Error", "HP Máximo deve ser um número inteiro.")

        confirm_button = ctk.CTkButton(dialog, text="Criar", command=create_npc_confirm)
        confirm_button.pack(pady=10)

        # Centralizar a janela na tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = dialog.winfo_reqwidth()
        window_height = dialog.winfo_reqheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        dialog.geometry(f"+{x}+{y}")

    def delete_npc(self):
        if not self.npcs:
            messagebox.showinfo("Informação", "Nenhum NPC para deletar.")
            return

        delete_window = ctk.CTkToplevel(self.root)
        delete_window.title("Deletar NPC")
        delete_window.attributes('-topmost', 'true')  # Manter a janela no topo
        delete_window.minsize(300, 150)  # Definir tamanho mínimo

        npc_names = [npc.name for npc in self.npcs]
        npc_combobox = ctk.CTkComboBox(delete_window, values=npc_names)
        npc_combobox.pack(pady=10)

        def confirm_delete():
            selected_npc_name = npc_combobox.get()
            npc_to_delete = next((npc for npc in self.npcs if npc.name == selected_npc_name), None)
            if npc_to_delete:
                self.npcs.remove(npc_to_delete)
                self.update_character_display()
                delete_window.destroy()
            else:
                messagebox.showerror("Erro", "NPC não encontrado.")

        delete_button = ctk.CTkButton(delete_window, text="Deletar", command=confirm_delete)
        delete_button.pack(pady=10)

        # Centralizar a janela na tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = delete_window.winfo_reqwidth()
        window_height = delete_window.winfo_reqheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        delete_window.geometry(f"+{x}+{y}")

    def edit_exhaustion(self):
        exhaustion_value = tk.simpledialog.askinteger("Editar Exaustão", "Insira um valor de 0 a 100:", parent=self.root, minvalue=0, maxvalue=100)
        if exhaustion_value is not None:
            self.exhaustion_value = exhaustion_value
            self.update_exhaustion_display()

    def update_exhaustion_display(self):
            normalized_value = self.exhaustion_value / 100
            self.exhaustion_bar.set(normalized_value)
            self.exhaustion_value_label.configure(text=str(self.exhaustion_value))
        
    def create_player(self):
        self.create_character(self.players)

    def create_character(self, collection):
        dialog = tk.Toplevel(self.root)
        dialog.lift()

        name = simpledialog.askstring("Input", "Enter character name:", parent=dialog)
        max_hp = simpledialog.askinteger("Input", "Enter maximum HP:", parent=dialog)
        max_mp = simpledialog.askinteger("Input", "Enter maximum MP:", parent=dialog)

        dialog.destroy()

        if name and max_hp and max_mp and max_hp > 0 and max_mp > 0:
            character = Character(name, max_hp, max_mp, max_hp, max_mp)
            if isinstance(collection, list):
                collection.append(character)
            else:
                collection[name] = character
            self.update_character_display()
        else:
            messagebox.showerror("Error", "Maximum HP and MP must be greater than zero")

    def update_character_display(self):
        # Limpa os widgets antigos antes de criar os novos
        for widget in self.character_frame.winfo_children():
            widget.destroy()

        # Cria os widgets atualizados para cada personagem
        for player in self.players:
            self.create_character_widget(player, self.character_frame)

        npcs_per_row = 5  # Número máximo de NPCs por linha
        current_row_count = 0  # Contador de NPCs na linha atual
        current_row_frame = None  # Frame da linha atual

        for npc in self.npcs:
            self.create_npc_widget(npc, self.npc_frame)  # Use o self.npc_frame, que agora está dentro do canvas

            self.create_npc_widget(npc, current_row_frame)
            current_row_count += 1

            if current_row_count == npcs_per_row:
                # Reinicia o contador e o frame da linha quando atingir o limite
                current_row_count = 0
                current_row_frame = None

            # Limpa o frame de ícones de DoT 
            for widget in npc.dot_icons_frame.winfo_children():
                widget.destroy()

            # Atualiza as opções do combobox de alvo para DoT
            all_characters = self.players + self.npcs
            target_names = [character.name for character in all_characters]
            self.dot_target_combobox.configure(values=target_names)

            # Limpa o frame de ícones de DoT 
            for widget in npc.dot_icons_frame.winfo_children():
                widget.destroy()

            # Verifica se o frame de ícones de DoT existe
            if hasattr(npc, 'dot_icons_frame') and npc.dot_icons_frame:
                # Limpa o frame de ícones de DoT 
                for widget in npc.dot_icons_frame.winfo_children():
                    widget.destroy()

                # Cria ícones para os DoTs
                for buff_debuff_name, buff_debuff_data in npc.temp_buffs_debuffs.items():
                    if "dot_amount" in buff_debuff_data:
                        dot_amount = buff_debuff_data["dot_amount"]
                        remaining_time = buff_debuff_data['remaining_duration']

                        # Escolhe o ícone e a cor com base no tipo de DoT (dano ou cura)
                        dot_icon = blood_icon if dot_amount < 0 else dot_heal_icon
                        dot_color = "red" if dot_amount < 0 else "#167d14"

                        # Cria um frame para cada ícone e seu label de informação
                        dot_info_frame = ctk.CTkFrame(npc.dot_icons_frame, fg_color="transparent")
                        dot_info_frame.pack(side=tk.LEFT, padx=2)  # Empacota horizontalmente com espaçamento

                        # Cria o ícone com tooltip dentro do novo frame
                        icon_label = ctk.CTkLabel(dot_info_frame, image=dot_icon, text="", width=20, height=20, fg_color="transparent")
                        icon_label.pack(side=tk.LEFT)

                        # Armazena o nome do buff/debuff e o personagem na lambda function
                        icon_label.bind("<Button-1>", lambda event, c=npc, bn=buff_debuff_name: self.remove_buff_debuff(c, bn))

                        # Cria um label para exibir valor e turnos ao lado do ícone, também dentro do novo frame
                        dot_info_label = ctk.CTkLabel(dot_info_frame, text=f"{abs(dot_amount)} ({remaining_time})", 
                                                    text_color=dot_color,
                                                    font=('Helvetica', 10))
                        dot_info_label.pack(side=tk.LEFT)

                        # Tooltip com o nome do DoT
                        Hovertip(icon_label, buff_debuff_name, hover_delay=300) # SOCORROOOOOOOOOOOOOOOOOOOOOOOOOOO

        # Loop para Players - manipulação de buffs/debuffs 
        for player in self.players:
            buff_debuff_count = 1
            for buff_debuff_name, buff_debuff_data in player.temp_buffs_debuffs.items():
                if hasattr(player, 'buffs_debuffs_frame'):
                    buffs_debuffs_frame = player.buffs_debuffs_frame

                    # Cria um frame para cada buff/debuff com padding interno
                    inner_frame = ctk.CTkFrame(buffs_debuffs_frame, fg_color='#282a36', corner_radius=10)
                    inner_frame.pack(padx=3, pady=0, fill='x') 

                    if buff_debuff_data['type'] == 'dot':
                        # Lógica para exibir DoTs 
                        dot_color = "gray50" if buff_debuff_data["dot_amount"] < 0 else "darkgreen"

                        # Usa o formatted_text definido em add_temp_buff_debuff
                        label_text = buff_debuff_data['formatted_text']

                        # Label com o nome do DoT, formatação customizada e cor
                        dot_label = ctk.CTkLabel(inner_frame, text=label_text, font=('Helvetica', 11), text_color=dot_color, fg_color='#282a36', height=10, corner_radius=0, padx=0, pady=2)
                        dot_label.pack(side=tk.LEFT)

                        # Botão para remover o DoT
                        remove_dot_button = ctk.CTkButton(inner_frame, text="x", command=lambda buff_name=buff_debuff_name: self.remove_buff_debuff(player, buff_name), font=("Helvetica", 8), width=0, height=0, fg_color='transparent', corner_radius=5)
                        remove_dot_button.pack(side=tk.RIGHT, padx=1, pady=0)

                    else:  # Buffs/Debuffs regulares
                        # Lógica para exibir buffs/debuffs regulares
                        remaining_time = buff_debuff_data['remaining_duration']
                        label_text = f"{buff_debuff_count}. {buff_debuff_name} (CD: {remaining_time})" # NÃO
                        dot_color = 'white' 
                        buff_debuff_count += 1 

                        # Label com o nome do buff/debuff
                        buff_debuff_name_label = ctk.CTkLabel(inner_frame,
                                                              text=label_text,
                                                              font=('Helvetica', 11),
                                                              text_color=dot_color,
                                                              fg_color='#282a36',
                                                              height=10,
                                                              corner_radius=0,
                                                              padx=0, pady=2)
                        buff_debuff_name_label.pack(side=tk.LEFT)

                        # Label da duração (apenas para buffs/debuffs regulares)
                        if "dot_amount" not in buff_debuff_data:
                            buff_debuff_duration_label = ctk.CTkLabel(inner_frame,
                                                                      text=f"  (CD: {remaining_time} turnos)",
                                                                      font=('Helvetica', 11, 'bold'),
                                                                      text_color=('black', 'white'),
                                                                      fg_color='#282a36',
                                                                      height=10,
                                                                      corner_radius=0,
                                                                      padx=0, pady=2)
                            buff_debuff_duration_label.pack(side=tk.LEFT)

                        # Botão para remover buff/debuff/DoT
                        remove_buff_debuff_button = ctk.CTkButton(inner_frame,
                                                                  text="x",
                                                                  command=lambda buff_name=buff_debuff_name: self.remove_buff_debuff(player, buff_name),
                                                                  font=("Helvetica", 8),
                                                                  width=0,
                                                                  height=0,
                                                                  fg_color='transparent',
                                                                  corner_radius=5)
                        remove_buff_debuff_button.pack(side=tk.RIGHT, padx=1, pady=0)
                    # Get the 'type', defaulting to 'buff_debuff' if not present
                    buff_type = buff_debuff_data.get('type', 'buff_debuff')

                    if buff_type == 'dot':
                        # Lógica para exibir DoTs 
                        dot_color = "gray50" if buff_debuff_data["dot_amount"] < 0 else "darkgreen"

                        # Usa o formatted_text definido em add_temp_buff_debuff
                        label_text = buff_debuff_data['formatted_text']

                        # Cria um frame para cada DoT com padding interno
                        dot_frame = ctk.CTkFrame(buffs_debuffs_frame, fg_color='#282a36', corner_radius=10)
                        dot_frame.pack(anchor=tk.W, padx=5, pady=0, fill='x') 

                        # Frame interno para adicionar padding extra ao redor da label
                        inner_frame = ctk.CTkFrame(dot_frame, fg_color='#282a36', corner_radius=10)
                        inner_frame.pack(padx=3, pady=0, fill='x') 

                        # Label com o nome do DoT, formatação customizada e cor
                        dot_label = ctk.CTkLabel(inner_frame, text=label_text, font=('Helvetica', 11), text_color=dot_color, fg_color='#282a36', height=10, corner_radius=0, padx=0, pady=2)
                        dot_label.pack(side=tk.LEFT)

                        # Botão para remover o DoT
                        remove_dot_button = ctk.CTkButton(inner_frame, text="x", command=lambda buff_name=buff_debuff_name: self.remove_buff_debuff(player, buff_name), font=("Helvetica", 8), width=0, height=0, fg_color='transparent', corner_radius=5)
                        remove_dot_button.pack(side=tk.RIGHT, padx=1, pady=0)

                    else:  # Buffs/Debuffs regulares
                        # Lógica para exibir buffs/debuffs regulares
                        remaining_time = buff_debuff_data['remaining_duration']
                        label_text = f"{buff_debuff_count}. {buff_debuff_name} (CD: {remaining_time})"
                        dot_color = 'white' 
                        buff_debuff_count += 1 

                        # Frame interno para adicionar padding extra ao redor da label
                        inner_frame = ctk.CTkFrame(buffs_debuffs_frame, fg_color='#282a36', corner_radius=10)
                        inner_frame.pack(padx=3, pady=0, fill='x') 
                    # Label da duração (apenas para buffs/debuffs regulares)
                    if "dot_amount" not in buff_debuff_data:
                        buff_debuff_duration_label = ctk.CTkLabel(inner_frame,
                                                                  text=f"  (CD: {remaining_time} turnos)",
                                                                  font=('Helvetica', 11, 'bold'),
                                                                  text_color=('black', 'white'),
                                                                  fg_color='#282a36',
                                                                  height=10,
                                                                  corner_radius=0,
                                                                  padx=0, pady=2)
                        buff_debuff_duration_label.pack(side=tk.LEFT)

                        # Botão para remover buff/debuff/DoT
                        remove_buff_debuff_button = ctk.CTkButton(inner_frame,
                                                                text="x",
                                                                command=lambda buff_name=buff_debuff_name: self.remove_buff_debuff(player, buff_name),
                                                                font=("Helvetica", 8),
                                                                width=0,
                                                                height=0,
                                                                fg_color='transparent',
                                                                corner_radius=5)
                        remove_buff_debuff_button.pack(side=tk.RIGHT, padx=1, pady=0)

                    buff_debuff_count += 1  # Incrementa o contador apenas para buffs/debuffs regulares

    def create_npc_widget(self, npc, parent):
        # Criar um CTkFrame para o widget do NPC
        frame = ctk.CTkFrame(parent, border_width=2, fg_color='#393D43', border_color="#D3A62C")
        frame.pack(fill=tk.X, pady=2, padx=2)  # Removendo side=tk.LEFT para preencher horizontalmente

        info_frame = ctk.CTkFrame(frame, fg_color='#393D43')
        info_frame.pack(fill=tk.X, padx=5, pady=5)  # Reduzindo o padding para algo mais compacto

        # Definindo a altura mínima do frame
        info_frame.configure(height=100)

        name_label = ctk.CTkLabel(info_frame, text=npc.name, text_color=npc.hp_color, font=('Helvetica', 13, 'bold'))
        name_label.pack()

        hp_frame = ctk.CTkFrame(info_frame, fg_color='#393D43')
        hp_frame.pack(side=ctk.TOP)

        hp_label = ctk.CTkLabel(master=hp_frame, text=f" {npc.hp}/{npc.max_hp} ")
        hp_label.pack(side=ctk.LEFT)
        npc.hp_label = hp_label  # Assign the label to the NPC object

        hp_bar = ctk.CTkProgressBar(hp_frame, width=165, height=10, border_width=2, corner_radius=15, progress_color=npc.hp_color, fg_color="#787878")
        hp_bar.set(npc.hp / npc.max_hp if npc.max_hp > 0 else 0)
        hp_bar.pack(side=tk.LEFT)
        npc.hp_bar = hp_bar   # Assign the bar to the NPC object

        damage_icon = CTkImage(light_image=damage_icon_path, size=(20, 20))
        dmg_hp_button = CTkButton(hp_frame, image=damage_icon, command=lambda: self.modify_character(npc, "hp"), text="", width=5, height=5, fg_color="#393D43", hover_color='#5C0F0F')
        dmg_hp_button.pack(side=tk.LEFT)

        healing_icon = CTkImage(light_image=healing_icon_path, size=(20, 20))
        heal_hp_button = CTkButton(hp_frame, image=healing_icon, command=lambda: self.modify_character(npc, "heal"), text="", width=5, height=5, fg_color="#393D43", hover_color='#0E5310')
        heal_hp_button.pack(side=tk.LEFT)

        alter_hp_icon = CTkImage(light_image=alter_hp_path, size=(15, 15))
        alter_hp_max_button = CTkButton(hp_frame, image=alter_hp_icon, command=lambda: self.modify_character(npc, "increase_max_hp"), text="", width=5, height=5, fg_color="#393D43", hover_color='#2B2E32')
        alter_hp_max_button.pack(side=tk.LEFT)

        def change_hp_color():
            color = color_combobox.get()
            color_map = {
                "Branco": "white",
                "Laranja": "orange",
                "Vermelho": "#FF0027",
                "Preto": "#1A1A1A"
            }
            npc.hp_color = color_map.get(color, "white")
            hp_bar.configure(progress_color=npc.hp_color)
            name_label.configure(text_color=npc.hp_color)  # Muda a cor do texto do nome

        combo_frame = ctk.CTkFrame(info_frame)
        combo_frame.pack(side=ctk.TOP, pady=5)

        color_combobox = ctk.CTkComboBox(combo_frame, values=["Branco", "Laranja", "Vermelho", "Preto"],
                                        width=100,
                                        height=20,
                                        fg_color=('#2A2A33'),
                                        border_color=('#D3A62C'),
                                        text_color=('#C9B273'),
                                        dropdown_fg_color=('#2A2A33'),
                                        dropdown_hover_color=('#1D1C21'),
                                        dropdown_text_color=('#C9B273'),
                                        button_color=('#616161'),
                                        button_hover_color=('#181823'),
                                        border_width=1,
                                        font=('Helvetica', 11))
        color_combobox.set("Branco")  # Definir valor padrão
        color_combobox.pack(side=tk.LEFT)

        change_color_button = ctk.CTkButton(combo_frame, text="Rank", command=change_hp_color,
                                            width=50,
                                            height=10,
                                            fg_color=('grey25'),
                                            border_color=('#D3A62C'),
                                            corner_radius=0,
                                            border_width=1,  
                                            hover_color=('black'),
                                            text_color=('white'), 
                                            font=('Helvetica', 12)) 
        change_color_button.pack(side=tk.LEFT, padx=10)

        # Frame to hold the Spinbox (for size control)
        spinbox_container = ctk.CTkFrame(combo_frame, width=70, height=20)
        spinbox_container.pack(side=tk.RIGHT)
        spinbox_container.pack_propagate(0)

        # Create the Spinbox inside the container
        spinbox = CTkSpinbox(spinbox_container,
                            text_color='#C9B273', button_color='#616161', button_hover_color='#181823',
                            font=ctk.CTkFont(size=12))  # Set font size to 12
        spinbox.pack(fill=tk.BOTH, expand=True)
        # Armazena o spinbox no objeto NPC
        npc.spinbox = spinbox
        # Define a função on_spinbox_change e armazena no objeto NPC
        def on_spinbox_change(new_value):
            npc.spinbox_value = new_value
        npc.on_spinbox_change = on_spinbox_change
        # Configura o comando do spinbox
        spinbox.configure(command=npc.on_spinbox_change)

        # Frame para ícones de DoT (com altura máxima)
        dot_icons_frame = ctk.CTkFrame(info_frame, fg_color='#393D43')
        dot_icons_frame.pack(side=tk.TOP, anchor=tk.W)  # Alinha à esquerda
        dot_icons_frame.configure(height=25)  # Defina uma altura máxima adequada

        # Armazena o frame no objeto NPC para acesso posterior
        npc.dot_icons_frame = dot_icons_frame 

    def apply_dot(self):
        # Obtém o personagem selecionado
        selected_character = self.get_selected_character()
        if selected_character is None:
            ctkmessagebox(title="Erro", message="Nenhum personagem selecionado.", icon="warning")
            return

        # Cria a janela de diálogo para inserir os detalhes do DoT
        dot_window = ctk.CTkToplevel(self.root)
        dot_window.title("Aplicar DoT")
        dot_window.attributes('-topmost', True)
        dot_window.geometry("280x280")  # Tamanho da janela

        # Use o combobox dedicado para seleção de alvo
        self.target_combobox = self.dot_target_combobox 
        self.target_combobox.pack()

        # Widgets para inserir os dados do DoT
        ctk.CTkLabel(dot_window, text="Nome do DoT:").pack(pady=5)
        dot_name_entry = ctk.CTkEntry(dot_window)
        dot_name_entry.pack()

        ctk.CTkLabel(dot_window, text="Duração (turnos):").pack(pady=5)
        dot_duration_entry = ctk.CTkEntry(dot_window)
        dot_duration_entry.pack()

        ctk.CTkLabel(dot_window, text="Quantidade por Turno:").pack(pady=5)  # Texto alterado
        dot_amount_entry = ctk.CTkEntry(dot_window)
        dot_amount_entry.pack()

        # Botões para Dano e Cura
        damage_button = ctk.CTkButton(dot_window, text="Dano", 
                                      command=lambda: self.confirm_dot(dot_window, dot_name_entry, dot_duration_entry, dot_amount_entry, is_damage=True))
        damage_button.pack(pady=5)

        heal_button = ctk.CTkButton(dot_window, text="Cura", 
                                    command=lambda: self.confirm_dot(dot_window, dot_name_entry, dot_duration_entry, dot_amount_entry, is_damage=False))
        heal_button.pack(pady=5)

    def confirm_dot(self, dot_window, dot_name_entry, dot_duration_entry, dot_amount_entry, is_damage=True):
        dot_name = dot_name_entry.get()
        dot_duration = int(dot_duration_entry.get())
        # Ajusta o valor de dot_amount_per_turn com base em is_damage
        dot_amount_per_turn = int(dot_amount_entry.get())
        if is_damage:
            dot_amount_per_turn = -dot_amount_per_turn  # Dano é negativo

        # Obtém o personagem selecionado (novamente, pois a seleção pode ter mudado)
        selected_character = self.get_selected_character()
        if selected_character is None:
            ctkmessagebox(title="Erro", message="Nenhum personagem selecionado.", icon="warning")
            return
        if isinstance(selected_character, NPC):
            selected_character.add_temp_buff_debuff(dot_name, dot_duration, dot_amount=dot_amount_per_turn)
        else:
            # Handle the case where selected_character is not an NPC
            print("Error: Cannot apply DoT to a non-NPC character.")  # Or display a message to the user

        # Adiciona o DoT à lista temp_buffs_debuffs do personagem selecionado
        selected_character.add_temp_buff_debuff(dot_name, dot_duration, dot_amount=dot_amount_per_turn)
        selected_player_name = self.target_combobox.get()  # Use target_combobox
        # Fecha a janela de diálogo
        dot_window.destroy()
        self.update_character_display()

    def aplicar_dano_por_turno(self):
        for character in self.players + self.npcs:  # Itera sobre todos os personagens
            dots_to_remove = []  # Lista para armazenar os DoTs a serem removidos
            for buff_debuff_name, buff_debuff_data in list(character.temp_buffs_debuffs.items()):  # Iterate over a copy of the keys
                if "dot_amount" in buff_debuff_data:
                    dot_amount = buff_debuff_data["dot_amount"]
                    if dot_amount > 0:  # Cura
                        character.hp = min(character.hp + dot_amount, character.max_hp)
                    else:  # Dano
                        character.hp = max(0, character.hp + dot_amount)
                    print(f"{character.name} {'recebeu' if dot_amount < 0 else 'recuperou'} {abs(dot_amount)} de vida por turno de {buff_debuff_name}.")

                    # Decrementa a duração restante do DoT
                    buff_debuff_data['remaining_duration'] -= 0

                    # Atualiza o label de HP e a barra de HP diretamente
                    if character.hp_label is not None and character.hp_bar is not None:
                        character.hp_label.configure(text=f" {character.hp}/{character.max_hp} ")
                        character.hp_bar.set(character.hp / character.max_hp if character.max_hp > 0 else 0)
                    else:
                        print(f"Error: hp_label or hp_bar is None for character {character.name}")

                    # Verifica se o DoT expirou e remove se necessário
                    if buff_debuff_data['remaining_duration'] <= 0:
                        dots_to_remove.append(buff_debuff_name)

            # Remove os DoTs expirados (fora do loop interno)
            for dot_name in dots_to_remove:
                del character.temp_buffs_debuffs[dot_name]

    def modify_character(self, character, action):
        if action == "hp":
            damage = simpledialog.askinteger("Input", "Quanto de dano?", parent=self.root)
            if damage:
                character.hp = max(character.hp - damage, 0)
                # Atualiza o label de HP e a barra de HP diretamente
                character.hp_label.configure(text=f" {character.hp}/{character.max_hp} ")
                character.hp_bar.set(character.hp / character.max_hp if character.max_hp > 0 else 0)
        elif action == "heal":
            heal = simpledialog.askinteger("Input", "Quanto curar?", parent=self.root)
            if heal:
                character.hp = min(character.hp + heal, character.max_hp)
                # Atualiza o label de HP e a barra de HP diretamente
                character.hp_label.configure(text=f" {character.hp}/{character.max_hp} ")
                character.hp_bar.set(character.hp / character.max_hp if character.max_hp > 0 else 0)
        elif action == "increase_max_hp":
            new_max_hp = simpledialog.askinteger("Input", "Novo HP Max:", parent=self.root)
            if new_max_hp and new_max_hp > 0:
                character.max_hp = new_max_hp
                if character.hp > new_max_hp:
                    character.hp = new_max_hp
                # Atualiza o label de HP e a barra de HP diretamente
                character.hp_label.configure(text=f" {character.hp}/{character.max_hp} ")
                character.hp_bar.set(character.hp / character.max_hp if character.max_hp > 0 else 0)
        elif action == "increase_max_mp":
            new_max_mp = simpledialog.askinteger("Input", "Novo MP Max:", parent=self.root)
            if new_max_mp and new_max_mp > 0:
                character.max_mp = new_max_mp
                if character.mp > new_max_mp:
                    character.mp = new_max_mp
                # Atualiza o label de MP e a barra de MP diretamente
                character.mp_label.configure(text=f" {character.mp}/{character.max_mp} ")
                character.mp_bar.set(character.mp / character.max_mp if character.max_mp > 0 else 0)

    def delete_skill(self, character, name):
        skill = character.skills.get(name)
        if skill:
            del character.skills[name]
            messagebox.showinfo("Success", f"Habilidade '{name}' removida com sucesso!")
            self.update_character_display()  # Supondo que você tenha este método definido
            return True
        else:
            messagebox.showerror("Erro", "Habilidade inexistente.")
            return False

    def create_character_widget(self, character, parent):
        # Criar um CTkFrame para o widget do personagem
        frame = ctk.CTkFrame(parent, border_width=2, fg_color='#393D43', border_color="#D3A62C")  # Substitua '#FFFFFF' pela cor desejada em hexadecimal
        frame.pack(fill=ctk.X, pady=2)

        # Colorindo o segundo frame
        info_frame = ctk.CTkFrame(frame, fg_color='#393D43', border_width=0, border_color=None)
        info_frame.pack(side=ctk.LEFT, padx=10, pady=10)

        # Definindo a altura mínima do frame
        info_frame.configure(height=100)  # Ajuste o valor de 100 conforme necessário

        name_label = ctk.CTkLabel(info_frame, text=character.name, text_color="#DFA646", font=('Helvetica', 13, 'bold'))
        name_label.pack()  # Colorir

        hp_frame = ctk.CTkFrame(info_frame, fg_color='#393D43')  # Substitua '#0000FF' pela cor desejada em hexadecimal
        hp_frame.pack(side=ctk.TOP)

        hp_label = ctk.CTkLabel(master=hp_frame, text=f" {character.hp}/{character.max_hp} ", image=hp_icon, compound=ctk.LEFT)
        hp_label.pack(side=ctk.LEFT)
        character.hp_label = hp_label  # Assign the label to the character object

        # Criação da barra de progresso
        if isinstance(character, NPC):  # Verifica se o personagem é um NPC
            hp_bar = ctk.CTkProgressBar(hp_frame, width=225, height=15, border_width=2, corner_radius=10, progress_color='white', fg_color="#787878")
        else:
            hp_bar = ctk.CTkProgressBar(hp_frame, width=200, height=15, border_width=1, corner_radius=10, progress_color='#76BE1B', fg_color="#787878")

        # Configurando o valor da barra de progresso
        hp_bar.set(character.hp / character.max_hp if character.max_hp > 0 else 0)
        hp_bar.pack(side=tk.LEFT)
        character.hp_bar = hp_bar   # Assign the bar to the character object

        damage_icon = CTkImage(light_image=damage_icon_path, size=(20, 20))
        dmg_hp_button = CTkButton(hp_frame, image=damage_icon, command=lambda: self.modify_character(character, "hp"), text="", width=5, height=5, fg_color="#393D43", hover_color='#5C0F0F')
        dmg_hp_button.pack(side=tk.LEFT)

        healing_icon = CTkImage(light_image=healing_icon_path, size=(20, 20))
        heal_hp_button = CTkButton(hp_frame, image=healing_icon, command=lambda: self.modify_character(character, "heal"), text="", width=5, height=5, fg_color="#393D43", hover_color='#0E5310')
        heal_hp_button.pack(side=tk.LEFT)

        alter_hp_icon = CTkImage(light_image=alter_hp_path, size=(15, 15))
        alter_hp_max_button = CTkButton(hp_frame, image=alter_hp_icon, command=lambda: self.modify_character(character, "increase_max_hp"), text="", width=5, height=5, fg_color="#393D43", hover_color='#2B2E32')
        alter_hp_max_button.pack(side=tk.LEFT)

        character.hp_label = hp_label
        character.hp_bar = hp_bar
 
        if hasattr(character, 'mp'):
            mana_icon = ctk.CTkImage(light_image=mana_icon_image, size=(15, 15))
            mp_frame = ctk.CTkFrame(info_frame, fg_color='#393D43')  # Frame para MP
            mp_frame.pack(side=ctk.TOP)

            mp_label = ctk.CTkLabel(master=mp_frame, text=f" {character.mp}/{character.max_mp} ", image=mana_icon, compound=ctk.LEFT)
            mp_label.pack(side=ctk.LEFT)
            character.mp_label = mp_label  # Armazena o label de MP

            # Configurando a barra de progresso de MP
            mp_bar = ctk.CTkProgressBar(mp_frame, width=170, height=10, border_width=1, corner_radius=10, progress_color='#1192E5', fg_color="#787878")
            mp_bar.set(character.mp / character.max_mp if character.max_mp > 0 else 0)
            mp_bar.pack(side=tk.LEFT)

            modify_mana_button = ctk.CTkButton(mp_frame, image=mana_useorheal_icon, text="", width=10, height=10, fg_color="#393D43", hover_color='#266A96', command=lambda c=character: self.open_mana_window(c))
            modify_mana_button.pack(side=ctk.LEFT, padx=2)

            alter_mp_max_button = ctk.CTkButton(mp_frame,
                                                text="Editar MP", width=50, height=10, fg_color=('#2D2D51'), border_color=('#196EA5'), corner_radius=0, border_width=2, hover_color=('#266A96'), text_color=('#C9B273'),
                                                font=('Helvetica', 12), command=lambda: self.modify_character(character, "increase_max_mp")            )
            alter_mp_max_button.pack(side=tk.LEFT)

            if hasattr(character, 'mp'):
                character.mp_label = mp_label
                character.mp_bar = mp_bar

        # Exibe a barra se o jogador tiver dados de barra
        if not isinstance(character, NPC) and hasattr(character, 'bar_data'):
            for bar_name, bar_data in character.bar_data.items():
                # Verifica se o frame da barra já existe na interface
                bar_frame = character.bar_widgets.get(bar_name, {}).get('bar_frame')
                if bar_frame and bar_frame.winfo_exists():  # Verifica se o frame existe e não foi destruído
                    # Se o frame existir, atualize os widgets existentes
                    bar = character.bar_widgets[bar_name]['bar']
                    bar_value_label = character.bar_widgets[bar_name]['bar_value_label']

                    bar.set(bar_data['current_value'] / bar_data['max_value'])
                    bar_value_label.configure(text=f"{bar_data['current_value']}/{bar_data['max_value']}")
                else:
                    # Se o frame não existir, crie-o e armazene a referência em bar_data
                    bar_frame = ctk.CTkFrame(info_frame, fg_color='#393D43')
                    bar_frame.pack(side=tk.TOP, pady=(5, 0), anchor="e")  # Ancora à direita
                    bar_data['bar_frame'] = bar_frame  # Armazena a referência em bar_data

                    bar_data['bar_label'] = ctk.CTkLabel(bar_frame, text=f"{bar_name}: ")
                    bar_data['bar_label'].pack(side=tk.LEFT)

                    bar_data['bar'] = ctk.CTkProgressBar(bar_frame, width=150, height=10, 
                                                        progress_color=bar_data['color'], fg_color="#787878")
                    bar_data['bar'].set(bar_data['current_value'] / bar_data['max_value'])
                    bar_data['bar'].pack(side=tk.LEFT, padx=5)

                    bar_data['bar_value_label'] = ctk.CTkLabel(bar_frame, 
                                                            text=f"{bar_data['current_value']}/{bar_data['max_value']}")
                    bar_data['bar_value_label'].pack(side=tk.LEFT)

                    # Armazena os widgets da barra no dicionário bar_widgets
                    character.bar_widgets[bar_name] = {
                        'bar_frame': bar_frame,
                        'bar': bar_data['bar'],
                        'bar_value_label': bar_data['bar_value_label']
                    }
                    
                    # Botões da barra
                    bar_buttons_frame = ctk.CTkFrame(bar_data['bar_frame'], fg_color='#393D43')
                    bar_buttons_frame.pack(side=tk.LEFT, padx=5)  # Adiciona um pequeno espaçamento à esquerda dos botões

                    # Botão "Adicionar Valor"
                    add_value_button = ctk.CTkButton(bar_buttons_frame,
                                                    text="+",
                                                    command=lambda bn=bar_name: self.modify_bar_value(character, "add", bn),
                                                    width=25,
                                                    height=10,
                                                    fg_color='#2A2A33',
                                                    border_color='#D3A62C',
                                                    corner_radius=0,
                                                    border_width=1,
                                                    hover_color='#1D1C21',
                                                    text_color='#C9B273',
                                                    font=('Helvetica', 10))
                    add_value_button.pack(side=tk.LEFT, padx=2)

                    # Botão "Remover Valor"
                    remove_value_button = ctk.CTkButton(bar_buttons_frame,
                                                        text="-",
                                                        command=lambda bn=bar_name: self.modify_bar_value(character, "remove", bn),
                                                        width=25,
                                                        height=10,
                                                        fg_color='#2A2A33',
                                                        border_color='#D3A62C',
                                                        corner_radius=0,
                                                        border_width=1,
                                                        hover_color='#1D1C21',
                                                        text_color='#C9B273',
                                                        font=('Helvetica', 10))
                    remove_value_button.pack(side=tk.LEFT, padx=2)

                    # Botão "Alterar Total"
                    alter_total_button = ctk.CTkButton(bar_buttons_frame,
                                                    text="Set",
                                                    command=lambda bn=bar_name: self.modify_bar_value(character, "alter_total", bn),
                                                    width=35,
                                                    height=10,
                                                    fg_color='#2A2A33',
                                                    border_color='#D3A62C',
                                                    corner_radius=0,
                                                    border_width=1,
                                                    hover_color='#1D1C21',
                                                    text_color='#C9B273',
                                                    font=('Helvetica', 10))
                    alter_total_button.pack(side=tk.LEFT, padx=2)

                    # Botão para remover a barra (discreto e à direita)
                    remove_bar_button = ctk.CTkButton(bar_data['bar_frame'], 
                                                    text="x", 
                                                    command=lambda bn=bar_name: self.remove_bar_from_player(character, bn),
                                                    width=15, 
                                                    height=10,
                                                    fg_color=('gray75', 'gray25'),  # Cor mais discreta
                                                    hover_color=('gray50', 'gray10'),
                                                    text_color=('black', 'white'),
                                                    font=('Helvetica', 8, 'bold'))  # Fonte menor e em negrito
                    remove_bar_button.pack(side=tk.RIGHT)  # Posiciona à direita
                    
        # Loja e Gold
        gold_frame = ctk.CTkFrame(info_frame, fg_color='#393D43')
        gold_frame.pack(side=tk.TOP, pady=5) # Continuar

        edit_gold_button = ctk.CTkButton(master=gold_frame,
                                        text="Add $",  # Texto alterado para "Add $"
                                        command=lambda: self.edit_gold(character),
                                        height=25,
                                        width=50,
                                        fg_color=('#2A2A33'),  
                                        border_color=('#D3A62C'), 
                                        corner_radius=0,
                                        border_width=2,  # Largura da borda
                                        hover_color=('#1D1C21'),
                                        text_color=('#C9B273'),  # Cor do texto
                                        font=('Helvetica', 12))  # Fonte Helvetica tamanho 12
        edit_gold_button.pack(side=tk.LEFT, padx=2, anchor=tk.W)

        gold_label = ctk.CTkLabel(master=gold_frame,
                                text=f"Gold: ${character.player_gold}",
                                fg_color=('#2A2A33'),  # Fundo escuro padrão
                                text_color=('#C9B273'),  # Cor do texto
                                font=('Helvetica', 11, 'bold'),
                                corner_radius=10)  # Fonte Helvetica tamanho 12
        gold_label.pack(side=tk.LEFT, padx=2, anchor=tk.W)  # Utilize anchor=tk.W para alinhar à esquerda

        shop_combobox = ctk.CTkComboBox(master=gold_frame,
                                        values=["Poção Cura P. 25% HP - 350 Gold", 
                                                "Poção Cura M. 50% HP - 700 Gold", 
                                                "Poção Cura G. 100% HP - 1400 Gold", 
                                                "————————————————",
                                                "Poção Mana P. 25% MP - 500 Gold", 
                                                "Poção Mana M. 50% MP - 1000 Gold", 
                                                "Poção Mana G. 100% MP - 2000 Gold"],
                                        width=200,
                                        height=20,
                                        fg_color=('#2A2A33'),
                                        border_color=('#D3A62C'),
                                        text_color=('#C9B273'),
                                        dropdown_fg_color=('#2A2A33'),
                                        dropdown_hover_color=('#1D1C21'),
                                        dropdown_text_color=('#C9B273'),
                                        button_color=('#616161'),
                                        button_hover_color=('#181823'),
                                        border_width=1,
                                        font=('Helvetica', 11),
                                        dropdown_font=('Helvetica', 11))  # Aqui você pode usar 'system' para a fonte padrão do sistema
        shop_combobox.pack(side=tk.LEFT, padx=2, anchor=tk.W)

        buy_button = ctk.CTkButton(master=gold_frame,
                                text="Buy $",  # Texto do botão
                                command=lambda: self.buy_item(character, shop_combobox),
                                height=25,
                                width=50,
                                fg_color=('#2A2A33'),
                                border_color=('#D3A62C'), 
                                corner_radius=0,
                                border_width=2,  # Largura da borda
                                hover_color=('#302881'),
                                text_color=('#C9B273'),  # Cor do texto
                                font=('Helvetica', 12))  # Fonte Helvetica tamanho 12
        buy_button.pack(side=tk.LEFT, padx=2, anchor=tk.W)  # Posicionamento do botão        # Fim da loja

        delete_button = ctk.CTkButton(frame,
                                    text="X",
                                    command=lambda: self.delete_character(character),
                                    width=25,
                                    height=10,
                                    fg_color=('#2A2A33'),
                                    border_color=('#D3A62C'),
                                    corner_radius=0,
                                    border_width=1,
                                    hover_color=('#520C0A'),
                                    text_color=('#C9B273'),
                                    font=('Helvetica', 12))
        delete_button.pack(side=ctk.LEFT, padx=10, pady=10)  # Adjust padx and pady as needed for desired spacing

        skill_frame = ctk.CTkFrame(frame, fg_color="#393D43")  # Frame para usar Habilidades
        skill_frame.pack(side=tk.LEFT, padx=10)

        skill_label = ctk.CTkLabel(skill_frame, text="Habilidades:")
        skill_label.pack()

        skill_combobox = ctk.CTkComboBox(master=skill_frame,
                                         values=list(character.skills.keys()),
                                         width=235,
                                         height=15,
                                         fg_color=('#2A2A33'),
                                         border_color=('#D3A62C'),
                                         text_color=('#C9B273'),
                                         dropdown_fg_color=('#2A2A33'),
                                         dropdown_hover_color=('#1D1C21'),
                                         dropdown_text_color=('#C9B273'),
                                         button_color=('#616161'),
                                         button_hover_color=('#181823'),
                                         border_width=1,
                                         font=('Helvetica', 12),
                                         dropdown_font=('Helvetica', 11))
        skill_combobox.pack()

        # Armazena a referência à combobox no objeto do personagem
        character.skill_combobox = skill_combobox 

        self.update_skill_combobox_appearance(character, skill_combobox)

        use_skill_button = ctk.CTkButton(skill_frame,
                                         text="Usar",
                                         # Modifica o lambda para ignorar o evento
                                         command=lambda event=None: self.use_skill(character, skill_combobox.get()),
                                         width=50,
                                         height=20,
                                         fg_color='#2A2A33',
                                         border_color='#D3A62C',
                                         corner_radius=0,
                                         border_width=1,
                                         hover_color='#1D1C21',
                                         text_color='#C9B273',
                                         font=('Helvetica', 12, "bold"))
        use_skill_button.pack(side=ctk.LEFT, padx=1, pady=4)

        add_skill_button = ctk.CTkButton(skill_frame,
                                        text="Adicionar",
                                        command=lambda: self.add_skill(character),
                                        width=60,
                                        height=20,
                                        fg_color='#2A2A33',
                                        border_color='#D3A62C',
                                        corner_radius=0,
                                        border_width=1,
                                        hover_color='#1D1C21',
                                        text_color='#C9B273',
                                        font=('Helvetica', 12))
        add_skill_button.pack(side=ctk.LEFT, padx=2, pady=4)

        delete_skill_button = ctk.CTkButton(skill_frame,
                                        text="DEL. Skill",
                                        command=lambda: self.delete_skill(character, skill_combobox.get()),
                                        width=50,
                                        height=20,
                                        fg_color='#2A2A33',
                                        border_color='#D3A62C',
                                        corner_radius=0,
                                        border_width=1,
                                        hover_color='#1D1C21',
                                        text_color='#C9B273',
                                        font=('Helvetica', 12))
        delete_skill_button.pack(side=tk.LEFT, padx=1, pady=4)

        # Botão para editar skill
        edit_skill_button = ctk.CTkButton(skill_frame,
                                           text="Edit. Skill",
                                           command=lambda: self.edit_skill(character, skill_combobox.get()),
                                           width=50,
                                           height=20,
                                           fg_color='#2A2A33',
                                           border_color='#D3A62C',
                                           corner_radius=0,
                                           border_width=1,
                                           hover_color='#1D1C21',
                                           text_color='#C9B273',
                                           font=('Helvetica', 12))
        edit_skill_button.pack(side=tk.LEFT, padx=1, pady=4)

        cooldown_skills_frame = ctk.CTkScrollableFrame(frame,
                                                    fg_color='#282a36',   # Cor de fundo
                                                    corner_radius=0,
                                                    border_width=1,
                                                    border_color="#D3A62C",
                                                    width=250,            # Largura controlada
                                                    height=50)           # Altura ajustável
        cooldown_skills_frame.pack(side=tk.LEFT, padx=10, pady=5, fill='x')  # Controle de expansão lateral sem expandir verticalmente

        # Label para "Em Cooldown"
        cooldown_skills_label = ctk.CTkLabel(cooldown_skills_frame, text="Em Cooldown:",
                                            font=('Helvetica', 12),
                                            text_color=('black', 'white'),  # Cor do texto
                                            fg_color='#282a36',    # Cor de fundo
                                            corner_radius=5,       # Cantos arredondados
                                            padx=5, pady=0)        # Padding
        cooldown_skills_label.pack(side=tk.TOP, padx=5, pady=0)

        # Percorra as habilidades e adicione-as ao frame com scrollbar
        for skill_name, skill_data in character.skills.items():
            if skill_data['remaining_cooldown'] > 0:
                # Frame para cada habilidade em cooldown
                skill_frame = ctk.CTkFrame(cooldown_skills_frame, fg_color='#282a36', corner_radius=0)
                skill_frame.pack(anchor=tk.W, padx=5, pady=0, fill='x')  # Padding externo para separação lateral

                # Label do nome da habilidade
                skill_name_label = ctk.CTkLabel(skill_frame,
                                                text=f"- {skill_name}",
                                                font=('Helvetica', 11),
                                                text_color=('black', 'white'),
                                                height=0,
                                                fg_color='#282a36',
                                                corner_radius=10,
                                                padx=5, pady=2)  # Ajuste o padx para o espaço lateral desejado
                skill_name_label.pack(side=tk.LEFT)

                # Label do status do cooldown
                cooldown_status_label = ctk.CTkLabel(skill_frame,
                                                    text=f"(CD: {skill_data['remaining_cooldown']}/{skill_data['cooldown']}) ",
                                                    font=('Helvetica', 11, 'bold'),
                                                    text_color=('black', 'white'),
                                                    height=10,
                                                    fg_color='#282a36',
                                                    corner_radius=0,
                                                    padx=0, pady=2)
                cooldown_status_label.pack(side=tk.LEFT)
                
        # Frame para buffs/debuffs
        buffs_debuffs_frame = ctk.CTkFrame(frame, fg_color='#282a36', corner_radius=5, width=200, height=150, border_width=1, border_color="#D3A62C")
        buffs_debuffs_frame.pack(side=tk.LEFT, padx=10, pady=0)

        # Label para Buffs/Debuffs
        buffs_debuffs_label = ctk.CTkLabel(buffs_debuffs_frame, text="Buffs/Debuffs:",
                                            font=('Helvetica', 12),
                                            text_color=('black', 'white'),
                                            fg_color='#282a36',
                                            corner_radius=10,
                                            padx=5, pady=0)
        buffs_debuffs_label.pack(side=tk.TOP, padx=5, pady=0)

        # Exemplo de uso para buffs/debuffs
        for buff_debuff_name, buff_debuff_data in character.temp_buffs_debuffs.items():
            if buff_debuff_data['remaining_duration'] > 0:
                # Criando um frame para cada buff/debuff com padding interno
                buff_debuff_frame = ctk.CTkFrame(buffs_debuffs_frame, fg_color='#282a36', corner_radius=10)
                buff_debuff_frame.pack(anchor=tk.W, padx=5, pady=0, fill='x')  # Padding externo para separação vertical

                # Frame interno para adicionar padding extra ao redor das labels
                inner_frame = ctk.CTkFrame(buff_debuff_frame, fg_color='#282a36', corner_radius=10)
                inner_frame.pack(padx=3, pady=0, fill='x')  # Padding interno

                # Label do nome do buff/debuff
                buff_debuff_name_label = ctk.CTkLabel(inner_frame,
                                                    text=f"{buff_debuff_name}",
                                                    font=('Helvetica', 11),
                                                    text_color=('black', 'white'),
                                                    fg_color='#282a36',
                                                    height=10,
                                                    corner_radius=0,
                                                    padx=0, pady=2)
                buff_debuff_name_label.pack(side=tk.LEFT)

                # Label do status da duração restante
                remaining_time = buff_debuff_data['remaining_duration']
                buff_debuff_duration_label = ctk.CTkLabel(inner_frame,
                                                        text=f"  (CD: {remaining_time} turnos)",
                                                        font=('Helvetica', 11, 'bold'),
                                                        text_color=('black', 'white'),
                                                        fg_color='#282a36',
                                                        height=10,
                                                        corner_radius=0,
                                                        padx=0, pady=2)
                buff_debuff_duration_label.pack(side=tk.LEFT)

                # Botão para remover buff/debuff
                remove_buff_debuff_button = ctk.CTkButton(inner_frame,
                                                        text="x",
                                                        command=lambda buff_name=buff_debuff_name: self.remove_buff_debuff(character, buff_name),
                                                        font=("Helvetica", 8),
                                                        width=0,
                                                        height=0,
                                                        fg_color='transparent',  # Cor de fundo do botão
                                                        corner_radius=5)  # Raio dos cantos do botão
                remove_buff_debuff_button.pack(side=tk.RIGHT, padx=1, pady=0)

        # Botão para adicionar buff/debuff
        add_buff_debuff_button = ctk.CTkButton(buffs_debuffs_frame,
                                            text="Add Buff",
                                            command=lambda: self.add_buff_debuff(character),
                                            width=50,
                                            height=10,
                                            fg_color=('#2A2A33'),
                                            border_color=('#D3A62C'), 
                                            corner_radius=0,
                                            border_width=1,  # Largura da borda
                                            hover_color=('#1D1C21'),
                                            text_color=('#C9B273'),  # Cor do texto
                                            font=('Helvetica', 12))  # Fonte Helvetica tamanho 12
        add_buff_debuff_button.pack(side=tk.TOP, padx=1, pady=2)

    def remove_bar_from_player(self, player, bar_name):
        if bar_name in player.bar_data:
            # Destrói os widgets da barra
            bar_frame = player.bar_data[bar_name]['bar_frame']
            if bar_frame:
                bar_frame.destroy()

            # Remove os dados da barra do jogador
            del player.bar_data[bar_name]

            # Atualiza a exibição do personagem
            self.update_character_display()

    def add_buff_debuff(self, character):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Adicionar Buff/Debuff")

        # Garante que a janela apareça por cima de outras (mesmo após perder o foco)
        dialog.attributes('-topmost', True)
        dialog.lift()  # Traz a janela para frente ao ser criada

        # Aumenta o tamanho da janela 
        dialog.geometry("255x230") 

        name_label = ctk.CTkLabel(dialog, text="Nome do Buff/Debuff:")
        name_label.pack(pady=5)
        name_entry = ctk.CTkEntry(dialog)
        name_entry.pack(pady=5)

        duration_label = ctk.CTkLabel(dialog, text="Duração (turnos):")
        duration_label.pack(pady=5)
        duration_entry = ctk.CTkEntry(dialog)
        duration_entry.pack(pady=5)

        # Checkbox para indicar se é um DoT
        is_dot_checkbox = ctk.CTkCheckBox(dialog, text="É um DoT?")
        is_dot_checkbox.pack(pady=5)

        def confirm_add():
            buff_debuff_name = name_entry.get()
            try:
                duration = int(duration_entry.get())
                if duration > 0:
                    is_dot = is_dot_checkbox.get()  # Obtém o valor do checkbox (1 se marcado, 0 se não)
                    character.add_temp_buff_debuff(buff_debuff_name, duration, buff_type="dot" if is_dot else "buff_debuff")
                    self.update_character_display()
                    dialog.destroy()
                else:
                    messagebox.showerror("Erro", "A duração deve ser maior que zero.")
            except ValueError:
                messagebox.showerror("Erro", "A duração deve ser um número inteiro.")

        confirm_button = ctk.CTkButton(dialog, text="Adicionar", command=confirm_add)
        confirm_button.pack(pady=10)

        # Centralizar a janela na tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = dialog.winfo_reqwidth()
        window_height = dialog.winfo_reqheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        dialog.geometry(f"+{x}+{y}")

    def remove_buff_debuff(self, character, buff_name):
        def delete_buff():
            if isinstance(character, Character):  # Check if it's a Character
                character.remove_buff_debuff(buff_name)
            elif isinstance(character, NPC):  # Check if it's an NPC
                if buff_name in character.temp_buffs_debuffs:
                    del character.temp_buffs_debuffs[buff_name]
                else:
                    messagebox.showerror("Erro", f"{character.name} não possui o buff/debuff '{buff_name}'.")
            else:
                messagebox.showerror("Erro", "Tipo de personagem não suportado.") 

            self.update_character_display()
            confirm_window.destroy()

        def edit_buff():
            def save_changes():
                new_name = name_entry.get()
                try:
                    new_duration = int(duration_entry.get())
                    if new_duration > 0:
                        # Update the buff/debuff
                        if new_name != buff_name:
                            character.temp_buffs_debuffs[new_name] = character.temp_buffs_debuffs.pop(buff_name)
                        character.temp_buffs_debuffs[new_name]['duration'] = new_duration
                        character.temp_buffs_debuffs[new_name]['remaining_duration'] = new_duration
                        self.update_character_display()
                        edit_window.destroy()
                    else:
                        messagebox.showerror("Erro", "A duração deve ser maior que zero.")
                except ValueError:
                    messagebox.showerror("Erro", "A duração deve ser um número inteiro.")

            confirm_window.destroy()
            edit_window = ctk.CTkToplevel(self.root)
            edit_window.title("Edit Buff/Debuff")
            edit_window.attributes('-topmost', True)
            edit_window.geometry("300x200")

            name_label = ctk.CTkLabel(edit_window, text="Novo nome:")
            name_label.pack(pady=5)
            name_entry = ctk.CTkEntry(edit_window)
            name_entry.insert(0, buff_name)
            name_entry.pack(pady=5)

            duration_label = ctk.CTkLabel(edit_window, text="Nova duração (turnos):")
            duration_label.pack(pady=5)
            duration_entry = ctk.CTkEntry(edit_window)
            duration_entry.insert(0, str(character.temp_buffs_debuffs[buff_name]['duration']))
            duration_entry.pack(pady=5)

            save_button = ctk.CTkButton(edit_window, text="Salvar", command=save_changes)
            save_button.pack(pady=10)

        # Ask for confirmation before deleting or editing
        confirm_window = ctk.CTkToplevel(self.root)
        confirm_window.title("Confirmação")
        confirm_window.attributes('-topmost', True)
        confirm_window.geometry("340x160")

        ctk.CTkLabel(confirm_window, text=f"Deseja deletar ou editar o buff/debuff '{buff_name}'?").pack(pady=10)

        delete_button = ctk.CTkButton(confirm_window, text="Deletar", command=delete_buff)
        delete_button.pack(pady=5)

        edit_button = ctk.CTkButton(confirm_window, text="Editar", command=edit_buff)
        edit_button.pack(pady=5)

    def update_skill_combobox_appearance(self, character, combobox):
        values = []
        for skill_name in character.skills.keys():
            if character.skills[skill_name]['remaining_cooldown'] == 0:
                # Adiciona o ícone ♦ na frente da habilidade
                values.append(f"♦ {skill_name}")
            else:
                values.append(skill_name)

        combobox.configure(values=values)

    def buy_item(self, character, shop_combobox):
        selected_item = shop_combobox.get()
        if selected_item == "Poção Cura P. 25% HP - 350 Gold":
            cost = 350
            hp_restore = int(character.max_hp * 0.25)
            if character.player_gold >= cost:
                character.player_gold -= cost
                character.hp = min(character.hp + hp_restore, character.max_hp)
        elif selected_item == "Poção Cura M. 50% HP - 700 Gold":
            cost = 700
            hp_restore = int(character.max_hp * 0.50)
            if character.player_gold >= cost:
                character.player_gold -= cost
                character.hp = min(character.hp + hp_restore, character.max_hp)
        elif selected_item == "Poção Cura G. 100% HP - 1400 Gold":
            cost = 1400
            hp_restore = int(character.max_hp * 1.00)
            if character.player_gold >= cost:
                character.player_gold -= cost
                character.hp = min(character.hp + hp_restore, character.max_hp)
        elif selected_item == "Poção Mana P. 25% MP - 500 Gold":
            cost = 500
            mp_restore = int(character.max_mp * 0.25)
            if character.player_gold >= cost:
                character.player_gold -= cost
                character.mp = min(character.mp + mp_restore, character.max_mp)
        elif selected_item == "Poção Mana M. 50% MP - 1000 Gold":
            cost = 1000
            mp_restore = int(character.max_mp * 0.50)
            if character.player_gold >= cost:
                character.player_gold -= cost
                character.mp = min(character.mp + mp_restore, character.max_mp)
        elif selected_item == "Poção Mana G. 100% MP - 2000 Gold":
            cost = 2000
            mp_restore = int(character.max_mp * 1.00)
            if character.player_gold >= cost:
                character.player_gold -= cost
                character.mp = min(character.mp + mp_restore, character.max_mp)
        self.update_character_display()

    def open_mana_window(self, character):
        # Cria a nova janela
        mana_window = ctk.CTkToplevel(self.root)
        mana_window.title("Modificar Mana")
        mana_window.attributes('-topmost', 'true')  # Mantém a janela sempre no topo

        # Obtém a posição da janela de origem
        x = self.root.winfo_x() + 100  # 100 pixels à direita
        y = self.root.winfo_y() + 100  # 100 pixels abaixo

        # Define a posição da nova janela
        mana_window.geometry(f"+{x}+{y}")

        mana_label = ctk.CTkLabel(mana_window, text="Insira o valor de mana:")
        mana_label.pack(pady=10)

        mana_entry = ctk.CTkEntry(mana_window)
        mana_entry.pack(pady=10)
        mana_entry.focus()  # Define o foco no campo de entrada

        def use_mana():
            mana = int(mana_entry.get())
            character.mp = max(character.mp - mana, 0)
            mana_window.destroy()
            character.mp_label.configure(text=f" {character.mp}/{character.max_mp} ")
            character.mp_bar.set(character.mp / character.max_mp if character.max_mp > 0 else 0)

        def restore_mana():
            restore = int(mana_entry.get())
            character.mp = min(character.mp + restore, character.max_mp)
            mana_window.destroy()
            character.mp_label.configure(text=f" {character.mp}/{character.max_mp} ")
            character.mp_bar.set(character.mp / character.max_mp if character.max_mp > 0 else 0)

        use_button = ctk.CTkButton(mana_window, text="Usar", command=use_mana)
        use_button.pack(side=ctk.LEFT, padx=10, pady=10)

        restore_button = ctk.CTkButton(mana_window, text="Recuperar", command=restore_mana)
        restore_button.pack(side=ctk.LEFT, padx=10, pady=10)

    def modify_character(self, character, action):
        if action == "hp":
            damage = simpledialog.askinteger("Input", "Quanto de dano?", parent=self.root)
            if damage:
                character.hp = max(character.hp - damage, 0)

                # Check if hp_label and hp_bar are not None before configuring
                if character.hp_label is not None and character.hp_bar is not None:
                    character.hp_label.configure(text=f" {character.hp}/{character.max_hp} ")
                    character.hp_bar.set(character.hp / character.max_hp if character.max_hp > 0 else 0)
                else:
                    print(f"Error: hp_label or hp_bar is None for character {character.name}")

        elif action == "heal":
            heal = simpledialog.askinteger("Input", "Quanto curar?", parent=self.root)
            if heal:
                character.hp = min(character.hp + heal, character.max_hp)

                # Update the HP label and bar directly
                if character.hp_label is not None and character.hp_bar is not None:
                    character.hp_label.configure(text=f" {character.hp}/{character.max_hp} ")
                    character.hp_bar.set(character.hp / character.max_hp if character.max_hp > 0 else 0)
                else:
                    print(f"Error: hp_label or hp_bar is None for character {character.name}")

        elif action == "increase_max_hp":
            new_max_hp = simpledialog.askinteger("Input", "Novo HP Max:", parent=self.root)
            if new_max_hp and new_max_hp > 0:
                character.max_hp = new_max_hp
                if character.hp > new_max_hp:
                    character.hp = new_max_hp

                # Update the HP label and bar directly
                if character.hp_label is not None and character.hp_bar is not None:
                    character.hp_label.configure(text=f" {character.hp}/{character.max_hp} ")
                    character.hp_bar.set(character.hp / character.max_hp if character.max_hp > 0 else 0)
                else:
                    print(f"Error: hp_label or hp_bar is None for character {character.name}")

        elif action == "increase_max_mp":
            new_max_mp = simpledialog.askinteger("Input", "Novo MP Max:", parent=self.root)
            if new_max_mp and new_max_mp > 0:
                character.max_mp = new_max_mp
                if character.mp > new_max_mp:
                    character.mp = new_max_mp
        elif action == "increase_max_mp":
            new_max_mp = simpledialog.askinteger("Input", "Novo MP Max:", parent=self.root)
            if new_max_mp and new_max_mp > 0:
                character.max_mp = new_max_mp
                if character.mp > new_max_mp:
                    character.mp = new_max_mp

    def modify_bar_value(self, character, action, bar_name, event=None):
        if not hasattr(character, 'bar_data') or not character.bar_data:
            messagebox.showinfo("Informação", "Nenhuma barra para modificar.")
            return

        bar_data = character.bar_data[bar_name]  # Usa o bar_name passado como argumento

        if action == "add":
            value_to_add = simpledialog.askinteger("Adicionar Valor", "Valor a adicionar:", parent=self.root)
            if value_to_add is not None:
                bar_data['current_value'] = min(bar_data['current_value'] + value_to_add, bar_data['max_value'])
                # Atualiza a barra de progresso e o label de valor
                bar_data['bar'].set(bar_data['current_value'] / bar_data['max_value'])
                bar_data['bar_value_label'].configure(text=f"{bar_data['current_value']}/{bar_data['max_value']}")
                # Removida a chamada para self.update_character_display()
                character.bar_widgets[bar_name]['bar'].set(bar_data['current_value'] / bar_data['max_value'])
                character.bar_widgets[bar_name]['bar_value_label'].configure(text=f"{bar_data['current_value']}/{bar_data['max_value']}")

        elif action == "remove":
            value_to_remove = simpledialog.askinteger("Remover Valor", "Valor a remover:", parent=self.root)
            if value_to_remove is not None:
                bar_data['current_value'] = max(bar_data['current_value'] - value_to_remove, 0)
                # Atualiza a barra de progresso e o label de valor
                bar_data['bar'].set(bar_data['current_value'] / bar_data['max_value'])
                bar_data['bar_value_label'].configure(text=f"{bar_data['current_value']}/{bar_data['max_value']}")
                # Removida a chamada para self.update_character_display()

        elif action == "alter_total":
            new_max_value = simpledialog.askinteger("Alterar Total", "Novo valor máximo:", parent=self.root)
            if new_max_value is not None and new_max_value > 0:
                bar_data['max_value'] = new_max_value
                # Ajusta o valor atual se necessário
                bar_data['current_value'] = min(bar_data['current_value'], bar_data['max_value'])
                # Atualiza a barra de progresso e o label de valor
                bar_data['bar'].set(bar_data['current_value'] / bar_data['max_value'])
                bar_data['bar_value_label'].configure(text=f"{bar_data['current_value']}/{bar_data['max_value']}")
                # Removida a chamada para self.update_character_display()

    def edit_gold(self, character):
        add_gold = simpledialog.askinteger("Add Gold", f"Atual valor de Gold: ${character.player_gold}\nInserir valor de Gold para inserir (Ou subtrair):")
        if add_gold is not None:
            character.player_gold += add_gold
            self.update_character_display()

    def add_skill(self, character):
        skill_name = simpledialog.askstring("Input", "Nome da habilidade:", parent=self.root)
        cooldown = simpledialog.askinteger("Input", "Cooldown:", parent=self.root)
        mana_cost = simpledialog.askinteger("Input", "Custo de mana (opcional):", parent=self.root)
        hp_cost = simpledialog.askinteger("Input", "Custo de HP (opcional):", parent=self.root)
        description = simpledialog.askstring("Input", "Descrição da habilidade:", parent=self.root)  # Campo para a descrição
        add_buff_debuff = messagebox.showinfo("Adicionar Buff/Debuff", "Adicionar buff/debuff temporário?")

        if skill_name and cooldown is not None:
            if add_buff_debuff:
                buff_debuff_name = simpledialog.askstring("Input", "Nome do Buff/Debuff:", parent=self.root)
                buff_debuff_duration = simpledialog.askinteger("Input", "Duração do Buff/Debuff:", parent=self.root)
                character.add_skill(skill_name, cooldown, mana_cost or 0, hp_cost or 0, description or "", temp_buff_debuff={'name': buff_debuff_name, 'duration': buff_debuff_duration})
            else:
                character.add_skill(skill_name, cooldown, mana_cost or 0, hp_cost or 0, description or "")
            self.update_character_display()

    def use_skill(self, character, name):
        # Remove as tags HTML e o símbolo ♦ do nome da habilidade
        import re
        name = re.sub('<[^<]+?>', '', name)  # Remove tags HTML
        name = name.replace('♦ ', '')  # Remove o símbolo ♦ e o espaço em branco

        # Chama o método use_skill da classe Character 
        success = character.use_skill(name) 

        if success:
            pass 

    def delete_skill(self, character, skill_name):
        skill = character.skills.get(skill_name)
        if skill:
            del character.skills[skill_name]
            messagebox.showinfo("Success", f"Habilidade '{skill_name}' removida com sucesso!")
            self.update_character_display()  # Atualiza a exibição do personagem após remover a habilidade
        else:
            messagebox.showerror("Erro", "Habilidade inexistente.")

    def edit_skill(self, character, skill_name):
        # Remove as tags HTML e o símbolo ♦ do nome da habilidade
        import re
        skill_name = re.sub('<[^<]+?>', '', skill_name)  # Remove tags HTML
        skill_name = skill_name.replace('♦ ', '')  # Remove o símbolo ♦ e o espaço em branco

        # Verifica se a habilidade existe
        if skill_name not in character.skills:
            messagebox.showerror("Erro", "Habilidade inexistente.")
            return

        # Obtém os dados da habilidade
        skill_data = character.skills[skill_name]

        # Chama a função skill_dialog para editar a habilidade
        self.skill_dialog("Editar Habilidade", skill_data, skill_name, player=character)  # Passa o personagem como argumento

    def skill_dialog(self, title, skill_data, skill_name=None, new_skill=False, player=None):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.attributes('-topmost', True) 
        dialog.geometry("470x430")

        # Use um frame para organizar os elementos dentro da janela de diálogo
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Campos de entrada para as informações da habilidade
        ctk.CTkLabel(main_frame, text="Nome da Habilidade:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        name_entry = ctk.CTkEntry(main_frame, width=250)  # Increased width to 250
        if skill_name:
            name_entry.insert(0, skill_name)
        name_entry.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(main_frame, text="Cooldown:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        cooldown_entry = ctk.CTkEntry(main_frame)
        cooldown_entry.insert(0, str(skill_data.get("cooldown", 0)))
        cooldown_entry.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(main_frame, text="Mana Cost:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        mana_entry = ctk.CTkEntry(main_frame)
        mana_entry.insert(0, str(skill_data.get("mana_cost", 0)))
        mana_entry.grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkLabel(main_frame, text="HP Cost:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        hp_entry = ctk.CTkEntry(main_frame)
        hp_entry.insert(0, str(skill_data.get("hp_cost", 0)))
        hp_entry.grid(row=3, column=1, padx=5, pady=5)

        ctk.CTkLabel(main_frame, text="Remaining Cooldown:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        remaining_cooldown_entry = ctk.CTkEntry(main_frame)
        remaining_cooldown_entry.insert(0, str(skill_data.get("remaining_cooldown", 0)))
        remaining_cooldown_entry.grid(row=4, column=1, padx=5, pady=5)

        ctk.CTkLabel(main_frame, text="Buff/Debuff Nome:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        buff_debuff_name_entry = ctk.CTkEntry(main_frame)
        buff_debuff_name_entry.insert(0, skill_data.get("temp_buff_debuff", {}).get("name", ""))
        buff_debuff_name_entry.grid(row=5, column=1, padx=5, pady=5)

        ctk.CTkLabel(main_frame, text="Buff/Debuff Duração:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        buff_debuff_duration_entry = ctk.CTkEntry(main_frame)
        buff_debuff_duration_entry.insert(0, str(skill_data.get("temp_buff_debuff", {}).get("duration", 0)))
        buff_debuff_duration_entry.grid(row=6, column=1, padx=5, pady=5)

        ctk.CTkLabel(main_frame, text="Descrição da Habilidade:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        description_entry = ctk.CTkEntry(main_frame)
        description_entry.insert(0, str(skill_data.get("description", "")))
        description_entry.grid(row=7, column=1, padx=5, pady=5)

        # Botões para salvar ou cancelar as alterações
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=(20, 0))  # Adicione espaço acima dos botões

        ok_button = ctk.CTkButton(button_frame, text="OK", command=lambda: self.save_skill_edits(
            dialog, player, skill_name, name_entry, cooldown_entry, mana_entry, hp_entry,
            remaining_cooldown_entry, buff_debuff_name_entry, buff_debuff_duration_entry, description_entry
        ))
        ok_button.pack(side="left", padx=(0, 10))

        cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=dialog.destroy)
        cancel_button.pack(side="left")

        dialog.mainloop()
        
    def save_skill_edits(self, dialog, player, old_skill_name, name_entry, cooldown_entry, mana_entry, hp_entry,
                        remaining_cooldown_entry, buff_debuff_name_entry, buff_debuff_duration_entry, description_entry):
        new_skill_name = name_entry.get()
        try:
            new_cooldown = int(cooldown_entry.get())
            new_mana_cost = int(mana_entry.get())
            new_hp_cost = int(hp_entry.get())
            new_remaining_cooldown = int(remaining_cooldown_entry.get())
            new_buff_debuff_name = buff_debuff_name_entry.get()
            new_buff_debuff_duration = int(buff_debuff_duration_entry.get())
            new_description = description_entry.get()

            # Atualiza os dados da habilidade no personagem
            if old_skill_name in player.skills:
                # Se o nome da habilidade foi alterado, remove a habilidade antiga e adiciona a nova
                if new_skill_name != old_skill_name:
                    del player.skills[old_skill_name]

                # Define temp_buff_debuff como None se new_buff_debuff_name estiver vazio
                temp_buff_debuff = {'name': new_buff_debuff_name, 'duration': new_buff_debuff_duration} if new_buff_debuff_name else None

                player.skills[new_skill_name] = {
                    'cooldown': new_cooldown,
                    'mana_cost': new_mana_cost,
                    'hp_cost': new_hp_cost,
                    'remaining_cooldown': new_remaining_cooldown,
                    'temp_buff_debuff': temp_buff_debuff,
                    'description': new_description
                }

                messagebox.showinfo("Successo", "Habilidade editada com sucesso!")
                self.update_character_display()
                dialog.destroy()
            else:
                messagebox.showerror("Erro", "Habilidade não encontrada.")

        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos. Certifique-se de que todos os campos numéricos contenham números inteiros.")

    def add_exp(self):
        exp = simpledialog.askinteger("Input", "Quanto de XP adicionar?", parent=self.root)
        if exp:
            self.players[0].exp += exp  # Aumenta a XP do jogador
            self.level_up()  # Verifica se o jogador deve subir de nível
            self.update_exp_bar()

    def set_max_exp(self):
        max_exp = simpledialog.askinteger("Input", "Novo XP máximo:", parent=self.root)
        if max_exp:
            self.players[0].max_exp = max_exp
            self.update_exp_bar()

    def set_level(self):
        level = simpledialog.askinteger("Input", "Novo nível:", parent=self.root)
        if level:
            self.players[0].level = level
            self.update_exp_bar()

    def level_up(self):
        player = self.players[0]
        if player.exp >= player.max_exp:
            player.level += 1
            player.exp -= player.max_exp
            player.max_exp = int(player.max_exp * 1.15)  # Aumenta o XP máximo necessário para o próximo nível
            self.level_label.configure(text=f"Level {player.level}")
            self.exp_label.configure(text=f"EXP {player.exp}/{player.max_exp}")

    def update_exp_bar(self):
        player = self.players[0]
        if player.max_exp > 0:
            progress_value = (player.exp / player.max_exp) * 1
        else:
            progress_value = 0
        self.exp_bar.set(progress_value)
        self.exp_label.configure(text=f"EXP: {player.exp}/{player.max_exp}")
        self.level_label.configure(text=f"Level: {player.level}")

    def add_turn(self):
        self.turn_count += 1
        self.turn_label.configure(text=f"Turno: {self.turn_count}")
        # Atualiza cooldowns e aplica DoTs
        for character in self.players:
            character.decrease_skill_cooldowns()
            character.decrease_buff_debuff_durations_by_turn() 
        self.aplicar_dano_por_turno()

        # Atualiza a interface após as mudanças no estado do jogo
        self.update_character_display()

    def remove_turn(self):
        if self.turn_count > 0:
            self.turn_count -= 1
            self.turn_label.configure(text=f"Turno: {self.turn_count}")

    def update_character_cooldowns(self):
        for character in self.players:
            character.decrease_skill_cooldowns()
            character.decrease_buff_debuff_durations_by_turn()  # Novo método para decrementar buffs/debuffs por turno
        self.update_character_display()
                # Atualiza a aparência das comboboxes após atualizar os cooldowns
        for player in self.players:
            skill_combobox = player.skill_combobox 
            if skill_combobox:
                self.update_skill_combobox_appearance(player, skill_combobox)

    def end_combat(self):
        for player in self.players:
            for skill in player.skills.values():
                skill['remaining_cooldown'] = 0  # Reseta todos os cooldowns das habilidades
        self.turn_count = 0  # Reseta o contador de turnos
        self.turn_label.configure(text=f"Turno: {self.turn_count}")
        self.update_character_display()  # Atualiza a exibição dos personagens

    def update_exhaustion_bar(self, value):
        self.exhaustion_bar['value'] = value
        
        self.turn_navigation_frame = tk.Frame(root)
        self.turn_navigation_frame.pack(pady=10)
        
        self.prev_turn_button = tk.Button(self.turn_navigation_frame, text="Voltar", command=self.prev_turn)
        self.prev_turn_button.pack(side=tk.LEFT, padx=5)
        
        self.next_turn_button = tk.Button(self.turn_navigation_frame, text="Próximo", command=self.next_turn)
        self.next_turn_button.pack(side=tk.LEFT, padx=5)
       
    def next_turn(self):
        if self.combatant:
            self.current_turn = (self.current_turn + 1) % len(self.combatant)
            self.update_combatant_display()

    def prev_turn(self):
        if self.combatant:
            self.current_turn = (self.current_turn - 1) % len(self.combatant)
            self.update_combatant_display()

    def save_data(self):
        data = {
            "players": [player.to_dict() for player in self.players],
            "exhaustion_value": self.exhaustion_value,
            "turn_count": self.turn_count,
            "npcs": [npc.to_dict() for npc in self.npcs],
            "combatants": self.combatants,  # Adiciona a lista de combatentes
            "players": [player.to_dict() for player in self.players],
        }
        with open("character_data.json", "w") as f:
            json.dump(data, f)
        messagebox.showinfo("Success", "Dados salvos com sucesso.")

    def load_data(self):
        if os.path.exists("character_data.json"):
            with open("character_data.json", "r") as f:
                data = json.load(f)
                self.players = [Character.from_dict(char_data) for char_data in data["players"]]
                self.npcs = [NPC.from_dict(npc_data) for npc_data in data.get("npcs", [])]
                self.combatants = data.get("combatants", [])  # Carrega a lista de combatentes ou cria uma vazia se não existir
                self.exhaustion_value = data.get("exhaustion_value", 0)
                self.turn_count = data.get("turn_count", 0)
                self.update_exhaustion_display()
                self.update_character_display()
                self.update_exp_bar()
                self.turn_label.configure(text=f"Turno: {self.turn_count}")
            for npc in self.npcs:
                if npc.spinbox:  # Verifica se o spinbox existe (foi criado)
                    npc.spinbox.set(npc.spinbox_value)
        else:
            messagebox.showerror("Error", "Arquivo de dados não encontrado.")

if __name__ == "__main__":
    root = tk.Tk()

    color_styles = {
    'green': 'Green.Horizontal.TProgressbar',
    'red': 'Red.Horizontal.TProgressbar',
    'light gray': 'LightGray.Horizontal.TProgressbar',
    'orange': 'Orange.Horizontal.TProgressbar',
    'black': 'Black.Horizontal.TProgressbar'
    }

    # Define o estilo da barra de progresso verde para HP
    style = Style()
    style.theme_use('default')
    style.configure('green.Horizontal.TProgressbar', foreground='green', background='green')

    # Define o estilo da barra de progresso azul para MP
    style.configure('blue.Horizontal.TProgressbar', foreground='blue', background='blue')

    # Define o estilo para a barra de progresso de HP vermelha
    style = Style()
    style.configure('red.Horizontal.TProgressbar', foreground='red', background='red')
    
   # Instância do primeiro app (App)
    app = App(root)
    
    # Ajustando a posição da janela principal
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 1620  # largura desejada da janela principal
    window_height = 960  # altura desejada da janela principal
    x = (screen_width - window_width) // 2  # calcula a posição X central
    y = (screen_height - window_height) // 2  # calcula a posição Y central
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")  # define a geometria da janela principal
    
    root.mainloop()
