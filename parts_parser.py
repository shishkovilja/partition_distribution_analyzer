import re
import pandas as pd


def load_parts(file_name):
    cache_groups_dict = {}
    table = []

    parts_file = open(file_name)

    table_header_str = None

    grp_id_idx = 0
    table_columns = []
    attrs_names = []

    for line in parts_file:
        if not table_header_str:
            match = re.match(r'\[(.+)', line)
        
            if match:
                table_header_str, = match.groups()
                table_columns = table_header_str.split(',')
                grp_id_idx = table_columns.index('groupId')
                table_columns[grp_id_idx] = 'groupName'

                attrs_idx = table_columns.index('nodeAddresses') + 1
                attrs_names = table_columns[attrs_idx:]

            continue
        
        if '[next group: ' in line:
            group_id, name = re.match(r'.+id=(.+), name=(.+)]', line).groups()
            cache_groups_dict[group_id] = name
        elif 'Control utility [' in line:
            break
        else:
            match = re.match(r'(.+),\[(.+)],(.+)', line)
            if match is not None:
                vals_str, address_str, attrs_str = match.groups()

                vals = vals_str.split(',')
                vals[grp_id_idx] = cache_groups_dict.get(vals[grp_id_idx], vals[grp_id_idx])

                row = vals
                row.append(address_str)
                row += attrs_str.split(',')

                table.append(row)

    parts_file.close()

    df = pd.DataFrame(table, columns=table_columns)

    excluded_groups_list = ['ignite-sys-cache']

    df = df[~df.groupName.isin(excluded_groups_list)]
    df = df[df.primary == 'P']
    df['partition'] = pd.to_numeric(df['partition'])
    df['updateCounter'] = pd.to_numeric(df['updateCounter'])
    df['partitionSize'] = pd.to_numeric(df['partitionSize'])
    
    return df, attrs_names
