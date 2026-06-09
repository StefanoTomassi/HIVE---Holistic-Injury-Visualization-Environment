import numpy as np
from Strain_limits_and_ROM import ROM_labels, Spine_labels
import matplotlib as mpl
import core.io.create_objects as create_objects 
import matplotlib.pyplot as plt

def get_IV_NIC(theta_dynamic, theta_physiological) -> np.ndarray:
    """
    Calculate the Injury Criterion (IV_NIC) based on the dynamic and physiological angles.

    Parameters:
    theta_dynamic (np.ndarray): Instant angle value during the motion of the spine segment.
    theta_physiological (np.ndarray): array containing in first place the extension physiological angle and in second place the flexion physiological angle.

    Returns:
    np.ndarray: Calculated IV_NIC values.
    """
    # Ensure that the input arrays are numpy arrays
    theta_dynamic = np.array(theta_dynamic)
    theta_physiological = np.array(theta_physiological)
    theta_dynamic = np.asarray(theta_dynamic)
    delta = theta_dynamic - theta_dynamic[0]   # spostamento dalla posizione neutra

    IV_NIC = np.where(
    delta >= 0,
    delta / theta_physiological[1],
    delta / theta_physiological[0]
)

    return IV_NIC

def get_dynamic_theta(upx, upy, lowx, lowy) -> np.ndarray:
    """
    Calculate the dynamic angle (theta_dynamic) based on the static angle (theta_static), angular velocity (theta_dot), and time.

    Parameters:
    theta_static (float): The static angle value.
    theta_dot (float): The angular velocity.
    time (float): The time at which to calculate the dynamic angle.

    Returns:
    float: Calculated dynamic angle (theta_dynamic).
    """    
    dx = upx - lowx
    dy = upy - lowy
    theta_dynamic = np.arctan2(dx, dy)
    return theta_dynamic

def get_SA_nodes(node_dict: dict, criteria: str, coordinates: np.array, ids: np.array) -> dict:
    """
    Extracts relevant nodes from the node dictionary based on a list of relevant node names.

    Parameters:
    node_dict (dict): A dictionary mapping node names to their IDs.
    relevant_node_names (list): A list of node names that are relevant for the analysis.

    Returns:
    dict: A dictionary containing only the relevant nodes and their corresponding IDs.
    """
    SA_nodes = {k: v for k, v in node_dict.items() if criteria in k}
    mask = np.isin(ids, list(int(v) for v in SA_nodes.values()))
    SA_coordinates = coordinates[:, mask]
    return SA_nodes, SA_coordinates

def plot_kinematic(x_coordinates, z_coordinates, IV_NIC, ROM_label):
    """
    Plot the kinematic data of x and z coordinates over time.

    Parameters:
    x_coordinates (np.ndarray): Array of x coordinates for the nodes.
    z_coordinates (np.ndarray): Array of z coordinates for the nodes.
    time (np.ndarray): Array of time values corresponding to the coordinates.

    Returns:
    None: Displays a plot of the kinematic data.
    """
    x_max = x_coordinates[np.argmax(IV_NIC)]
    z_max = z_coordinates[np.argmax(IV_NIC)]

    plt.figure(figsize=figsize)
    plt.xlabel('x [mm]', fontdict={'fontsize': 11, 'family': 'calibri'})
    plt.ylabel('z [mm]', fontdict={'fontsize': 11, 'family': 'calibri'})
    plt.title('Spine curvature', fontdict={'fontsize': 11, 'family': 'calibri'})

    # Fixed limits (30 mm x, 100 mm y spans → aspect handles scaling)
    #plt.xlim(-280, -180)
    #plt.ylim(450, 550)
    
    for i, (x, z) in enumerate(zip(x_max[1:], z_max[1:])):
        plt.plot(x, z, 'ro')                          # punto rosso
        plt.text(x + 5, z, Spine_labels[i], fontsize=6,      # etichetta sopra il punto
             ha='left', va='bottom')
    #x_min, x_max_plot = plt.xlim()
    y_min, y_max = plt.ylim()

    # posizione nel corner basso‑sinistro dei dati
    #x_text = x_min + 0.05 * (x_max_plot - x_min) - 125
    y_text = y_min + 0.05 * (y_max - y_min)

    plt.text(-250, y_text, ROM_label + ' out of ROM', color= c40,
         fontsize=11,
         ha='left',   # horizontal alignment: sinistra
         va='bottom') # vertical alignment: in basso
    #plt.axis('equal')
    plt.axis('square')

    plt.plot(x_max[1:], z_max[1:], 'r-', linewidth=1, alpha=0.7)
    file = 'A010_'+ROM_label+'_kinematic'
    plt.savefig(file)

def plot_IV_NIC(time, IV_NIC, ROM, ROM_label):
    plt.figure(figsize=figsize)
    plt.plot(time, IV_NIC, label='IV-NIC'+str(ROM), color=c33)
    plt.xlabel('Time [ms]',fontdict={'fontsize': 11, 'family': 'calibri'})
    plt.ylabel('IV-NIC',fontdict={'fontsize': 11, 'family': 'calibri'})
    plt.title('IV-NIC for '+str(ROM_label),fontdict={'fontsize': 11, 'family': 'calibri'})
    plt.ylim([-1.5, 1.5])
    plt.xlim([time[0]-1, time[-1]+1])
    plt.axhline(y=-1, color='red', linestyle='--', linewidth=1)
    plt.axhline(y=1,  color='red', linestyle='--', linewidth=1)
    plt.fill_between([time[0]-50, time[-1]+50], 1, 1.5, color='red', alpha=0.2)
    plt.fill_between([time[0]-50, time[-1]+50], -1.5, -1, color='red', alpha=0.2) 
    file = 'A010_'+ROM_label+'_IV_NIC'
    plt.savefig(file)
    