from ParseDef import PDA_TRANSITIONS
import os

# --- Configuration ---
OUTPUT_FILENAME = "parse_graph.dot"

def generate_dot_file(transitions):
    """
    Generates the GraphViz DOT format string from the PDA transitions.

    Args:
        transitions (dict): The dictionary of (C_State, Input, S_Top) -> (N_State, S_Act, Action).

    Returns:
        str: The complete DOT language string.
    """
    
    # Start the DOT graph definition
    dot_lines = [
        "digraph PDA {",
        "\trankdir=LR; // Left to Right layout",
        "\tnode [shape=circle, style=filled, fillcolor=\"#E6F0FF\"];",
        "\tsubgraph cluster_key {",
        "\t\tlabel = \"State Legend\"; color=lightgrey;",
        "\t\tnode [shape=none, fillcolor=none];",
        "\t\tKey [label=\"Edge Label Format:\\nInput/Stack_Top \\u2192 Stack_Action / Action\"];",
        "\t}",
        
        "\t// Define special states",
        "\tq_accept [shape=doublecircle, fillcolor=\"#B2FFB2\"]; // Final Accept State",
        "\tinitial_node [shape=point];",
        "\tinitial_node -> q_start;", # Define the start state
        "\n\t// Transitions (Edges)",
    ]

    # Set of all states (nodes) found in the transitions
    all_states = set()

    for (c_state, input_token, stack_top), (n_state, stack_action, action_name) in transitions.items():
        all_states.add(c_state)
        all_states.add(n_state)

        # Create the edge label (Input / Stack_Top -> Stack_Action / Action_Name)
        # We use the unicode right arrow (->) in the label for readability.
        if action_name == 'A_NULL':
            label_parts = [
                f"{input_token}",
                f"Stack: {stack_top} \u2192 {stack_action}",
               ]
        else:
            label_parts = [
                f"{input_token}",
                f"Stack: {stack_top} \u2192 {stack_action}",
                f"Action: {action_name}"
            ]
            
        label = "\\n".join(label_parts) # Use \n for multi-line label inside DOT string

        # 2. Define the edge
        dot_lines.append(f"\t{c_state} -> {n_state} [label=\"{label}\", fontname=\"Monospace\"];")

    # Add state definitions (to ensure all nodes exist, even if they have no outgoing edges)
    dot_lines.append("\n\t// State Definitions (Nodes)")
    for state in sorted(list(all_states)):
        # Ensure we don't redefine the special nodes
        if state not in ['q_accept', 'initial_node']:
            dot_lines.append(f"\t{state};")
    
    dot_lines.append("}")
    return "\n".join(dot_lines)

def main():
    """
    Main function to generate and save the DOT file.
    """
    print("--- PDA Visualizer ---")
    
    # Generate the DOT content
    dot_content = generate_dot_file(PDA_TRANSITIONS)
    
    # Write to file
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write(dot_content)
        
        print(f"\n✅Successfully generated GraphViz DOT file: '{OUTPUT_FILENAME}'")
        print("-----------------------------------------------------------------")
        print("Next:")
        print("OR: If you have GraphViz installed locally, run:")
        print(f"> dot -Tpng {OUTPUT_FILENAME} -o pda_diagram.png")
        print("-----------------------------------------------------------------")
        
    except IOError as e:
        print(f"\n❌ ERROR: Could not write to file {OUTPUT_FILENAME}. {e}")

if __name__ == "__main__":
    main()
