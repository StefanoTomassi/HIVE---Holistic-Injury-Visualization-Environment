def get_strain(dr, p):
    """
    
    
    """
    import lsreader as lr
    import numpy as np

    strain_data = dr.get_data(lr.DataType.D3P_SHELL_EFFECTIVE_PLASTIC_STRAIN, ist=p.ist, ipt=p.ipt, ipart_user = p.ipart_user) 
    strain_data = np.array(strain_data)
    return strain_data

def get_selected_part(desired_parts: str, part_dict: dict) -> list:
    part_to_analyze = []
    for key, value in part_dict.items():
        if desired_parts in value:
            part_to_analyze.append(value)
    return part_to_analyze

def compute_max_strain(strain, max_strain):
    max_strain = np.maximum(max_strain, strain)
    return max_strain

def get_segment_from_label(joint_label):
    # simple: use C2C5 if C2C3/C3C4/C4C5, use C5T1 if C5C6/C6C7/C7T1
    seg = "C2C5" if "C1C2" in joint_label or "C2C3" in joint_label or "C3C4" in joint_label or "C4C5" in joint_label else "C5T1"
    return seg

def boxplot_strain(max_strain, selected_components):
    plt.figure(figsize=figsize)
    keys = list(max_strain.keys())
    values = [max_strain[k][0]*100 for k in keys]
    for i, label in enumerate(keys):
    # parse label: "N_L_C1C2-ALL" -> joint="C1C2", comp="ALL"
        if "-" not in label:
            continue
        joint_part, comp_part = label.split("-")   # e.g. "N_L_C1C2", "ALL"
        # optional: extract joint like "C1C2" (if you want to double‑check)
        joint = joint_part.split("_")[-1]          # e.g. "C1C2"

        # which joint segment to use (C2C5 vs C5T1) based on your rule
        seg = get_segment_from_label(joint)
    # build key for strain_limits
        limit_key = f"{comp_part}_strain_limits_{seg}"
        if limit_key in strain_limits:
            lower, mean, upper = strain_limits[limit_key]
            x_center = i + 1
            # short horizontal lines inside the box
            plt.hlines(
                [lower, mean, upper],
                xmin=x_center - 0.4,
                xmax=x_center + 0.4,
                colors="red",
                linestyles=["--", "-", "--"],
                linewidths=[1, 1.5, 1],
                alpha=0.8
            )
    keys = [k[4:-3] for k in keys ]
        
    plt.boxplot(values, labels=keys, vert=True, patch_artist=True,
                boxprops=dict(facecolor='lightblue', alpha=0.7),
                medianprops=dict(color='black'),
                whiskerprops=dict(linestyle='--'),showfliers=False)
    plt.ylabel('Strain values [%]')
    plt.title(f"Strain values for {selected_components} at 0° rotated seat")
    plt.grid(True, axis='y', alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout(pad=2.0)  # Più padding verticale
    plt.grid(True, axis='y', alpha=0.3, linestyle=':')
    plt.subplots_adjust(left=0.2, right=0.95, top=0.86, bottom=0.2)
    plt.savefig('A015_strain_for_'+selected_components)