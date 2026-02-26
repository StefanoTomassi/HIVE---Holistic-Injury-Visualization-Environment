def get_strain(dr, p, shells):
    """
    
    
    """
    import lsreader as lr
    import numpy as np

    strain_data = dr.get_data(lr.DataType.D3P_SHELL_EFFECTIVE_PLASTIC_STRAIN, ist=p.ist, ipt=p.ipt, ipart_user = p.ipart_user) 
    strain_data = np.array(strain_data)
    return strain_data