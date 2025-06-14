import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import json

class ComponentFeatureImportanceCalculator:

    def __init__(self, json_file):
        self.agent_graph = self.load_graph_from_json(json_file)

    def load_graph_from_json(self, json_file):
        with open(json_file, 'r') as file:
            return json.load(file)

    def calculate_feature_importance_random_forest(self):
            """
            Calculate feature importance using Random Forest based on jailbreak success rates from graph data.
                
            Returns:
                dict: Feature importance results
            """
            # Initialize empty lists to store data
            data = []
            
            for node in self.agent_graph['nodes']:
                # Create a dictionary for this node's data
                node_data = {}
                
                # One-hot encode agents (0-3)
                for i in range(4):
                    node_data[f'agent_{i}'] = 1 if i == node['agent_index'] else 0

                # One-hot encode tools (0-2)
                for i in range(3):
                    node_data[f'tool_{i}'] = 1 if i in node['tool_in_input'] else 0
                
                # One-hot encode memories (0-6)
                for i in range(7):
                    node_data[f'memory_{i}'] = 1 if i in node['memory_in_input'] else 0
                
                # Add jailbreak success rate as output/label
                node_data['jailbreak_success_rate'] = node['jailbreak_success_rate']
                
                data.append(node_data)

            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Prepare features and target
            X = df.drop('jailbreak_success_rate', axis=1)
            y = df['jailbreak_success_rate']

            # Train Random Forest model
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X, y)

            # Get feature importance
            feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': rf_model.feature_importances_
            })
            feature_importance = feature_importance.sort_values('importance', ascending=False)
            
            # Convert to dictionary format for JSON serialization
            feature_importance_dict = {
                'feature_importance': feature_importance.to_dict('records')
            }
            
            self.feature_importance_dict = feature_importance_dict
            return self.feature_importance_dict
    
    def save_feature_importance_to_json(self, json_file):
        with open(json_file, 'w') as file:
            json.dump(self.feature_importance_dict, file)