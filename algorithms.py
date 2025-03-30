#   algorithms.py
#   Advanced Algorithms for AION System Enhancement

import numpy as np
import tensorflow as tf
from sklearn.cluster import KMeans
import networkx as nx
import heapq
import collections
from typing import List, Dict, Tuple, Any
import logging

#   --- Configuration ---
#   Adjust these parameters as needed
CNN_EPOCHS = 10
KMEANS_CLUSTERS = 5
PATH_WEIGHT = 'capacity'

#   --- Logging Setup ---
#   Ensure logging is configured (e.g., in AION.py)
#   If not, add basic setup here:
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#   --- AI-Powered Threat Analysis ---
def ai_threat_analysis(threat_data: Dict[str, Any]) -> Dict[str, List[float]]:
    """
    Analyzes threat data to predict and classify potential security risks.

    Args:
        threat_data: A dictionary containing threat indicators and labels.
                     Example: {'indicators': [[...], [...]], 'labels': [[...], [...]]}

    Returns:
        A dictionary containing CNN predictions, anomaly scores, and risk scores.
    """

    try:
        #   1. Input Validation
        if not isinstance(threat_data, dict) or 'indicators' not in threat_data or 'labels' not in threat_data:
            raise ValueError("Invalid threat data format.")
        indicators = np.array(threat_data['indicators'])
        labels = np.array(threat_data['labels'])
        if len(indicators) == 0 or len(indicators) != len(labels):
            raise ValueError("Inconsistent number of indicators and labels.")

        #   2. CNN Model
        cnn_model = tf.keras.models.Sequential([
            tf.keras.layers.Conv1D(32, 3, activation='relu', input_shape=(indicators.shape[1], 1)),
            tf.keras.layers.MaxPooling1D(2),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(labels.shape[1], activation='softmax')  #   Dynamically adjust output size
        ])
        cnn_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        cnn_data = indicators.reshape(indicators.shape[0], indicators.shape[1], 1)
        cnn_model.fit(cnn_data, labels, epochs=CNN_EPOCHS, verbose=0)  #   Reduced verbosity
        cnn_predictions = cnn_model.predict(cnn_data, verbose=0)

        #   3. Anomaly Detection
        kmeans = KMeans(n_clusters=KMEANS_CLUSTERS, random_state=0, n_init='auto')
        kmeans.fit(indicators)
        anomaly_scores = kmeans.transform(indicators).min(axis=1)

        #   4. Predictive Risk Scoring
        risk_scores = [cnn_predictions[i].max() * anomaly_scores[i] for i in range(len(indicators))]

        return {
            "cnn_predictions": cnn_predictions.tolist(),
            "anomaly_scores": anomaly_scores.tolist(),
            "risk_scores": risk_scores,
        }

    except Exception as e:
        logging.error(f"Threat analysis failed: {e}")
        return {"error": str(e)}  #   Return error details

#   --- Network Optimization ---
def optimize_network_flow(network_data: Dict[str, Any]) -> List[str]:
    """
    Optimizes network traffic flow to minimize congestion and latency.

    Args:
        network_data: A dictionary representing the network topology.
                      Example: {'edges': [...], 'source': 'A', 'target': 'C'}

    Returns:
        An optimized routing path (list of nodes), or an empty list on failure.
    """
    try:
        if not isinstance(network_data, dict) or 'edges' not in network_data or 'source' not in network_data or 'target' not in network_data:
            raise ValueError("Invalid network data format.")

        graph = nx.Graph()
        for edge in network_data['edges']:
            graph.add_edge(edge['from'], edge['to'], capacity=edge['capacity'])

        source = network_data['source']
        target = network_data['target']
        optimized_path = nx.shortest_path(graph, source=source, target=target, weight=PATH_WEIGHT)
        return optimized_path

    except nx.NetworkXNoPath:
        logging.warning(f"No path found between {network_data['source']} and {network_data['target']}.")
        return []
    except Exception as e:
        logging.error(f"Network optimization failed: {e}")
        return []

#   --- Automated Resource Allocation ---
def allocate_resources(resource_demands: Dict[str, Dict[str, float]], resource_capacities: Dict[str, float]) -> Dict[str, Dict[str, float]]:
    """
    Allocates system resources (CPU, Memory, Disk) based on demands and capacities.
    Implements a greedy allocation strategy.

    Args:
        resource_demands: A dictionary of resource demands per process.
                         Example: {'process1': {'CPU': 10, 'Memory': 20, 'Disk': 5}, ...}
        resource_capacities: A dictionary of available resource capacities.
                           Example: {'CPU': 15, 'Memory': 25, 'Disk': 15}

    Returns:
        A dictionary of resource allocations per process.
        Returns an empty dictionary on failure.

    Raises:
        ValueError: If the input data format is invalid.
    """
    if not isinstance(resource_demands, dict) or not isinstance(resource_capacities, dict):
        raise ValueError("Invalid resource data format.")

    allocations: Dict[str, Dict[str, float]] = {}  #   Initialize with type hint
    for process, demand in resource_demands.items():
        available_resources = sorted(resource_capacities.items(), key=lambda item: item[0])  #   Sort by resource name
        allocated: Dict[str, float] = {}  #   Initialize allocation for this process
        remaining_demand = sum(demand.values())  #   Total demand for the process

        for resource, capacity in available_resources:
            allocate = min(remaining_demand, min(demand.get(resource, 0.0), capacity))  #   Allocate what's available and needed
            if allocate > 0:
                allocated[resource] = allocate
                resource_capacities[resource] -= allocate
                remaining_demand -= allocate
            if remaining_demand <= 0:
                break  #   No more demand for this process

        allocations[process] = allocated
        #   Restore capacities for the next process
        for resource, allocated_amount in allocated.items():
            resource_capacities[resource] += allocated_amount

    return allocations

#   --- Sample Data and Usage ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')  #   Basic logging setup

    #   Sample Threat Data
    THREAT_CLASSES = ['malware', 'intrusion', 'ddos', 'phishing']
    threat_data = {
        'indicators': [
            [0.8, 0.2, 0.5, 0.9],  #   Example: Network traffic, CPU load, etc.
            [0.1, 0.9, 0.2, 0.3],
            [0.6, 0.4, 0.7, 0.5],
            [0.2, 0.7, 0.3, 0.8],  #   Added more data points
            [0.9, 0.1, 0.8, 0.1],
        ],
        'labels': [
            [1, 0, 0, 0],  #   One-hot encoded: malware
            [0, 1, 0, 0],  #   intrusion
            [0, 0, 1, 0],  #   ddos
            [0, 0, 0, 1],  #   phishing
            [1, 0, 0, 0],
        ]
    }
    try:
        threat_analysis_results = ai_threat_analysis(threat_data)
        print("Threat Analysis:", threat_analysis_results)
    except Exception as e:
        print(f"Error in threat analysis: {e}")

    #   Sample Network Data
    network_data = {
        'edges': [
            {'from': 'A', 'to': 'B', 'capacity': 10},
            {'from': 'B', 'to': 'C', 'capacity': 5},
            {'from': 'A', 'to': 'D', 'capacity': 7},
            {'from': 'D', 'to': 'C', 'capacity': 12},
            {'from': 'A', 'to': 'E', 'capacity': 8},  #   Added more edges
            {'from': 'E', 'to': 'C', 'capacity': 9},
        ],
        'source': 'A',
        'target': 'C',
    }
    try:
        optimized_path = optimize_network_flow(network_data)
        print("Optimized Path:", optimized_path)
    except Exception as e:
        print(f"Error in network optimization: {e}")

    #   Sample Resource Data
    resource_demands = {
        'process1': {'CPU': 10, 'Memory': 20, 'Disk': 5},
        'process2': {'CPU': 5, 'Memory': 10, 'Disk': 10},
        'process3': {'CPU': 8, 'Memory': 15, 'Disk': 7},  #   Added more processes
    }
    resource_capacities = {
        'CPU': 20,  #   Increased capacity
        'Memory': 30,
        'Disk': 20,
    }
    try:
        allocations = allocate_resources(resource_demands, resource_capacities)
        print("Resource Allocations:", allocations)
    except Exception as e:
        print(f"Error in resource allocation: {e}")
