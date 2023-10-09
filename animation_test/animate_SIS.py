import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.animation import FuncAnimation
import matplotlib
matplotlib.use('TkAgg')


def simulate_sis_model(graph, infection_prob, recovery_prob, num_iterations):
    num_nodes = graph.number_of_nodes()
    infected = set()

    # Seleccionar un nodo inicialmente infectado al azar
    initial_node = np.random.choice(list(graph.nodes()))
    infected.add(initial_node)
    quantity_timestamp = None
    quantity_infected = []
    quantity_susceptible = []
    for _ in range(num_iterations):
        # Crear una copia del conjunto de nodos infectados para evitar iterar sobre un conjunto cambiante
        current_infected = list(infected)
        quantity_infected.append(len(current_infected))
        quantity_susceptible.append(num_nodes - len(current_infected))
        # Iterar sobre los nodos infectados
        for node in current_infected:
            neighbors = list(graph.neighbors(node))
            # Propagar la infección a los vecinos susceptibles
            for neighbor in neighbors:
                if neighbor not in infected and np.random.random() < infection_prob:
                    infected.add(neighbor)

            # Recuperar los nodos infectados con cierta probabilidad
            if np.random.random() < recovery_prob:
                infected.remove(node)
    quantity_timestamp = pd.DataFrame({'timestamp': np.arange(0, num_iterations), 'num_infected': np.array(
        quantity_infected), 'num_susceptible': np.array(quantity_susceptible)})
    return infected, quantity_timestamp


# Crear un grafo aleatorio utilizando la biblioteca NetworkX
num_nodes = 50
avg_degree = 4
graph = nx.erdos_renyi_graph(num_nodes, avg_degree / num_nodes)

# Parámetros de la simulación
infection_prob = 0.2
recovery_prob = 0.1
num_iterations = 100

# Simular el modelo SIS
infected_nodes, inf_df = simulate_sis_model(
    graph, infection_prob, recovery_prob, num_iterations)

node_colors = [
    'red' if node in infected_nodes else 'blue' for node in graph.nodes()]

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 5))

# Definir la función de actualización para la animación


def update(frame):
    axes[0].clear()
    axes[1].clear()

    # Filtrar los datos hasta el timestamp actual
    data_filt = inf_df[inf_df['timestamp'] <= frame]

    # Obtener el número de infectados y susceptibles en el último timestamp
    last_row = data_filt.iloc[-1]
    num_infected = last_row['num_infected']
    num_susceptible = last_row['num_susceptible']

    # Actualizar los colores de los nodos en el grafo
    node_colors_updated = [
        'red' if i < num_infected else 'blue' for i in range(len(graph.nodes()))]

    # Dibujar el grafo sin cambiar su estructura, solo actualizando los colores de los nodos
    pos = nx.spring_layout(graph, pos=fixed_pos, k=1, fixed=fixed_nodes)
    nx.draw_networkx_nodes(
        graph, pos=pos, node_color=node_colors_updated, node_size=180, ax=axes[0])
    nx.draw_networkx_edges(graph, pos=pos, width=0.5,
                           alpha=0.5, edge_color='black', ax=axes[0])
    nx.draw_networkx_labels(graph, pos=pos, font_size=8,
                            font_color='black', ax=axes[0])

    # Graficar el lineplot de Seaborn
    sns.lineplot(x=data_filt['timestamp'],
                 y=data_filt['num_infected'], ax=axes[1], label='Infectados')
    sns.lineplot(x=data_filt['timestamp'],
                 y=data_filt['num_susceptible'], ax=axes[1], label='Susceptibles')

    # Configurar el título y las etiquetas de los ejes
    axes[1].set_title('Animación de valores en función del tiempo')
    axes[1].set_xlabel('Timestamp')
    axes[1].set_ylabel('Valor')


# Crear una posición inicial fija para los nodos del grafo
fixed_pos = nx.spring_layout(graph)
fixed_nodes = fixed_pos.keys()

# Crear la animación
animation = FuncAnimation(
    fig, update, frames=inf_df['timestamp'].max(), interval=100)


# Función de pausa
def pause_animation(event):
    if animation.running:
        animation.event_source.stop()

# Función de reinicio


def restart_animation(event):
    if not animation.running:
        animation.event_source.start()


# Asociar eventos de teclado
fig.canvas.mpl_connect('key_press_event', pause_animation)
fig.canvas.mpl_connect('key_release_event', restart_animation)

# Mostrar la animación
plt.show()
