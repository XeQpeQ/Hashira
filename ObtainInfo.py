import requests
import tkinter as tk
from tkinter import ttk, scrolledtext
from ttkthemes import ThemedStyle
from threading import Thread

# Lista para almacenar los nombres recientes buscados
nombres_recientes = []

def get_user_id(username):
    api_endpoint = 'https://users.roblox.com/v1/usernames/users'
    request_payload = {'usernames': [username], 'excludeBannedUsers': True}
    response = requests.post(api_endpoint, json=request_payload)
    if response.status_code == 200 and response.json()['data']:
        user_id = response.json()['data'][0]['id']
        return user_id
    return None

def get_account_creation_date(user_id):
    account_info_endpoint = f'https://users.roblox.com/v1/users/{user_id}'
    response = requests.get(account_info_endpoint)
    if response.status_code == 200:
        creation_date = response.json()['created']
        return creation_date.split('T')[0]  # Obtener la fecha sin la parte de la hora
    return 'Desconocida'

def get_user_friends(user_id):
    friends_endpoint = f'https://friends.roblox.com/v1/users/{user_id}/friends'
    response = requests.get(friends_endpoint)
    if response.status_code == 200:
        friends_data = response.json()['data']
        return [{'username': friend['name'], 'id': friend['id'], 'is_banned': friend['isBanned'], 'creation_date': get_account_creation_date(friend['id'])} for friend in friends_data]
    return []

def get_user_followers(user_id, limit=10, cursor=None):
    followers_endpoint = f'https://friends.roblox.com/v1/users/{user_id}/followers'
    params = {'limit': limit, 'cursor': cursor} if cursor else {'limit': limit}
    response = requests.get(followers_endpoint, params=params)
    if response.status_code == 200:
        followers_data = response.json()['data']
        next_cursor = response.json().get('nextPageCursor')
        return [{'username': follower['name'], 'id': follower['id'], 'status': follower.get('status', 'Desconocido'), 'creation_date': follower.get('created')} for follower in followers_data], next_cursor
    return [], None

def get_user_robux(user_id):
    robux_endpoint = f'https://economy.roblox.com/v1/users/{user_id}/currency'
    response = requests.get(robux_endpoint)
    if response.status_code == 200:
        robux_amount = response.json().get('robux', 0)
        return robux_amount
    return 0

def update_info_display(selected_user):
    user_id = selected_user.get('id')

    account_creation_date = get_account_creation_date(user_id)
    friends = get_user_friends(user_id)
    robux_amount = get_user_robux(user_id)

    result_label.config(text=f'ID de Usuario: {user_id}\nCuenta creada el: {account_creation_date}\nRobux: {robux_amount}')

    # Limpiar la lista de amigos previos
    for row in tree_friends.get_children():
        tree_friends.delete(row)

    # Mostrar la lista de amigos en el Treeview
    for friend in friends:
        status = 'Baneado' if friend['is_banned'] else 'No Baneado'
        tree_friends.insert("", "end", values=(friend['username'], friend['id'], status, friend['creation_date']))

    # Iniciar hilos en segundo plano para obtener y mostrar seguidores en el Treeview
    thread_followers = Thread(target=update_followers_display, args=(user_id,))
    thread_followers.start()

def update_followers_display(user_id):
    # Obtener y mostrar seguidores en lotes
    limit = 10  # Número de seguidores por página
    cursor = None

    while True:
        followers_data, next_cursor = get_user_followers(user_id, limit, cursor)

        # Mostrar la lista de seguidores en el Treeview
        for follower in followers_data:
            username = follower.get('username', 'Usuario Desconocido')
            status = follower.get('status', 'Desconocido')
            creation_date = follower.get('creation_date', 'Desconocida')
            tree_followers.insert("", "end", values=(username, follower['id'], status, creation_date))

        if not next_cursor:
            break

        cursor = next_cursor

# Configuración de la interfaz
app = tk.Tk()
app.title("Información de Usuario Roblox")
app.geometry("800x600")  # Tamaño fijo de la interfaz

# Centrar la ventana en la pantalla
app.eval('tk::PlaceWindow . center')

# Aplicar un tema personalizado
style = ThemedStyle(app)
style.set_theme("equilux")

# Frame principal
frame = ttk.Frame(app)
frame.pack(fill="both", expand=True)

# Frame para la entrada del usuario
frame_input = ttk.Frame(frame)
frame_input.pack(pady=10)

# Etiqueta y entrada para el nombre de usuario
username_label = ttk.Label(frame_input, text="Nombre de Usuario:")
username_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
username_entry = ttk.Entry(frame_input)
username_entry.grid(row=0, column=1, padx=10, pady=10)

# Botón para obtener la información del usuario
get_info_button = ttk.Button(frame_input, text="Obtener Información", command=lambda: update_info_display({'id': get_user_id(username_entry.get())}))
get_info_button.grid(row=1, column=0, columnspan=2, pady=10)

# Combobox para mostrar nombres recientes
nombres_combobox = ttk.Combobox(frame_input, values=tuple(nombres_recientes), state="readonly")
nombres_combobox.grid(row=2, column=0, columnspan=2, pady=10)
nombres_combobox.set("Nombres Recientes")

# Asociar la función de obtener información al cambio en el Combobox
nombres_combobox.bind("<<ComboboxSelected>>", lambda event: update_info_display({'id': get_user_id(nombres_combobox.get())}))

# Configuración del Frame interior para mostrar la información
frame_info = ttk.Frame(frame)
frame_info.pack(expand=True)

# Etiqueta para mostrar el resultado
result_label = ttk.Label(frame_info, text="")
result_label.pack(pady=10)

# Configurar el Treeview para mostrar la lista de amigos
friends_label = ttk.Label(frame_info, text='Amigos:')
friends_label.pack()

tree_friends = ttk.Treeview(frame_info, columns=('Username', 'ID', 'Status', 'Creation Date'), show='headings')
tree_friends.heading('Username', text="Username")
tree_friends.heading('ID', text="ID")
tree_friends.heading('Status', text="Status")
tree_friends.heading('Creation Date', text="Creation Date")
tree_friends.column('Username', stretch=tk.NO, width=150)
tree_friends.column('ID', stretch=tk.NO, width=100)
tree_friends.column('Status', stretch=tk.NO, width=100)
tree_friends.column('Creation Date', stretch=tk.NO, width=100)
tree_friends.pack()

# Configuración del Treeview para mostrar la lista de seguidores
followers_label = ttk.Label(frame_info, text='Seguidores:')
followers_label.pack()

tree_followers = ttk.Treeview(frame_info, columns=('Username', 'ID', 'Status', 'Creation Date'), show='headings')
tree_followers.heading('Username', text="Username")
tree_followers.heading('ID', text="ID")
tree_followers.heading('Status', text="Status")
tree_followers.heading('Creation Date', text="Creation Date")
tree_followers.column('Username', stretch=tk.NO, width=150)
tree_followers.column('ID', stretch=tk.NO, width=100)
tree_followers.column('Status', stretch=tk.NO, width=100)
tree_followers.column('Creation Date', stretch=tk.NO, width=100)
tree_followers.pack()

# Main loop
app.mainloop()
