from calculate_component_feature_importance import ComponentFeatureImportanceCalculator

def main():
    calculator = ComponentFeatureImportanceCalculator('./data/output/detailed_graph_with_jb.json')
    # print(calculator.agent_graph["nodes"][0])
    calculator.calculate_feature_importance_random_forest()
    print(calculator.feature_importance_dict)
    calculator.save_feature_importance_to_json('./data/output/component_feature_importance.json')

if __name__ == "__main__":
    main()